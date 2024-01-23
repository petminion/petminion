import logging
import os
import tempfile
import time
from typing import Optional

import cv2
import numpy
from mastodon import Mastodon, errors

from .SocialMediaClient import SocialMediaClient
from .util import app_config

logger = logging.getLogger()


class MastodonClient(SocialMediaClient):
    """Talks to the Reddit API for posting pictures of birds and pets"""

    def __init__(self) -> None:
        """ Create an instance of the Mastodon class
        see https://botwiki.org/resource/tutorial/how-to-make-a-mastodon-botsin-space-app-bot/
        https://botwiki.org/resource/guide/the-definitive-guide-to-creative-botmaking/

        Looks for app settings mastodon.AccessToken and mastodon.InstanceUrl

        FIXME have the bot put in relevant hashtags
        FIXME have the bot delete old images
        FIXME limit posts to ones with very high accuracy and a max of one post per day

        example config.ini entries:
        [mastodon]
        AccessToken = YOURSECRETACCESSTOKEN
        InstanceUrl = https://YOURMASTODONINSTANCE
        """

        s = 'mastodon'
        self.client = Mastodon(
            access_token=app_config.config.get(s, 'AccessToken'),
            api_base_url=app_config.config.get(s, 'InstanceUrl')
        )

    def upload_media(self, filename: str, thumbnail: Optional[str] = None) -> str:
        """Upload media+thumbnail and return the media id"""

        logger.info(f"Uploading {filename} to mastodon")

        if os.path.getsize(filename) > 40 * 1024 * 1024:
            raise Exception("Video file size exceeds Mastodon 40MB limit")

        # not needed - can be detected from filename , mime_type='image/jpeg'
        media = self.client.media_post(filename, thumbnail=thumbnail)
        return media['id']

    def upload_media_with_thumbnail(self, filename: str, thumbnail: numpy.ndarray) -> str:
        """Upload media+thumbnail and return the media id"""

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as temp_file:
            cv2.imwrite(temp_file.name, thumbnail)
            return self.upload_media(filename, temp_file.name)

    def upload_image(self, image: numpy.ndarray) -> str:
        """Upload an image and return the media id"""

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as temp_file:
            cv2.imwrite(temp_file.name, image)
            return self.upload_media(temp_file.name)

    def post_status(self, title: str, media_ids: list[str] = []) -> None:
        """Post a status to mastodon"""
        for attempt in range(3):
            try:
                self.client.status_post(status=title, visibility='unlisted', media_ids=media_ids)
                return  # success
            except errors.MastodonAPIError as e:
                # mastodon exception args are generated as follows
                # raise ex_type('Mastodon API returned error', response_object.status_code, response_object.reason, error_msg)

                error_code = e.args[1]
                if error_code == 422:
                    logger.warning(f"Mastodon told us to wait: {e}")
                    time.sleep(5)
                    # Try again after a bit of delay...
                else:
                    raise e

    def post_image(self, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to mastodon"""

        id = self.upload_image(image)
        self.post_status(title, [id])
