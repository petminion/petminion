
import json
import logging
import os
import tempfile
import time as systime  # prevent name clash with datetime.time
from datetime import datetime, time
from typing import NamedTuple

import cv2

from .ImageRecognizer import \
    ImageDetection  # noqa: F401 needed for find at runtime
from .RateLimit import RateLimit
from .util import load_state, save_state, user_data_dir

logger = logging.getLogger()


class FeedingNotAllowed(Exception):
    """Raised by do_feeding() when a feeding can not be permitted now"""
    pass


save_name = "rule-v2"


class State():
    """A class representing the serializable state of a TrainingRule"""

    def __init__(self):
        self.fed_today = 0  # how many feedings have we done so far today
        self.last_time = datetime.now().time()  # the last time our rule was run


class TrainingRule:
    """A class representing a training rule for the pet minion"""

    def __init__(self, trainer):
        """The normal constructor when created by the Trainer"""
        self.trainer = trainer
        self.state = State()
        self.feed_interval_limit = RateLimit("feed_limit", 10 * 60)  # 10 minutes
        self.failure_capture_limit = RateLimit("failure_capture_limit", 4 * 60 * 60)  # 4 hour
        self.live_capture_limit = RateLimit("live_capture_limit", 5)  # every few seconds

    @staticmethod
    def create_from_save(trainer, desired_class) -> 'TrainingRule':
        """Try to recreate a pickled/saved TrainingRule from our saved state file, return None if not possible"""

        r = desired_class(trainer)  # create a default instance
        try:
            r.state = load_state(save_name)
        except Exception as e:
            logger.warning(
                f'No saved training state ({e}) found, using default state...')
        return r

    def do_feeding(self, num_feedings: int = 1) -> None:
        """Do a feeding
        Use a cooldown to not allow feedings to close to each other.
        """
        # FIXME - we should also store success images occasionally (but not to frequently) when target is seen but feeding not currently allowed
        self.save_image(is_success=True, store_annotated=True)

        self.trainer.feeder.feed(num_feedings)
        self.state.fed_today += num_feedings

        # wait a few seconds after food dispensed to see if we can store a photo of the target eating
        if not self.trainer.is_simulated:
            # don't sleep if running in the sim (to be developer friendly)
            systime.sleep(60)
        self.trainer.capture_image()
        self.save_image(is_success=False, summary="eating")
        self.trainer.share_social("Fed my cat")

        save_state(save_name, self.state)  # save to disk so we don't miss feedings if we restart

    def run_once(self):
        """Do idle processing for this rule - mostly by calling evaluate_scene()"""

        # check for crossing midnight
        now = datetime.now()  # time + date
        now_time = now.time()  # time of day
        old_time = self.state.last_time
        self.state.last_time = now_time
        if now_time < old_time:
            # We crossed midnight since last run
            logger.debug(f'Did { self.state.fed_today } feedings yesterday')
            self.state.fed_today = 0
            save_state(save_name, self.state)  # make sure to update the serialized state

        if not self.evaluate_scene():
            # We 'failed' on this camera frame.  The vast majority of frames will be failures
            # but it is useful to save a few of them for future training purposes - let's do one every four hours?
            if self.failure_capture_limit.can_run():
                self.save_image(is_success=False)

        if self.live_capture_limit.can_run():  # keep a live image every few seconds
            filepath = os.path.join(
                tempfile.gettempdir(), "petminion_live.png")
            self.store_annotated(filepath)

    def evaluate_scene(self) -> bool:
        """Evaluate the current scene

        Raises:
            NotImplementedError: Subclasses must implement

        Returns:
            bool: return true if we considered it 'successful'
        """
        raise NotImplementedError

    # FIXME add thresholds for 'aggressive' or 'conservative' matching
    # FIXME add a bounding box for region to watch (so we only detect tokens that are in the bowl)
    def count_detections(self, name: str):
        detections = self.trainer.image.detections

        return list(map(lambda x: x.name, detections)).count(name)

    def is_detected(self, name: str):
        return self.count_detections(name) > 0

    def store_annotated(self, filepath):
        """Store the current annotated frame in a file"""
        cv2.imwrite(filepath, self.trainer.image.annotated)

    def save_image(self, is_success: bool, summary: str = None, details: str = None, store_annotated: bool = False):
        """Save the current image
        Useful for future model training, or simulated camera input or social media purposes. The image is stored in
        filename.png, metadata stored in filename.json. 

        filename will be (success|failure)-localtime-summary 

        Args:
            is_success (bool): If true this image is 'successful' and will be marked that way in the name
            summary (str, optional): A short string which replaces the default 'success' or 'failure' prefixes. Defaults to None.
            details (str, optional): If provided this long string will be stored in filename.json. Defaults to None.
            store_annotated (bool, optional): If true, also store the annotated image in filename-annotated.png.
        """
        now = datetime.now()
        prefix = summary if summary else (
            "success" if is_success else "failure")
        filename = f'{ prefix }-{now:%Y%m%d_%H%M%S}'
        image_dir = os.path.join(
            user_data_dir(), self.__class__.__name__, "captures")
        os.makedirs(image_dir, exist_ok=True)

        # Write the raw image
        img_name = os.path.join(
            image_dir, f"{filename}.png")
        logger.debug(f'Storing image to {img_name}')
        cv2.imwrite(img_name, self.trainer.image.image)

        # store annotated image if any detections were found
        if store_annotated and self.trainer.image.detections:
            self.store_annotated(os.path.join(
                image_dir, f"{filename}-annotated.png"))

        # write metadata
        data = {
            "classifications": self.trainer.image.classifications,
            "detections": self.trainer.image.detections
        }
        if summary:
            data['summary'] = summary
        if details:
            data['details'] = details
        with open(os.path.join(
                image_dir, f"{filename}.json"), "w") as f:
            json.dump(data, f, indent=2)


