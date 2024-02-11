
import os

import cv2
import numpy as np

from petminion.VideoWriter import GIFWriter, MP4Writer


def test_mp4_writer(test_image_dir, tmp_path):
    path = str(tmp_path / "test.mp4")
    img = cv2.imread(os.path.join(test_image_dir, 'test-pantone.jpg'))
    with MP4Writer(path) as vw:
        # vw.add_frame(np.zeros((480, 640, 3), dtype=np.uint8))
        vw.add_frame(img)
        vw.add_frame(img)
        vw.add_frame(img)
    assert os.path.exists(path)


def test_gif_writer(test_image_dir, tmp_path):
    path = str(tmp_path / "test.gif")
    img = cv2.imread(os.path.join(test_image_dir, 'test-pantone.jpg'))
    with GIFWriter(path) as vw:
        # vw.add_frame(np.zeros((480, 640, 3), dtype=np.uint8))
        vw.add_frame(img)
        vw.add_frame(img)
        vw.add_frame(img)
    assert os.path.exists(path)
