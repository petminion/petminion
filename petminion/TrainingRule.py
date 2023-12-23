
from .ImageRecognizer import ImageDetection
from .util import user_state_dir, user_data_dir
from typing import NamedTuple
from datetime import time, datetime, timedelta
import os
import cv2
import json
import logging
import tempfile
import jsonpickle
import time as systime  # prevent name clash with datetime.time
logger = logging.getLogger()


class FeedingNotAllowed(Exception):
    """Raised by do_feeding() when a feeding can not be permitted now"""
    pass


save_name = os.path.join(user_state_dir(), "rule_state.json")


class TrainingRule:

    def __init__(self, trainer):
        """The normal constructor when created by the Trainer"""
        self.trainer = trainer
        self.fed_today = 0  # how many feedings have we done so far today
        self.last_time = datetime.now().time()
        self.last_feed_datetime = None
        self.last_failure_datetime = None
        self.last_live_frame = None

        # Note, we have to use seconds for these intervals because timedelta is not properly serialized by jsonpickle
        self.min_feed_interval = timedelta(minutes=10).total_seconds()
        self.failure_capture_interval = timedelta(hours=4).total_seconds()
        self.live_frame_capture_interval = timedelta(seconds=2).total_seconds()

    @staticmethod
    def create_from_save(trainer, desired_class):
        """Try to recreate a pickled/saved TrainingRule from our saved state file, return None if not possible"""
        try:
            logger.info(f'Restoring training state from {save_name}')
            with open(save_name, "r") as f:
                json = f.read()
                r = jsonpickle.decode(json)
                r.trainer = trainer  # restore unsaved field
                return r
        except Exception as e:
            logger.warning(
                f'No saved training state ({e}) found, using default state...')
            return desired_class(trainer)  # create a default instance

    def save_state(self):
        """Serialize this object to the filesystem so it can be restore_state later..."""
        # FIXME - move out of this class into a general utility pickling class

        logger.debug(f'Saving state to {save_name}')
        # unpicklable=False, doesn't work well - we loose too much type info
        json = jsonpickle.encode(self,  indent=2)
        with open(save_name, "w") as f:
            f.write(json)

    def __getstate__(self):
        """Used by jsonpickle to get the object used for serialization
        """
        # per https://stackoverflow.com/questions/18147435/how-to-exclude-specific-fields-on-serialization-with-jsonpickle
        state = self.__dict__.copy()
        del state['trainer']  # We do not want this serialized
        return state

    def __setstate__(self, state):
        """Used by jsonpickle to unpickle from a saved state object"""
        self.__dict__.update(state)

    def do_feeding(self):
        """Do a feeding
        Use a cooldown to not allow feedings to close to each other.
        """
        now = datetime.now()
        # if self.last_feed_datetime and now < self.last_feed_datetime + timedelta(seconds=self.min_feed_interval):
        # raise FeedingNotAllowed(f'Too soon for this feeding, try again at { self.last_feed_time + self.min_feed_interval }')
        # logger.warning(f'Too soon for this feeding, try again at { self.last_feed_datetime + timedelta(seconds=self.min_feed_interval) }')

        # FIXME - we should also store success images occasionally (but not to frequently) when target is seen but feeding not currently allowed
        self.save_image(is_success=True, store_annotated=True)

        self.trainer.feeder.feed()
        self.fed_today += 1
        self.last_feed_datetime = now

        # wait a few seconds after food dispensed to see if we can store a photo of the target eating
        if not self.trainer.is_simulated:
            # don't sleep if running in the sim (to be developer friendly)
            systime.sleep(60)
        self.trainer.capture_image()
        self.save_image(is_success=False, summary="eating")
        self.trainer.share_social("Fed my cat")

        self.save_state()  # save to disk so we don't miss feedings if we restart

    def run_once(self):
        """Do idle processing for this rule - mostly by calling evaluate_scene()"""

        now = datetime.now()  # time + date
        now_time = now.time()  # time of day
        if now_time < self.last_time:
            # We crossed midnight since last run
            logger.debug(f'Did { self.fed_today } feedings yesterday')
            self.fed_today = 0
        self.last_time = now_time

        if not self.evaluate_scene():
            # We 'failed' on this camera frame.  The vast majority of frames will be failures
            # but it is useful to save a few of them for future training purposes - let's do one every four hours?
            if not self.last_failure_datetime or now >= self.last_failure_datetime + timedelta(seconds=self.failure_capture_interval):
                self.last_failure_datetime = now
                self.save_image(is_success=False)

        if not self.last_live_frame or now >= self.last_live_frame + timedelta(seconds=self.live_frame_capture_interval):
            self.last_live_frame = now
            filepath = os.path.join(tempfile.gettempdir(), "minion_live.png")
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
    def __init__(self, trainer):
        super().__init__(trainer)

        # FIXME - pull schedule from some sort of json file?
        self.schedule = [ScheduledFeeding(time(7, 00), 3),
                         ScheduledFeeding(time(14, 00), 1),
                         ScheduledFeeding(time(16, 00), 1),
                         ScheduledFeeding(time(17, 45), 2)]

    def is_feeding_allowed(self):
        # find all previously allowed feedings for today
        now = datetime.now()

        num_allowed = 0
        for f in self.schedule:
            if now.time() >= f.when:
                num_allowed += f.num_feedings

        if num_allowed <= self.fed_today:
            logger.debug(
                f'Feeding not allowed. Already fed { self.fed_today } out of { num_allowed } feedings')
            return False

        if self.last_feed_datetime and now < self.last_feed_datetime + timedelta(seconds=self.min_feed_interval):
            logger.warning(
                f'Too soon for this feeding, try again at { self.last_feed_datetime + timedelta(seconds=self.min_feed_interval) }')
            return False

        return True


class SimpleFeederRule(ScheduledFeederRule):
    def __init__(self, trainer, target="cat"):
        super().__init__(trainer)

        self.target = target

    def evaluate_scene(self) -> bool:
        if self.is_detected(self.target):
            if self.is_feeding_allowed():
                logger.debug(
                    f'A feeding is allowed and we just saw a { self.target }')
                self.do_feeding()

            # claim success because we just saw the target (even though we weren't allowed to feed)
            return True

        return False


class CatTrainingRule0(TrainingRule):
    def __init__(self, trainer):
        super().__init__(trainer)
        self.old_count = 0

    def evaluate_scene(self) -> bool:
        count = self.count_detections("spring")
        # self.since_success > 60 * 5 FIXME place a limit on repeated feedings in a short time?

        # A new token appeared?
        if count > self.old_count and self.is_detected("cat"):
            self.do_feeding()
            self.old_count = count
            return True

        # someone took away a token (cat kicked it out of camera) - FIXME use a more conservative match for this test?
        if count < self.old_count:
            logger.warning(
                'Token removed from target (cat is cheating? FIXME)')
            self.old_count = count
            self.save_image(is_success=False, summary="cheating")

        return False
