import configparser
import logging
import os
import tempfile
import time as systime
from typing import Optional

from petminion import BallRecognizer

from .BallRecognizer import BallRecognizer
from .Camera import CameraDisconnectedError, SimCamera
from .ColorCorrector import ColorCorrector
from .CV2Camera import CV2Camera  # noqa: F401 needed for find at runtime
from .Feeder import *  # noqa: F403 must use * here because we find classnames at runtime
# Not yet ready: from .PiCamera import PiCamera
from .ImageRecognizer import ImageRecognizer
from .MastodonClient import MastodonClient
from .ProcessedImage import ProcessedImage
from .RateLimit import RateLimit, SimpleLimit
from .RedditClient import RedditClient
from .SocialMediaClient import SocialMediaClient
from .TrainingRule import *  # noqa: F403 must use * here because we find classnames at runtime
from .util import app_config
from .VideoWriter import VideoWriter  # prevent name clash with datetime.time

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

    def __init__(self, is_simulated: bool = False, repeat_forever: bool = False):
        self.is_simulated = is_simulated
        self.camera = SimCamera(repeat_forever) if is_simulated else class_by_name("Camera")()

        self.social_rate = RateLimit("social_rate", 60 * 60 * 1)  # 1 post per hour
        self.social_timer = None
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
            self, rule_class)

        self.feeder = Feeder() if is_simulated else class_by_name("Feeder")()  # noqa: F405
        self.image: Optional[ProcessedImage] = None

        self.recognizers = [ImageRecognizer(), BallRecognizer()]  # FIXME, perhaps this should be part of the rule instead?
        self.color_corrector = ColorCorrector()
        self.corrector_check_rate = SimpleLimit(60)  # 1 check per minute

    def capture_image(self) -> None:
        """Grab a new image from the camera"""
        img = self.camera.read_image()

        def check_for_card() -> None:
            if self.color_corrector.look_for_card(img):
                logger.info("Found color card, saving calibration data...")
                self.color_corrector.save_state()

        if self.color_corrector.is_ready:
            # occasionally we should still look for new color corrector cards...
            if self.corrector_check_rate.can_run():
                check_for_card()

            img = self.color_corrector.correct_image(img)
            # show_image(img, "live")
        else:
            check_for_card()

        self.image = ProcessedImage(self.recognizers, img)

    def start_social(self, status_text: str, capture_seconds=64) -> None:
        """The pet just did something interesting, start a social media movie - posting capture_seconds later"""
        if not self.social_rate.can_run():
            logger.warning("Skipping social media post due to rate limit")
        else:
            if self.social_timer:
                logger.warning("Skipping social media post - already in progress")
            else:
                # if running in simulation cut the length of videos quite short
                if self.is_simulated:
                    capture_seconds = 3

                t = SimpleLimit(capture_seconds)
                t.set_ran()  # a crude way to turn this into a general alarm/timer class
                self.social_timer = t

                self.social_frame_interval = SimpleLimit(2)  # capture a frame every 2 seconds
                self.social_first_image = self.image.raw_image
                self.social_status = status_text

                # we claim 4 fps, which for 64 seconds at 4 seconds per frame means the gif will be 4 seconds of viewing time
                self.social_writer = VideoWriter(tempfile.mktemp(suffix=".mp4"), 4)

    def update_social(self) -> None:
        """Update a social media movie and possibly post it"""

        # if a social media post is in progress, add the current image to the video
        if self.social_timer:
            if self.social_frame_interval.can_run():
                self.social_writer.add_frame(self.image.raw_image)

            # we ran out of time, post the video
            if self.social_timer.can_run():
                self.social_timer = None  # stop the timer

                self.social_writer.close()

                # thumbnails are not allowed for mastondon videos!
                # media_id = self.social.upload_media_with_thumbnail(self.social_writer.filename, self.social_first_image)
                media_id = self.social.upload_media(self.social_writer.filename)
                self.social.post_status(self.social_status, [media_id])

                os.remove(self.social_writer.filename)  # Delete the video file

    def run_once(self) -> None:
        """Run one iteration of the training rules"""
        self.capture_image()
        self.update_social()
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
