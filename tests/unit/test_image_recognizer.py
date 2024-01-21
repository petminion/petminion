
import os

import cv2
import pytest

from petminion.ImageRecognizer import ImageRecognizer


@pytest.fixture
def recognizer():
    return ImageRecognizer()


def test_classifier(recognizer, test_image_dir) -> None:
    # Read the image using OpenCV
    path = os.path.join(test_image_dir, 'cat.jpg')
    img = cv2.imread(path)
    result = recognizer.do_classification(img)
    assert result[0].name == 'Egyptian cat'


def test_image_detector(recognizer, test_image_dir) -> None:
    # Read the image using OpenCV
    path = os.path.join(test_image_dir, 'cat.jpg')
    img = cv2.imread(path)
    annotated, result = recognizer.do_detection(img)
    assert result[0].name == 'cat'
