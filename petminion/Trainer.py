import configparser
import logging
import time as systime  # prevent name clash with datetime.time

from .Camera import CameraDisconnectedError, SimCamera
from .CV2Camera import CV2Camera  # noqa: F401 needed for find at runtime
from .Feeder import *  # noqa: F403 must use * here because we find classnames at runtime
# Not yet ready: from .PiCamera import PiCamera
from .ImageRecognizer import ImageRecognizer
from .MastodonClient import MastodonClient
from .ProcessedImage import ProcessedImage
from .RateLimit import RateLimit
from .RedditClient import RedditClient
from .SocialMediaClient import SocialMediaClient
from .TrainingRule import *  # noqa: F403 must use * here because we find classnames at runtime
from .util import app_config

logger = logging.getLogger()
recognizers = [ImageRecognizer()]


def class_by_name(name):
    """
    Look for a named class in the settings file and try to create an instance
    gives clear error message if not found
    """
    cname = app_config.settings[name]
    class_obj = globals()[cname]
    return class_obj


class Trainer:
    """Class representing a trainer for pet minions.

    The Trainer class is responsible for capturing images from a camera, running training rules,
    and sharing images to social media. It provides methods to run the trainer once or run it
    continuously until terminated.

    Attributes:
        is_simulated (bool): Flag indicating if the trainer is running in simulated mode.
        camera: An instance of the camera class used for capturing images.
        recognizer: An instance of the image recognizer class used for image processing.
        reddit: An instance of the Reddit client class used for posting images to social media.
        rule: An instance of the training rule class used for running training rules.
        feeder: An instance of the feeder class used for feeding the pet minion.
        image: The current captured image.

    Methods:
        capture_image: Captures a new image from the camera.
        share_social: Shares the current image to social media with a given title.
        run_once: Runs one iteration of the training rules.
        run: Runs the trainer continuously until terminated.
    """

    def __init__(self, is_simulated: bool = False, force_clean: bool = False):
        self.is_simulated = is_simulated
        self.camera = SimCamera() if is_simulated else class_by_name("Camera")()

        self.social_rate = RateLimit("social_rate", 60 * 60 * 1)  # 1 post per hour
        self.social = SocialMediaClient()  # provide a stub implementation that does nothing
        if not is_simulated or app_config.settings.getboolean('SimSocialMedia'):
            try:
                self.social = RedditClient()
            except configparser.Error:
                logger.warning("RedditClient not available - reddit posting disabled")
            try:
                self.social = MastodonClient()
            except configparser.Error:
                logger.warning("MastodonClient not available - reddit posting disabled")

        rule_class = class_by_name("TrainingRule")
        self.rule = TrainingRule.create_from_save(  # noqa: F405
            self, rule_class) if not force_clean else rule_class(self)

        self.feeder = Feeder() if is_simulated else class_by_name("Feeder")()  # noqa: F405
        self.image = None

    def capture_image(self) -> None:
        """Grab a new image from the camera"""
        self.image = ProcessedImage(recognizers, self.camera.read_image())

    def share_social(self, title: str) -> None:
        """Share the current image to social media with the given title"""
        if self.social_rate.can_run():
            self.social.post_image(title, self.image.raw_image)
        else:
            logger.warning("Skipping social media post due to rate limit")

    def run_once(self) -> None:
        """Run one iteration of the training rules"""
        self.capture_image()
        self.rule.run_once()
        # sleep for 100ms, because if we are on a low-end rPI the image processing (if allowed to run nonstop) will fully consume the CPU (starving critical things like zigbee)
        systime.sleep(0.100)

    def run(self) -> None:
        """Run forever, the app is normally terminated by SIGTERM"""
        logger.info(
            "Watching camera (use --debug for progress info. press ctrl-C to exit)...")
        while True:
            try:
                self.run_once()
            except CameraDisconnectedError as e:
                logger.info(f"exiting... { e }")
                break
