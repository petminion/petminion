from imageai.Classification import ImageClassification
from imageai.Detection import ObjectDetection
from typing import NamedTuple
import urllib.request
import os
import logging
from .util import user_cache_dir

logger = logging.getLogger()


class ImageDetection(NamedTuple):
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
    def __init__(self):
        # autodownload the model files if needed

        self.detector = detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(get_model_path(
            "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/yolov3.pt", "yolov3.pt"))
        detector.loadModel()

        self.classifier = classifier = ImageClassification()
        classifier.setModelTypeAsResNet50()
        classifier.setModelPath(get_model_path(
            "https://github.com/OlafenwaMoses/ImageAI/releases/download/3.0.0-pretrained/resnet50-19c8e357.pth", "resnet50-19c8e357.pth"))
        classifier.loadModel()

    def do_detection(self, image) -> tuple[any, list[ImageDetection]]:
        annotated, detections = self.detector.detectObjectsFromImage(input_image=image,
                                                                     minimum_percentage_probability=30,
                                                                     output_type="array")

        for eachObject in detections:
            logger.debug(
                f'Detection: { eachObject["name"] } : { eachObject["percentage_probability"] } : { eachObject["box_points"] }')

        # Convert to our typed representation
        d = list(map(lambda x: ImageDetection(
            x["name"], x["percentage_probability"],
            eachObject["box_points"][0], eachObject["box_points"][1], eachObject["box_points"][2], eachObject["box_points"][3]),
            detections))
        return annotated, d

    def do_classification(self, image) -> list[ImageDetection]:
        predictions, probabilities = self.classifier.classifyImage(
            image, result_count=5)
        for eachPrediction, eachProbability in zip(predictions, probabilities):
            logger.debug(
                f'Classification: { eachPrediction } : { eachProbability }')

        # Convert to our typed representation
        d = list(map(lambda prediction, probability: ImageDetection(
            prediction, probability), predictions, probabilities))

        return d
