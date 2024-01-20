import os

import pytest


@pytest.fixture(scope='session')
def test_image_dir():
    return os.path.join(os.path.dirname(__file__), 'image')
