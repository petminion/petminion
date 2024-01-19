import logging
import os
import tempfile

import cv2
import numpy

from .Camera import Camera, CameraDisconnectedError
from .RateLimit import RateLimit
from .util import has_windows

logger = logging.getLogger()

live_capture_limit = RateLimit("live_capture_limit", 5)  # every few seconds


def show_image(image: numpy.ndarray) -> None:
    if False and has_windows():  # FIXME hangs when calling any gui functions
        window_name = "petminion"
        # cv2.startWindowThread()
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(window_name, 640, 480)
        if image:
            cv2.imshow(window_name, image)
        cv2.waitKey(1)
    else:
        # no gui - at least save a live image every few seconds
        if image is not None and live_capture_limit.can_run():
            filepath = os.path.join(
                tempfile.gettempdir(), "petminion_live.png")
            cv2.imwrite(filepath, image)


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
        # cam_port = 0
        # we no longer use port numbers, instead we use linux udev rules to assign a consistent name
        # we manually specify V4L2 as the backend because ANY tries to parse the filename for a # pattern if the device is not found.
        # also possibly CAP_GSTREAMER might work better than V4L2 TBD!
        self.cam = cam = cv2.VideoCapture("/dev/camera", cv2.CAP_V4L2)

        wb_auto = False  # we want to avoid constantly changing our white balance
        if wb_auto:
            cam.set(cv2.CAP_PROP_AUTO_WB, 1)  # Turn on/off auto white balance adjustment
        else:
            cam.set(cv2.CAP_PROP_AUTO_WB, 0)
            cam.set(cv2.CAP_PROP_WB_TEMPERATURE, 3222)  # from crude testing in my living room

        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))  # type: ignore
        # we can get a much higher frame rate if we use H264, but opencv doesn't automatically decompress it
        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # the default of 250 is -6 as a signed byte
        # a logitech c920 supports between-2 to -11.  Might need to go lower if bluring still occurs. -8 is definitely
        # sharper at preventing bluring, but a bit too dark in the morning.
        # Must be set _after_ setting width and height
        # cam.set(cv2.CAP_PROP_EXPOSURE, -6)
        exp = int(cam.get(cv2.CAP_PROP_EXPOSURE))

        # FIXME - might need to turn off autofocus if shortening exposures is not enough to make things sharp
        # Possibly also see if frame rate can be changed to 60 fps instead of 30
        # https://pedja.supurovic.net/setting-up-logitech-c920-webcam-for-the-best-video-complete-guide/?lang=lat

        logger.info(
            f"Camera width={ width }, height={height}, exposure={exp}")

        if width != 1920:
            logger.warning("Requested resolution of 1920x1080 not available, problems might occur...")
        # check access
        if (not cam.isOpened() or width == 0):
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
