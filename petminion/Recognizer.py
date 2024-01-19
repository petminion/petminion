import logging
from typing import NamedTuple, Optional

import numpy

logger = logging.getLogger()


class ImageDetection(NamedTuple):
    """
    Represents the result of an image detection.

    Attributes:
        name (str): The name of the detected object.
        probability (float): The probability/confidence score of the detection.
        x1 (int, optional): The x-coordinate of the top-left corner of the bounding box. Defaults to -1.
        y1 (int, optional): The y-coordinate of the top-left corner of the bounding box. Defaults to -1.
        x2 (int, optional): The x-coordinate of the bottom-right corner of the bounding box. Defaults to -1.
        y2 (int, optional): The y-coordinate of the bottom-right corner of the bounding box. Defaults to -1.
    """
    name: str
    probability: float
    x1: int = -1
    y1: int = -1
    x2: int = -1
    y2: int = -1


class Recognizer:
    """
    A base class for performing object detection and image classification.

    Attributes:
        detector: An instance of ObjectDetection class for object detection.
        classifier: An instance of ImageClassification class for image classification.

    Methods:
        do_detection: Performs object detection on an image and returns annotated image and a list of ImageDetection objects.
        do_classification: Performs image classification on an image and returns a list of ImageDetection objects.
    """

    def __init__(self):
        """
        Initializes the Recognizer class.
        """
        pass

    def do_detection(self, image: numpy.ndarray) -> tuple[Optional[numpy.ndarray], list[ImageDetection]]:
        """
        Performs object detection on the given image.

        Args:
            image: A numpy array representing the image.

        Returns:
            A tuple containing the annotated image and a list of ImageDetection objects.
        """
        # Stub always claims no detection
        return []

    def do_classification(self, image: numpy.ndarray) -> list[ImageDetection]:
        """
        Performs image classification on the given image.

        Args:
            image: A numpy array representing the image.

        Returns:
            A list of ImageDetection objects.
        """

        # Stub always claims no classifications
        return []
