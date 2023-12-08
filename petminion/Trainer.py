from .Camera import *
from .ImageRecognizer import *
from .Feeder import *
from .TrainingRule import *
from .ProcessedImage import ProcessedImage


class Trainer:
    def __init__(self, is_simulated: bool = False):

        self.camera = SimCamera() if is_simulated else CV2Camera()
        self.recognizer = ImageRecognizer()
        self.rule = CatFeederRule(self)
        self.feeder = Feeder() if is_simulated else ZigbeeFeeder()
        self.image = None

    def runOnce(self):
        self.image = ProcessedImage(self.recognizer, self.camera.read_image())
        self.rule.evaluate_scene()

    def run(self):
        while True:
            try:
                self.runOnce()
            except CameraDisconnectedError as e:
                logger.info(f"exiting... { e }")
                break
