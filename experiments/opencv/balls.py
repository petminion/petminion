
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


# Define the lower and upper bounds for the red color - this needs to be done in two sections because red 'straddles' the 0/180 line
center_hue = 90  # green
hue_width = 15
# center_hue = 0  # red
# hue_width = 10

s_min = 190
s_max = 240
v_min = 0
v_width = 180

denoise = NoiseEliminator()

hsv = None  # global for debugging access


def count_balls(frame: np.ndarray) -> tuple[int, np.ndarray]:
    global hsv

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
        cv2.drawContours(frame, [contour], 0, (0, 0, 255), 2)

        # If the % filled is above a certain threshold, consider it as a ball
        fill_ratio = 0.4
        filled = area > w * h * fill_ratio
        squareish = abs((w / h) - 1.0) < 0.4  # if close to zero, it's a square
        big_enough = w > 8
        if filled and squareish and big_enough:

            # Draw the bounding box on the frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Add the bounding box to the list
            bounding_boxes.append((x, y, w, h))

    # Return the bounding boxes of the balls
    return len(bounding_boxes), frame


def test_balls() -> None:
    # Open the camera
    cap = cv2.VideoCapture("/dev/camera", cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('U', 'Y', 'V', 'Y'))
    # we can get a much higher frame rate if we use H264, but opencv doesn't automatically decompress it
    # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    dest_size = (640, 480)
    wb_auto = False  # we want to avoid constantly changing our white balance
    if wb_auto:
        cap.set(cv2.CAP_PROP_AUTO_WB, 1)  # Turn on/off auto white balance adjustment
    else:
        cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 3222)  # from crude testing in my living room

    window_name = "Camera Feed"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)

    def mouse_callback(event, x, y, flags, param):
        color = hsv[y, x]
        labels['text'] = f"HSV: {color}"

    cv2.setMouseCallback(window_name, mouse_callback)  # type: ignore

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        w = frame.shape[1]  # Set w to the width of the frame
        if (w != 640):
            # Resize the frame to 640x480
            frame = cv2.resize(frame, dest_size, interpolation=cv2.INTER_LANCZOS4)

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        count, frame = count_balls(frame)
        print(f"Found {count} balls")

        # Display the HSV color of the pixel under the cursor
        cv2.putText(frame, labels['text'], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow(window_name, frame)

        # Wait for a key press
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()


# Call the function to start showing the camera feed
test_balls()
