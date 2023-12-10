
from .ImageRecognizer import ImageDetection
from .util import user_data_dir
from typing import NamedTuple
from datetime import time, datetime, timedelta
import os
import cv2
import json
import logging
logger = logging.getLogger()


class FeedingNotAllowed(Exception):
    """Raised by do_feeding() when a feeding can not be permitted now"""
    pass


class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer
        self.fed_today = 0  # how many feedings have we done so far today
        self.last_time = datetime.now().time()
        self.last_feed_datetime = None
        self.last_failure_datetime = None
        self.min_feed_interval = timedelta(minutes=10)
        self.failure_capture_interval = timedelta(hours=4)

    def do_feeding(self):
        """Do a feeding
        Use a cooldown to not allow feedings to close to each other.
        """
        self.save_image(is_success=True, store_annotated=True)

        now = datetime.now()
        if self.last_feed_datetime and now < self.last_feed_datetime + self.min_feed_interval:
            # raise FeedingNotAllowed(f'Too soon for this feeding, try again at { self.last_feed_time + self.min_feed_interval }')
            logger.warning(
                f'Too soon for this feeding, try again at { self.last_feed_datetime + self.min_feed_interval }')
        else:
            self.trainer.feeder.feed()
            self.fed_today += 1
            self.last_feed_datetime = now

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
            if not self.last_failure_datetime or now >= self.last_failure_datetime + self.failure_capture_interval:
                self.last_failure_datetime = now
                self.save_image(is_success=False)

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

    def save_image(self, is_success: bool, summary: str = None, details: str = None, store_annotated: bool = False):
        """Save the current image
        Useful for future model training, or simulated camera input or social media purposes. The image is stored in
        filename.png, metadata stored in filename.json. 

        filename will be (success|failure)-localtime-summary 

        Args:
            is_success (bool): If true this image is 'successful' and will be marked that way in the name
            summary (str, optional): A short string which is added to the filename. Defaults to None.
            details (str, optional): If provided this long string will be stored in filename.json. Defaults to None.
            store_annotated (bool, optional): If true, also store the annotated image in filename-annotated.png.
        """
        now = datetime.now()
        filename = f'{ "success" if is_success else "failure" }-{now:%Y%m%d_%H%M%S}{ ("-" + summary) if summary else "" }'
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
            cv2.imwrite(os.path.join(
                image_dir, f"{filename}-annotated.png"), self.trainer.image.annotated)

        # write metadata
        data = {
            "classifications": self.trainer.image.classifications,
            "detections": self.trainer.image.detections
        }
        if summary:
            data.summary = summary
        if details:
            data.details = details
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
        self.schedule = [ScheduledFeeding(time(7, 20), 3),
                         ScheduledFeeding(time(14, 00), 1),
                         ScheduledFeeding(time(16, 00), 1)]

    def is_feeding_allowed(self):
        # find all previously allowed feedings for today
        now = datetime.now().time()

        num_allowed = 0
        for f in self.schedule:
            if now >= f.when:
                num_allowed += f.num_feedings

        logger.debug(
            f'Already fed { self.fed_today } out of { num_allowed } feedings')
        return num_allowed > self.fed_today


class SimpleFeederRule(ScheduledFeederRule):
    def __init__(self, trainer, target="cat"):
        super().__init__(trainer)

        self.target = target

    def evaluate_scene(self) -> bool:
        if self.is_feeding_allowed() and self.is_detected(self.target):
            logger.debug(
                f'A feeding is allowed and we just saw a { self.target }')
            self.do_feeding()
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
