import cv2
import logging
import os

logger = logging.getLogger()


class CameraDisconnectedError(IOError):
    pass


class Camera:
    def read_image(self):
        raise NotImplementedError


class SimCamera(Camera):
    def __init__(self, repeat_forever: bool = False):
        self.img_dir = '/home/kevinh/development/petminion/tests/image'
        self.filenames = list(filter(lambda x: x.endswith(
            ".jpg"), os.listdir(self.img_dir)))
        self.next_name = iter(self.filenames)
        self.repeat_forever = repeat_forever

    def read_image(self):
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


class CV2Camera(Camera):
    def __init__(self):
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

    def read_image(self):
        # reading the input using the camera
        camGood, camImage = self.cam.read()

        # If image will detected without any error,
        # show result
        if camGood:
            return camImage
        else:
            raise CameraDisconnectedError("Camera read error")
