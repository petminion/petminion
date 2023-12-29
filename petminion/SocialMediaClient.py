import logging

import numpy

logger = logging.getLogger()


class SocialMediaClient:
    """A client for posting images to social media platforms"""

    def post_image(self, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to social media"""
        logger.warning("Social Media posts are disabled - not posting")
