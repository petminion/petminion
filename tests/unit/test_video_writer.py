
import os

import numpy as np

from petminion.VideoWriter import VideoWriter


def test_video_writer(tmp_path):
    path = str(tmp_path / "test.mp4")
    with VideoWriter(path) as vw:
        vw.add_frame(np.zeros((480, 640, 3), dtype=np.uint8))
        vw.add_frame(np.zeros((480, 640, 3), dtype=np.uint8))
        vw.add_frame(np.zeros((480, 640, 3), dtype=np.uint8))
    assert os.path.exists(path)
