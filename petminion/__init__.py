import logging

logger = logging.getLogger()

class Feeder:
    
    def feed():
        pass

class ImageClassification:
    pass

class ImageDetection:
    pass

class ImageRecognizer:
    def do_detection(image) -> tuple[any, list[ImageDetection]]:
        return None
    
    def do_classification(image) -> list[ImageClassification]:
        return None


class TrainingRule:
    def __init__(self, trainer):
        self.trainer = trainer

    def do_feeding(self):
        self.trainer.feeder.feed()

    def evaluate_scene(self):
        pass



class CatTrainingRule0(TrainingRule):
    pass



