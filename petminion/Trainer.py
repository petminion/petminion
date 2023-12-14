from .Camera import *
from .CV2Camera import CV2Camera
from .PiCamera import PiCamera
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

        self.camera = SimCamera() if is_simulated else class_by_name("Camera")()
        self.recognizer = ImageRecognizer()

        rule_class = class_by_name("TrainingRule")
        self.rule = TrainingRule.create_from_save(self, rule_class)

        self.feeder = Feeder() if is_simulated else class_by_name("Feeder")()
        self.image = None

    def run_once(self):
        self.image = ProcessedImage(self.recognizer, self.camera.read_image())
        self.rule.run_once()

    def run(self):
        logger.info(
            "Watching camera (use --debug for progress info. press ctrl-C to exit)...")
        while True:
            try:
                self.run_once()
            except CameraDisconnectedError as e:
                logger.info(f"exiting... { e }")
                break
        self.rule.save_state()  # Keep current feeding/schedule data
