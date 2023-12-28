import cv2
import numpy as np


def count_red_circles(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the red color range
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    # Combine the masks
    mask = mask1

    # Apply a series of morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours of the red circles
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Count the number of red circular objects
    bounding_boxes = []  # List to store bounding boxes

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity > 0.8 and area > 100:  # Adjust circularity and area thresholds as needed
            x, y, w, h = cv2.boundingRect(contour)  # Get the bounding box coordinates
            bounding_boxes.append((x, y, w, h))  # Add the bounding box to the list

    return bounding_boxes
