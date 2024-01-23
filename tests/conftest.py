import os
import textwrap

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
