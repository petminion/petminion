import typing
from functools import cached_property

import cv2
import numpy

from .ImageRecognizer import ImageDetection, ImageRecognizer


class ProcessedImage:
    """
    Represents a processed image with associated annotations, classifications, and detections.

    Parameters:
    - recognizers (list[ImageRecognizer]): A list of ImageRecognizer objects used for image processing.
    - raw_image (numpy.ndarray): The raw image to be processed.
    """

    def __init__(self, recognizers: list[ImageRecognizer], raw_image: numpy.ndarray):
        self.__recognizers = recognizers

        # for machine vision purposes we use a lower res image for processing
        image = raw_image
        w = image.shape[1]  # Set w to the width of the frame
        if (w != 640):
            # Resize the frame to 640x480
            dest_size = (640, 480)
            image = cv2.resize(image, dest_size, interpolation=cv2.INTER_LANCZOS4)
        self.raw_image = raw_image
        self.image = image

    @property
    def annotated(self) -> typing.Optional[numpy.ndarray]:
        """
        Returns the annotated image with visualized detections. (or None if no annotations available)
        """
        a = self.image.copy()
        for d in self.detections:  # implicitly will update __annotated
            # Draw the bounding box on the frame
            cv2.rectangle(a, (d.x1, d.y1), (d.x2, d.y2), (0, 255, 0), 2)
            cv2.putText(a, d.name, (d.x1, d.y1), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
        return a

    @cached_property
    def classifications(self) -> list[ImageDetection]:
        """
        Returns a list of ImageDetection objects representing the classifications of the image.
        """
        classifications = []
        for recognizer in self.__recognizers:
            classifications.extend(recognizer.do_classification(self.image))
        return classifications

    @cached_property
    def detections(self) -> list[ImageDetection]:
        """
        Returns a list of ImageDetection objects representing the object detections in the image.
        """
        detections = []
        for recognizer in self.__recognizers:
            d = recognizer.do_detection(self.image)
            detections.extend(d)

        return detections
