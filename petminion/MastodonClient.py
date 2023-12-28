import logging
import tempfile

import cv2
import numpy
from mastodon import Mastodon

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

    def post_image(self, subreddit: str, title: str, image: numpy.ndarray) -> None:
        """Given an image array, post that image to mastodon"""

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as temp_file:
            cv2.imwrite(temp_file.name, image)
            media = self.client.media_post(temp_file.name, mime_type='image/jpeg')
            self.client.status_post(status=title, media_ids=[media['id']])
