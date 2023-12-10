from .ImageRecognizer import ImageDetection, ImageRecognizer

from functools import cached_property
import numpy


class ProcessedImage:

    def __init__(self, recognizer: ImageRecognizer, image: numpy.ndarray):
        self.__recognizer = recognizer
        self.image = image
        self.__annotated = None

    @property
    def annotated(self) -> numpy.ndarray:
        self.detections  # implicity will update __annotated
        return self.__annotated

    @cached_property
    def classifications(self) -> list[ImageDetection]:
        return self.__recognizer.do_classification(self.image)

    @cached_property
    def detections(self) -> list[ImageDetection]:
        a, d = self.__recognizer.do_detection(self.image)
        self.__annotated = a
        return d
