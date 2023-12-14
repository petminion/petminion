import cv2
import logging
import os
import numpy
from .Camera import Camera, CameraDisconnectedError

logger = logging.getLogger()


class CV2Camera(Camera):
    """Uses the OpenCV API to read from a USB webcam.
    """

    def __init__(self):
        """Constructor

        Raises:
            ConnectionError: Raised if we don't have permission to access the camera device
        """
        # initialize the camera
        # If you have multiple camera connected with
        # current device, assign a value in cam_port
        # variable according to that
        cam_port = 0
        self.cam = cam = cv2.VideoCapture(cam_port)

        # cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('U','Y','V','Y'))
        # cam.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        # cam.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera width={ width }, height={height}")

        # we check if the camera is opened previously or not
        if (cam.isOpened() == False):
            raise ConnectionError("Can't access camera")

    def read_image(self) -> numpy.ndarray:
        """Read a frame from the camera

        Raises:
            CameraDisconnectedError: Raised if the camera is removed

        Returns:
            numpy.ndarray: A frame from the camera
        """
        # reading the input using the camera
        camGood, camImage = self.cam.read()

        # If image will detected without any error,
        # show result
        if camGood:
            return camImage
        else:
            raise CameraDisconnectedError("Camera read error")
