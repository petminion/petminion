import configparser
import logging
import os
import tempfile

import cv2
import numpy
import praw

logger = logging.getLogger()


class RedditClient:
    """Talks to the Reddit API for posting pictures of birds and pets"""

    def __init__(self, is_simulated: bool = False) -> None:
        """Constructor

        Args:
            is_simulated (bool, optional): If true, most code paths will be used but actual posting to reddit will be skipped. Defaults to False.
        """
        section_name = "petminion"
        self.is_simulated = is_simulated
        self.reddit = None  # assume failure
        try:
            self.reddit = praw.Reddit(section_name)
            self.reddit.validate_on_submit = True  # Needed by reddit someday in the future
            logger.info(
                f"Connected to Reddit read_only={ self.reddit.read_only } as { self.reddit.user.me() }")
        except configparser.NoSectionError:
            logger.warning(
                f"No reddit config file (~/.config/praw.ini) { section_name } found, disabling reddit posts")

    def post_image(self, subreddit: str, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to the specified subreddit"""

        if not self.reddit:
            return  # No reddit connection

        # directory and contents will be autodeleted
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'petminion-upload.png')
            cv2.imwrite(path, image)

            s = self.reddit.subreddit(subreddit)
            if self.is_simulated:
                logger.warn(f"Skipping reddit post because simulating...")
            else:
                logger.info(f"Posting to subreddit {subreddit} title={title}")
                s.submit_image(title, path)
        pass


# reddit credentials are found in /.config/praw.ini per https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html

# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit_image
