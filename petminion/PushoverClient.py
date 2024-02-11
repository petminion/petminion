import logging
from typing import Optional

import requests

from .util import app_config

logger = logging.getLogger()


class PushoverClient:
    """A client for posting images via pushover.net"""

    def __init__(self) -> None:
        """ Create an instance of the PushoverClient.
        example config.ini entries:
        [pushover]
        ApiToken = SECRETFROMPUSHOVER
        UserKey = SECRETFROMPUSHOVER
        """

        s = 'pushover'
        self.api_token = app_config.config.get(s, 'ApiToken'),
        self.user_key = app_config.config.get(s, 'UserKey')

    def upload_media(self, filename: str, thumbnail: Optional[str] = None) -> str:
        """upload media for use in post_status()"""
        return filename  # We just use the provided filename as the media id

    def post_status(self, title: str, media_ids: list[str] = []) -> None:
        """Post a status"""

        data = {
            "token": self.api_token,
            "user": self.user_key,
            "title": "Petminion event",
            "message": title}

        # FIXME, for now we assume only one attachment
        if len(media_ids) > 0:
            data["files"] = {"attachment": ("attachment.gif", open(media_ids[0], "rb"), "image/gif")}

        r = requests.post("https://api.pushover.net/1/messages.json", data)
        logger.info(f"Pushover.net replied {r.text}")
