import logging

import pytest

# Must be before importint petminion
from petminion import Trainer, util


@pytest.mark.integtest
def test_integration():
    """A basic test of the entire app (using simulated data)
    """
    util.state_loading_disabled = True  # make tests not use saved state files
    logging.basicConfig(level=logging.DEBUG if True else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'Petminion integration test running...')

    t = Trainer(is_simulated=True)
    t.run()
