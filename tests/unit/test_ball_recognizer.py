
import os

import cv2
import pytest

from petminion.BallRecognizer import BallRecognizer


@pytest.fixture
def recognizer():
    return BallRecognizer()


def test_ball_detector(recognizer, test_image_dir) -> None:
    # Read the image using OpenCV
    path = os.path.join(test_image_dir, 'cat.jpg')
    img = cv2.imread(path)
    annotated, result = recognizer.do_detection(img)
    assert result == []
