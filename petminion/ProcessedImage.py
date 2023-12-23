from .ImageRecognizer import ImageDetection, ImageRecognizer

from functools import cached_property
import numpy


class ProcessedImage:
    """
    Represents a processed image with associated annotations, classifications, and detections.
    """

    def __init__(self, recognizer: ImageRecognizer, image: numpy.ndarray):
        self.__recognizer = recognizer
        self.image = image
        self.__annotated = None

    @property
    def annotated(self) -> numpy.ndarray:
        """
        Returns the annotated image with visualized detections.
        """
        self.detections  # implicitly will update __annotated
        return self.__annotated

    @cached_property
    def classifications(self) -> list[ImageDetection]:
        """
        Returns a list of ImageDetection objects representing the classifications of the image.
        """
        return self.__recognizer.do_classification(self.image)

    @cached_property
    def detections(self) -> list[ImageDetection]:
        """
        Returns a list of ImageDetection objects representing the object detections in the image.
        """
        a, d = self.__recognizer.do_detection(self.image)
        self.__annotated = a
        return d
