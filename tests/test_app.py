
from petminion import Trainer

import pytest
import logging


@pytest.mark.integtest
def test_integration():
    """A basic test of the entire app (using simulated data)
    """
    logging.basicConfig(level=logging.DEBUG if True else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'Petminion integration test running...')

    t = Trainer(is_simulated=True)
    t.run()
