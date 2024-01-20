
import os

import cv2
import pytest

from petminion.Trainer import Trainer


@pytest.fixture
def trainer():
    return Trainer(is_simulated=True)


def test_simple_feeder(trainer) -> None:
    # FIXME
    assert True
