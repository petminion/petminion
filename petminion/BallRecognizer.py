import logging
from tkinter import Image
from typing import Optional

import cv2
import numpy as np

from .Recognizer import ImageDetection, Recognizer

logger = logging.getLogger()


h = 10  # Parameter regulating filter strength for luminance component.
# Bigger h value perfectly removes noise but also removes image details, smaller h value preserves details but also preserves some noise
# 10 seems to work well
hColor = 10  # The same as h but for color components. For most images value equals 10 will be enough to remove colored noise and do not distort colors


class NoiseEliminator:
    def __init__(self):
        self.old_frames = []

    def filter_frame(self, frame):
        # if resolution changes we have to reset the old frames
        if len(self.old_frames) and self.old_frames[0].shape != frame.shape:
            self.old_frames = []

        if len(self.old_frames) > 3:
            self.old_frames.pop(0)

        if len(self.old_frames) < 3:
            return frame  # Haven't read enough frames to do real deoising

        time_window_size = len(self.old_frames) - 1
        time_window_size = time_window_size // 2 * 2 + 1  # Round down to the next lower odd number (window sizes must be odd)
        middle_index = time_window_size // 2
        frame = cv2.fastNlMeansDenoisingColoredMulti(self.old_frames, middle_index, time_window_size, None, h, hColor, 7, 21)
        return frame


# Define the lower and upper bounds for the red color - this needs to be done in two sections because red 'straddles' the 0/180 line
center_hue = 80  # green
hue_width = 15
# center_hue = 0  # red
# hue_width = 10

s_min = 190
s_max = 255
v_min = 0
v_width = 180

denoise = NoiseEliminator()


def find_balls(frame: np.ndarray) -> list[ImageDetection]:
    # Easy single frame denoising
    # if this isn't enough make a class that keeps the last 5 frames and uses https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html
    # multiframe.
    # frame = cv2.fastNlMeansDenoisingColored(frame, None, h, hColor, 7, 21)
    frame = denoise.filter_frame(frame)

    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower = np.array([center_hue, s_min, v_min])
    upper = np.array([center_hue + hue_width, s_max, v_min + v_width])
    mask = cv2.inRange(hsv, lower, upper)

    if center_hue < 10:  # red straddles the 0/180 line, so we need to handle it differently
        lower_red = np.array([175 - center_hue, s_min, 50])
        upper_red = np.array([180 - center_hue, s_max, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)

        # Combine the masks
        mask = cv2.bitwise_or(mask, mask2)

    # Apply a series of morphological operations to remove noise (not needed now that we are using denoising above)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours of the red circles
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the bounding boxes
    bounding_boxes = []

    # print(f"Found {len(contours)} contours")

    # fixme, keep the last N frames of bounding boxes.  only count balls that were in most of the last n frames.

    # Iterate over the contours
    for contour in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(contour)

        x, y, w, h = cv2.boundingRect(contour)

        # Draw the contour on the frame with red lines
        # cv2.drawContours(frame, [contour], 0, (0, 0, 255), 2)

        # If the % filled is above a certain threshold, consider it as a ball
        fill_ratio = 0.5
        filled = area > w * h * fill_ratio
        squareish = abs((w / h) - 1.0) < 0.4  # if close to zero, it's a square
        big_enough = w > 8
        if filled and squareish and big_enough:

            # Add the bounding box to the list
            bounding_boxes.append(ImageDetection("ball", 1.0, x, y, x + w, y + h))

    # Return the bounding boxes of the balls
    return bounding_boxes


class BallRecognizer(Recognizer):
    """
    Recognize colored balls in the image.

    Inherits from Recognizer class.

    Attributes:
        detector: An instance of ObjectDetection class for object detection.
        classifier: An instance of ImageClassification class for image classification.

    Methods:
        do_detection: Performs object detection on an image and returns annotated image and a list of ImageDetection objects.
        do_classification: Performs image classification on an image and returns a list of ImageDetection objects.
    """

    def __init__(self):
        super().__init__()

    def do_detection(self, image: np.ndarray) -> list[ImageDetection]:
        """
        Performs object detection on the given image.

        Args:
            image: A numpy array representing the image.

        Returns:
            A tuple containing the annotated image (or None if no detections found) and a list of ImageDetection objects.
        """
        # too verbose
        # logger.debug("Doing detection...")
        d = find_balls(image)

        return d
