
import time

import cv2
import numpy as np

labels = {'text': 'unset'}

h = 10  # Parameter regulating filter strength for luminance component.
# Bigger h value perfectly removes noise but also removes image details, smaller h value preserves details but also preserves some noise
# 10 seems to work well
hColor = 10  # The same as h but for color components. For most images value equals 10 will be enough to remove colored noise and do not distort colors


class NoiseEliminator:
    def __init__(self):
        self.old_frames = []

    def filter_frame(self, frame):
        self.old_frames.append(frame)
        if len(self.old_frames) > 3:
            self.old_frames.pop(0)

        time_window_size = len(self.old_frames) - 1
        time_window_size = time_window_size // 2 * 2 + 1  # Round down to the next lower odd number (window sizes must be odd)
        middle_index = time_window_size // 2
        frame = cv2.fastNlMeansDenoisingColoredMulti(self.old_frames, middle_index, time_window_size, None, h, hColor, 7, 21)
        return frame


def detect_red_circles():
    global labels

    # Open the camera
    cap = cv2.VideoCapture("/dev/camera")
    denoise = NoiseEliminator()

    window_name = "Camera Feed"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)

    hsv = None

    def mouse_callback(event, x, y, flags, param):
        global labels

        color = hsv[y, x]
        labels['text'] = f"HSV: {color}"

    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Easy single frame denoising
        # if this isn't enough make a class that keeps the last 5 frames and uses https://docs.opencv.org/3.4/d5/d69/tutorial_py_non_local_means.html
        # multiframe.
        # frame = cv2.fastNlMeansDenoisingColored(frame, None, h, hColor, 7, 21)
        frame = denoise.filter_frame(frame)

        # Convert the frame to the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds for the red color - this needs to be done in two sections because red 'straddles' the 0/180 line
        center_hue = 80  # green
        hue_width = 20
        # center_hue = 0  # red
        # hue_width = 10

        v_min = 0
        v_width = 180
        lower = np.array([center_hue, 60, v_min])
        upper = np.array([center_hue + hue_width, 255, v_min + v_width])
        mask = cv2.inRange(hsv, lower, upper)

        if center_hue < 10:  # red straddles the 0/180 line, so we need to handle it differently
            lower_red = np.array([175 - center_hue, 60, 50])
            upper_red = np.array([180 - center_hue, 255, 255])
            mask2 = cv2.inRange(hsv, lower_red, upper_red)

            # Combine the masks
            mask = cv2.bitwise_or(mask, mask2)

        # Apply a series of morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6, 6))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours of the red circles
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize a list to store the bounding boxes
        bounding_boxes = []

        print(f"Found {len(contours)} contours")

        # Iterate over the contours
        for contour in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(contour)

            x, y, w, h = cv2.boundingRect(contour)

            # Draw the contour on the frame with red lines
            cv2.drawContours(frame, [contour], 0, (0, 0, 255), 2)

            # If the % filled is above a certain threshold, consider it as a ball
            fill_ratio = 0.6
            filled = area > w * h * fill_ratio
            squareish = abs((w / h) - 1.0) < 0.3
            big_enough = w > 4
            if filled and squareish and big_enough:

                # Draw the bounding box on the frame
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Add the bounding box to the list
                bounding_boxes.append((x, y, w, h))

        # Display the HSV color of the pixel under the cursor
        cv2.putText(frame, labels['text'], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow(window_name, frame)

        # Wait for a key press
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

    # Return the bounding boxes of the balls
    return bounding_boxes


# Call the function to start showing the camera feed
detect_red_circles()
