import logging
import time as systime  # prevent name clash with datetime.time

from .Camera import CameraDisconnectedError, SimCamera
from .CV2Camera import CV2Camera
from .Feeder import *  # must use * here because we find classnames at runtime
# Not yet ready: from .PiCamera import PiCamera
from .ImageRecognizer import ImageRecognizer
from .ProcessedImage import ProcessedImage
from .RedditClient import RedditClient
from .TrainingRule import *  # must use * here because we find classnames at runtime
from .util import app_config

logger = logging.getLogger()


def class_by_name(name):
    """
    Look for a named class in the settings file and try to create an instance
    gives clear error message if not found
    """
    cname = app_config.settings[name]
    class_obj = globals()[cname]
    return class_obj


class Trainer:
    def __init__(self, is_simulated: bool = False, force_clean: bool = False):

        self.is_simulated = is_simulated
        self.camera = SimCamera() if is_simulated else class_by_name("Camera")()
        self.recognizer = ImageRecognizer()

        self.reddit = RedditClient(is_simulated)

        rule_class = class_by_name("TrainingRule")
        self.rule = TrainingRule.create_from_save(
            self, rule_class) if not force_clean else rule_class(self)

        self.feeder = Feeder() if is_simulated else class_by_name("Feeder")()
        self.image = None

    def capture_image(self):
        """Grab a new image from the camera"""
        self.image = ProcessedImage(self.recognizer, self.camera.read_image())

    def share_social(self, title: str) -> None:
        """Share the current image to social media with the given title"""
        self.reddit.post_image("petminion_test", title, self.image.annotated)

    def run_once(self):
        """Run one iteration of the training rules"""
        self.capture_image()
        self.rule.run_once()
        # sleep for 100ms, because if we are on a low-end rPI the image processing (if allowed to run nonstop) will fully consume the CPU (starving critical things like zigbee)
        systime.sleep(0.100)

    def run(self):
        """Run forever, the app is normally terminated by SIGTERM"""
        logger.info(
            "Watching camera (use --debug for progress info. press ctrl-C to exit)...")
        try:
            while True:
                try:
                    self.run_once()
                except CameraDisconnectedError as e:
                    logger.info(f"exiting... { e }")
                    break
        finally:
            self.rule.save_state()  # Keep current feeding/schedule data even if we get an exception
