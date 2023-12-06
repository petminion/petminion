from imageai.Classification import ImageClassification
from imageai.Detection import ObjectDetection
from typing import NamedTuple
import os
import logging

logger = logging.getLogger()


# FIXME store these files in our app config instead
# execution_path = os.getcwd()
execution_path = "/home/kevinh/development/crowbot/experiments/imageai"


class ImageDetection(NamedTuple):
    name: str
    probability: float
    x1: int = -1
    y1: int = -1
    x2: int = -1
    y2: int = -1


class ImageRecognizer:
    def __init__(self):
        # FIXME - autodownload the model files if needed

        self.detector = detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath(os.path.join(execution_path, "yolov3.pt"))
        detector.loadModel()

        self.classifier = classifier = ImageClassification()
        classifier.setModelTypeAsResNet50()
        classifier.setModelPath(os.path.join(
            execution_path, "resnet50-19c8e357.pth"))
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
