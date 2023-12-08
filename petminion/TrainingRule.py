
from .ImageRecognizer import ImageDetection
from typing import NamedTuple
from datetime import time, datetime
import logging
logger = logging.getLogger()


class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer
        self.fed_today = 0  # how many feedings have we done so far today

    def do_feeding(self):
        self.trainer.feeder.feed()
        self.fed_today += 1
        # FIXME reset this count at midnight
        # FIXME add a cooldown to not allow feedings to close to each other

    def evaluate_scene(self):
        raise NotImplementedError

    # FIXME add thresholds for 'aggressive' or 'conservative' matching
    # FIXME add a bounding box for region to watch (so we only detect tokens that are in the bowl)
    def count_detections(self, name):
        detections = self.trainer.image.detections

        return list(map(lambda x: x.name, detections)).count(name)

    def is_detected(self, name):
        return self.count_detections(name) > 0


class ScheduledFeeding(NamedTuple):
    """A scheduled feeding event for a particular time of day

    Args:
        NamedTuple (_type_): _description_
    """
    when: datetime.time
    num_feedings: int


class CatFeederRule(TrainingRule):
    def __init__(self, trainer):
        super().__init__(trainer)

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

        return num_allowed > self.fed_today

    def evaluate_scene(self):
        if self.is_feeding_allowed() and self.is_detected("cat"):
            self.do_feeding()


class CatTrainingRule0(TrainingRule):
    def __init__(self, trainer):
        super().__init__(trainer)
        self.old_count = 0

    def evaluate_scene(self):
        count = self.count_detections("spring")
        # self.since_success > 60 * 5 FIXME place a limit on repeated feedings in a short time?

        # A new token appeared?
        if count > self.old_count and self.is_detected("cat"):
            self.do_feeding()
            self.old_count = count
        # someone took away a token (cat kicked it out of camera) - FIXME use a more conservative match for this test?
        elif count < self.old_count:
            logger.warning(
                'Token removed from target (cat is cheating? FIXME)')
            self.old_count = count
