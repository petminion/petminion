from .ImageRecognizer import ImageRecognizer

from functools import cached_property

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
    
