
import logging

import pytest

from petminion.PushoverClient import PushoverClient


@pytest.mark.social
def test_pushover():
    p = PushoverClient()
    p.post_status("test message")
