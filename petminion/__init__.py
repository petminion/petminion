import logging
from functools import cached_property

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


class ProcessedImage:

    def __init__(self, recognizer: ImageRecognizer, image):
        self.__recognizer = recognizer
        self.image = image
        self.__annotated = None

    @property
    def annotated(self):
        self.detections() # implicity will update __annotated
        return self.__annotated

    @cached_property
    def classifications(self):
        return self.__recognizer.do_classification(self.image)        

    @cached_property
    def detections(self):
        a, d = self.__recognizer.do_detection(self.image)
        self.__annotated = a
        return d
    

