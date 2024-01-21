import os
import textwrap

import pytest

from petminion import util


@pytest.fixture(scope='session')
def test_image_dir() -> str:
    return os.path.join(os.path.dirname(__file__), 'image')


@pytest.fixture(scope='session')
def config_for_testing() -> None:
    """override the config file with our test settings"""

    util.state_loading_disabled = True  # make tests not use saved state files

    testing_config = textwrap.dedent("""
        [settings]
        trainingrule = SimpleFeederRule
        simsocialmedia = False
        # the class name of the _simulated_ feeder
        feeder = Feeder
    """)
    util.app_config.config.read_string(testing_config)
