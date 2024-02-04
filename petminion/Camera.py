import logging
import os
from importlib.resources import as_file, files

import cv2
import numpy

from . import resources

logger = logging.getLogger()


class CameraDisconnectedError(IOError):
    """A camera was disconnected
    """
    pass


class Camera:
    """A base-class for camera classes
    """

    def read_image(self) -> numpy.ndarray:
        """Subclasses must implement

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError


class SimCamera(Camera):
    """A simulated camera that fakes images by reading files from a filesystem.
    """

    def __init__(self, repeat_forever: bool = False):
        """Constructor

        Args:
            repeat_forever (bool, optional): If false we will end the stream after the last test-image is consumed, if true we will loop back to the first image. 
            Defaults to False.
        """
        # my_dir = os.path.dirname(__file__)  # where this python file is located
        # self.img_dir = os.path.join(my_dir, "..", "tests", "image")
        self.img_dir = files(resources).joinpath("simcamera")
        self.filenames = list(filter(lambda x: x.endswith(".jpg"), os.listdir(self.img_dir)))
        self.next_name = iter(self.filenames)
        self.repeat_forever = repeat_forever

    def read_image(self) -> numpy.ndarray:
        """Read an image from our tests directory.

        Raises:
            CameraDisconnectedError: at end of stream

        Returns:
            numpy.ndarray: A frame from the camera
        """
        f = next(self.next_name, None)
        if not f:
            if not self.repeat_forever:
                raise CameraDisconnectedError(
                    "End of simulated camera frames reached")

            # restart with the list of files again
            self.next_name = iter(self.filenames)
            f = next(self.next_name, None)
            if not f:
                # Note: this should not be simulated as CameraDisconnectedError
                raise IOError("No frames in simulated camera")

        return cv2.imread(os.path.join(self.img_dir, f))
