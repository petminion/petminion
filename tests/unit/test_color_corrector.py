
import os

import cv2
import pytest

from petminion.ColorCorrector import ColorCorrector


def test_color_corrector(test_image_dir) -> None:
    # Read the image using OpenCV
    c = ColorCorrector()

    path = os.path.join(test_image_dir, 'test-pantone.jpg')
    img = cv2.imread(path)
    c.look_for_card(img)
    assert True
