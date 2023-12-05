import cv2

class Camera:
    def read_image(self):
        raise NotImplementedError

class SimCamera(Camera):
    def read_image(self):
        return None

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
        width  = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print("Width=", width)
        print("Height=",height)

        #we check if the camera is opened previously or not
        if (cam.isOpened()==False):
            raise ConnectionError("Can't access camera")

    def read_image(self):
        # reading the input using the camera 
        camGood, camImage = self.cam.read() 
    
        # If image will detected without any error,  
        # show result 
        if camGood:
            return camImage
        else:
            raise IOError("Camera read error")