class ScheduledFeeding(NamedTuple):
    """A scheduled feeding event for a particular time of day

    Args:
        NamedTuple (_type_): _description_
    """
    when: datetime.time
    num_feedings: int


class ScheduledFeederRule(TrainingRule):
    """
    A class representing a rule for scheduled feeding.

    Attributes:
        trainer (Trainer): The trainer object associated with the rule.
        schedule (list): A list of ScheduledFeeding objects representing the feeding schedule.
    """

    def __init__(self, trainer):
        super().__init__(trainer)

        # FIXME - pull schedule from some sort of json file?
        self.schedule = load_state("schedule", [ScheduledFeeding(time(7, 00), 2),
                                                ScheduledFeeding(time(14, 00), 1),
                                                ScheduledFeeding(time(16, 00), 1),
                                                ScheduledFeeding(time(17, 45), 2)])

    @property
    def num_allowed(self):
        """
        Check if feeding is allowed based on the current time and feeding schedule.

        Returns:
            bool: True if feeding is allowed, False otherwise.
        """
        # find all previously allowed feedings for today
        now = datetime.now()

        n = 0
        for f in self.schedule:
            if now.time() >= f.when:
                n += f.num_feedings

        if n <= self.state.fed_today:
            logger.debug(
                f'Feeding not allowed. Already fed { self.state.fed_today } out of { n } feedings')
            return 0

        return n - self.state.fed_today


class SimpleFeederRule(ScheduledFeederRule):
    """
    A rule that allows feeding when a specific target is detected.

    Args:
        trainer (Trainer): The trainer object.
        target (str): The target to detect.

    Attributes:
        target (str): The target to detect.

    Methods:
        evaluate_scene: Evaluates the scene and performs feeding if the target is detected and feeding is allowed.
    """

    def __init__(self, trainer, target="cat"):
        super().__init__(trainer)

        self.target = target

    def evaluate_scene(self) -> bool:
        """
        Evaluates the scene and performs feeding if the target is detected and feeding is allowed.

        Returns:
            bool: True if the target is detected, False otherwise.
        """
        if self.is_detected(self.target):
            num_allowed = self.num_allowed

            if num_allowed:
                if not self.feed_interval_limit.can_run():
                    logger.warning(f'Too soon for this { num_allowed } feedings, try again later')
                else:

                    to_feed = 1  # assume one feeding
                    if self.feed_interval_limit.interval_secs == 0.0:
                        # There is no minimum interval, therefore we should just feed all eligible feedings now
                        to_feed = num_allowed

                    logger.debug(
                        f'A { to_feed } feeding is allowed and we just saw a { self.target }')

                    self.do_feeding(to_feed)

                    # claim success because we just saw the target (even though we weren't allowed to feed)
                    return True

        return False


class CatTrainingRule0(TrainingRule):
    """
    Rule for training a cat.

    This rule checks if a new token has appeared and if the cat is detected. If both conditions are met,
    it performs a feeding. If a token is removed from the target, it logs a warning and saves an image.

    Attributes:
        trainer (Trainer): The trainer object associated with this rule.
        old_count (int): The previous count of detections.

    Methods:
        evaluate_scene: Evaluates the scene and performs the necessary actions based on the conditions.

    """

    def __init__(self, trainer):
        """
        Initializes a new instance of the TrainingRule class.

        Args:
            trainer: The trainer object.

        """
        super().__init__(trainer)
        self.state.old_count = 0

    def evaluate_scene(self) -> bool:
        """
        Evaluates the scene and determines if a feeding should be performed based on the detected objects.

        Returns:
            bool: True if a feeding is performed, False otherwise.
        """
        count = self.count_detections("spring")
        # self.since_success > 60 * 5 FIXME place a limit on repeated feedings in a short time?

        # A new token appeared?
        if count > self.state.old_count and self.is_detected("cat"):
            self.do_feeding()
            self.state.old_count = count
            return True

        # someone took away a token (cat kicked it out of camera) - FIXME use a more conservative match for this test?
        if count < self.state.old_count:
            logger.warning(
                'Token removed from target (cat is cheating? FIXME)')
            self.state.old_count = count
            self.save_image(is_success=False, summary="cheating")

        return False
