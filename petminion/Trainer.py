from .Camera import *
from .ImageRecognizer import *
from .Feeder import *
from .TrainingRule import *
from .ProcessedImage import ProcessedImage


class Trainer:
    def __init__(self, is_simulated: bool = False):

        self.camera = SimCamera() if is_simulated else CV2Camera()
        self.recognizer = ImageRecognizer()
        self.rule = SimpleFeederRule(self, "bird")
        self.feeder = Feeder() if is_simulated else ZigbeeFeeder()
        self.image = None

    def run_once(self):
        self.image = ProcessedImage(self.recognizer, self.camera.read_image())
        self.rule.run_once()

    def run(self):
        while True:
            try:
                self.run_once()
            except CameraDisconnectedError as e:
                logger.info(f"exiting... { e }")
                break
