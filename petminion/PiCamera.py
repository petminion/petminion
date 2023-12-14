import picamera2
import logging
import os
import numpy
from .Camera import Camera

logger = logging.getLogger()




class PiCamera(Camera):
    """Reads from the built-in raspberry pi camera
    """

    def __init__(self):
        """Constructor

        Raises:
            ConnectionError: Raised if we don't have permission to access the camera device
        """
        logger.error("Picamera support is UNTESTED! FIXME")
        self.cam = cam = picamera2.PiCamera2()
    
        # cam.start_preview()

    def read_image(self) -> numpy.ndarray:
        """Read a frame from the camera

        Raises:
            CameraDisconnectedError: Raised if the camera is removed

        Returns:
            numpy.ndarray: A frame from the camera
        """
        # we reuse the old numpy array - I'm not sure if that is a good idea FIXME
        a = self.cam.capture_array()
        return self.output.array
