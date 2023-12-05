import os
from imageai.Classification import ImageClassification
from imageai.Detection import ObjectDetection

# importing OpenCV library 
import cv2
import numpy as np

# execution_path = os.getcwd()
execution_path = "/home/kevinh/development/crowbot/experiments/imageai"

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath( os.path.join(execution_path , "yolov3.pt"))
detector.loadModel()

prediction = ImageClassification()
prediction.setModelTypeAsResNet50()
prediction.setModelPath(os.path.join(execution_path, "resnet50-19c8e357.pth"))
prediction.loadModel()

# initialize the camera 
# If you have multiple camera connected with  
# current device, assign a value in cam_port  
# variable according to that 
cam_port = 0
cam = cv2.VideoCapture(cam_port) 

# cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('U','Y','V','Y'))
# cam.set(cv2.CAP_PROP_FRAME_WIDTH,640)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
width  = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Width=", width)
print("Height=",height)

#we check if the camera is opened previously or not
if (cam.isOpened()==False):
    print("Error reading video file")

shown = False
camGood = True
while camGood:
    # reading the input using the camera 
    camGood, camImage = cam.read() 
  
    # If image will detected without any error,  
    # show result 
    if camGood: 
    
        # No longer needed: convert image into RGB order (instead of the BGR used by default in opencv)
        # image = cv2.cvtColor(camImage, cv2.COLOR_BGR2RGB)
        image = camImage

        # Not needed
        # np.asarray(Image.open('test.jpg'), dtype='float64')

        # saving image in local storage 
        # cv2.imwrite("live.png", image) 

        # FIXME: use output_type = "array" to supress writing the output image (which is slow)
        # annotated_file = os.path.join(execution_path , "live-out.png")
        annotated, detections = detector.detectObjectsFromImage(input_image=image, 
                                                    minimum_percentage_probability=30,
                                                    output_type="array")

        # showing result, it take frame name and image  
        # output 
        # annotated = cv2.imread(annotated_file)
        cv2.imshow("Camview", annotated) 
        cv2.waitKey(1) # FIXME - need to wait at least briefly otherwise debug window doesn't show 

        os.system('clear')
        
        print("Detections")   
        for eachObject in detections:
            print("  ", eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )

        print("Classifications")
        predictions, probabilities = prediction.classifyImage(image, result_count=5 )
        for eachPrediction, eachProbability in zip(predictions, probabilities):
            print("  ", eachPrediction , " : " , eachProbability)
    
# If keyboard interrupt occurs, destroy image  
# window 

cv2.destroyWindow("Camview") 
  

