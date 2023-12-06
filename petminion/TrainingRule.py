
from .ImageRecognizer import ImageDetection

import logging
logger = logging.getLogger()



class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer

    def do_feeding(self):
        self.trainer.feeder.feed()

    def evaluate_scene(self):
        raise NotImplementedError
    
    # FIXME add thresholds for 'aggressive' or 'conservative' matching
    # FIXME add a bounding box for region to watch (so we only detect tokens that are in the bowl)
    def count_detections(self, name):
        detections = self.trainer.image.detections

        return list(map(lambda x: x.name, detections)).count(name)
    
    def is_detected(self, detections: list[ImageDetection]):    
        return self.count_detections() > 0


class CatTrainingRule0(TrainingRule):
    def __init__(self, trainer):
        super().__init__(trainer)
        self.old_count = 0
        
    def evaluate_scene(self):
        count = self.count_detections("spring")
        # self.since_success > 60 * 5 FIXME place a limit on repeated feedings in a short time?

        if count > self.old_count and self.is_detected("cat"):  # A new token appeared?
            self.do_feeding()
            self.old_count = count
        elif count < self.old_count:    # someone took away a token (cat kicked it out of camera) - FIXME use a more conservative match for this test?
            logger.warning('Token removed from target (cat is cheating? FIXME)')
            self.old_count = count
        
