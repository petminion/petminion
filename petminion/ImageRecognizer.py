import logging
import os
import urllib.request
from typing import NamedTuple

import numpy
from imageai.Classification import ImageClassification
from imageai.Detection import ObjectDetection

from .util import app_config, user_cache_dir

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


def get_model_path(url, filename):
    """Return the full path to reach a specified model file, if not found locally fetch from internet"""
    models_dir = user_cache_dir()
    path = os.path.join(models_dir, filename)
    if not os.path.exists(path):
        logger.info(
            f"Model file '{ filename }' not found in cache, downloading...")
        urllib.request.urlretrieve(url, path)
    return path


class ImageRecognizer:
    """
    A class that performs object detection and image classification using ImageAI library.

    Attributes:
        detector: An instance of ObjectDetection class for object detection.
        classifier: An instance of ImageClassification class for image classification.

    Methods:
        do_detection: Performs object detection on an image and returns annotated image and a list of ImageDetection objects.
        do_classification: Performs image classification on an image and returns a list of ImageDetection objects.
    """

    def __init__(self):
        """
        Initializes the ImageRecognizer class by loading the model files for object detection and image classification.
        The model files are downloaded if needed.
        """
        # autodownload the model files if needed
        fast_and_small = app_config.settings['FastModel']

        self.detector = detector = ObjectDetection()
        if fast_and_small:
            detector.setModelTypeAsTinyYOLOv3()
            detector.setModelPath(get_model_path(
                "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/tiny-yolov3.pt", "tiny-yolov3.pt"))
        else:
            detector.setModelTypeAsYOLOv3()
            detector.setModelPath(get_model_path(
                "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolov3.pt", "yolov3.pt"))
        logger.debug(
            f"Loading fast={fast_and_small} detector model (If this takes a long time, your computer doesn't have enough RAM)...")
        detector.loadModel()

        self.classifier = classifier = ImageClassification()
        if fast_and_small:
            classifier.setModelTypeAsMobileNetV2()
            classifier.setModelPath(get_model_path(
                "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/mobilenet_v2-b0353104.pth", "mobilenet_v2-b0353104.pth"))
        else:
            classifier.setModelTypeAsResNet50()
            classifier.setModelPath(get_model_path(
                "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/resnet50-19c8e357.pth", "resnet50-19c8e357.pth"))
        logger.debug(
            "Loading classifier model (If this takes a long time, "
            "your computer doesn't have enough RAM)..."
        )
        classifier.loadModel()

    def do_detection(self, image: numpy.ndarray) -> tuple[numpy.ndarray, list[ImageDetection]]:
        """
        Performs object detection on the given image.

        Args:
            image: A numpy array representing the image.

        Returns:
            A tuple containing the annotated image (or None if no detections found) and a list of ImageDetection objects.
        """
        # too verbose
        # logger.debug("Doing detection...")
        annotated, detections = self.detector.detectObjectsFromImage(
            input_image=image,
            minimum_percentage_probability=30,
            output_type="array"
        )

        # for eachObject in detections:
        #    logger.debug(
        #        f'Detection: { eachObject["name"] } : { eachObject["percentage_probability"] } : { eachObject["box_points"] }')

        # Convert to our typed representation
        d = list(map(lambda x: ImageDetection(
            x["name"], x["percentage_probability"],
            x["box_points"][0], x["box_points"][1],
            x["box_points"][2], x["box_points"][3]
        ), detections))

        if not len(d):
            annotated = None  # if no annotations found
        return annotated, d

    def do_classification(self, image: numpy.ndarray) -> list[ImageDetection]:
        """
        Performs image classification on the given image.

        Args:
            image: A numpy array representing the image.

        Returns:
            A list of ImageDetection objects representing the predicted classes and probabilities.
        """
        logger.debug("Doing classification...")
        predictions, probabilities = self.classifier.classifyImage(
            image, result_count=5)
        for eachPrediction, eachProbability in zip(predictions, probabilities):
            logger.debug(
                f'Classification: { eachPrediction } : { eachProbability }')

        # Convert to our typed representation
        d = list(map(lambda prediction, probability: ImageDetection(
            prediction, probability), predictions, probabilities))

        return d
