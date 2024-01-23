import logging

import numpy

logger = logging.getLogger()


class SocialMediaClient:
    """A client for posting images to social media platforms"""

    def post_image(self, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to social media"""
        logger.warning("Social Media posts are disabled - not posting")

    def upload_media_with_thumbnail(self, filename: str, thumbnail: numpy.ndarray) -> str:
        logger.warning("Social Media posts are disabled - not posting")

    def upload_image(self, image: numpy.ndarray) -> str:
        logger.warning("Social Media posts are disabled - not posting")

    def post_status(self, title: str, media_ids: list[str] = []) -> None:
        """Post a status to mastodon"""
        logger.warning("Social Media posts are disabled - not posting")
