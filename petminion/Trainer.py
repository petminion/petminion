from .Camera import *
from .ImageRecognizer import *
from .Feeder import *
from .TrainingRule import *
from .ProcessedImage import ProcessedImage
from .util import app_config


def class_by_name(name):
    """
    Look for a named class in the settings file and try to create an instance
    gives clear error message if not found
    """
    cname = app_config.settings[name]
    class_obj = globals()[cname]
    return class_obj


class Trainer:
    def __init__(self, is_simulated: bool = False):

        self.camera = SimCamera() if is_simulated else CV2Camera()
        self.recognizer = ImageRecognizer()
        self.rule = class_by_name("TrainingRule")(self)
        self.feeder = Feeder() if is_simulated else class_by_name("Feeder")()
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
