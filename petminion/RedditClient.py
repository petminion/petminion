import praw
import logging
import numpy
import tempfile
import cv2
import os

logger = logging.getLogger()


class RedditClient:
    """Talks to the Reddit API for posting pictures of birds and pets"""

    def __init__(self) -> None:
        self.reddit = praw.Reddit("petminion")
        logger.info(
            f"Connected to Reddit read_only={ self.reddit.read_only } as { self.reddit.user.me() }")

    def post_image(self, subreddit: str, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to the specified subreddit"""

        # directory and contents will be autodeleted
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'petminion-upload.png')
            cv2.imwrite(path, image)

            s = self.reddit.subreddit(subreddit)
            logger.info(f"Posting to subreddit {subreddit} title={title}")
            s.submit_image(title, path)
        pass


# reddit credentials are found in /.config/praw.ini per https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html

# https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html#praw.models.Subreddit.submit_image
