from .Camera import CV2Camera
from .ImageRecognizer import *
from .Feeder import *
from .TrainingRule import *

class Trainer:
    def __init__(self):
        self.camera = CV2Camera()
        self.recognizer = ImageRecognizer()
        self.rule = CatTrainingRule0(self)
        self.feeder = Feeder()
        self.image = None

    def runOnce(self):
        self.image = self.camera.read_image()
        self.rule.evaluate_scene()

    def run(self):
        while True:
            self.runOnce()

