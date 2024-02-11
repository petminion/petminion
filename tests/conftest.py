import contextlib
import logging
import os
import textwrap
from http.client import HTTPConnection

import pytest

from petminion import util
from petminion.CV2Camera import show_image


@pytest.fixture(scope='session')
def test_image_dir() -> str:
    return os.path.join(os.path.dirname(__file__), 'image')


@pytest.fixture(scope='session')
def config_for_testing() -> None:
    """override the config file with our test settings"""

    util.state_loading_disabled = True  # make tests not use saved state files

    # show_image(None)  # init debug window very early otherwise it might hang later
    util.windows_allowed = False

    testing_config = textwrap.dedent("""
        [settings]
        trainingrule = SimpleFeederRule
        simsocialmedia = False
        # the class name of the _simulated_ feeder
        feeder = Feeder
    """)
    util.app_config.config.read_string(testing_config)


@pytest.fixture(scope='session')
def debug_requests_on():
    '''Switches on logging for the HTTP requests module.'''
    HTTPConnection.debuglevel = 1  # 2 to also include POST body

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
