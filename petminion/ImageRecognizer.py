from imageai.Classification import ImageClassification
from imageai.Detection import ObjectDetection


import os

# FIXME store these files in our app config instead
# execution_path = os.getcwd()
execution_path = "/home/kevinh/development/crowbot/experiments/imageai"

class ImageDetection:
    pass

class ImageRecognizer:
    def __init__(self):
        # FIXME - autodownload the model files if needed

        self.detector = detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath( os.path.join(execution_path , "yolov3.pt"))
        detector.loadModel()

        self.classifier = classifier = ImageClassification()
        classifier.setModelTypeAsResNet50()
        classifier.setModelPath(os.path.join(execution_path, "resnet50-19c8e357.pth"))
        classifier.loadModel()

    def do_detection(self, image) -> tuple[any, list[ImageDetection]]:
        annotated, detections = self.detector.detectObjectsFromImage(input_image=image, 
                                            minimum_percentage_probability=30,
                                            output_type="array")
        
        print("Detections")   
        for eachObject in detections:
            print("  ", eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )

        # FIXME                
        return annotated, []
    
    def do_classification(self, image) -> list[ImageDetection]:
        predictions, probabilities = self.classifier.classifyImage(image, result_count=5 )
        for eachPrediction, eachProbability in zip(predictions, probabilities):
            print("  ", eachPrediction , " : " , eachProbability)

        # FIXME        
        return []
