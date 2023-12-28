import cv2
import numpy as np

dict_name = cv2.aruco.DICT_4X4_50
dict = cv2.aruco.getPredefinedDictionary(dict_name)


def draw_aruco_marker(marker_id=1):
    """
    Draws an ArUco marker to an OpenCV window.

    Args:
        window_name (str): The name of the OpenCV window.
        marker_id (int): The ID of the ArUco marker.
        marker_size (int): The size of the ArUco marker.

    Returns:
        None
    """
    # Based on this article: https://pyimagesearch.com/2020/12/14/generating-aruco-markers-with-opencv-and-python/
    # Create an ArUco dictionary

    marker_size = 256

    # Generate the marker image
    tag = np.zeros((marker_size, marker_size, 1), dtype="uint8")
    marker_image = cv2.aruco.generateImageMarker(dict, marker_id, marker_size, tag, 1)

    # Create a black image with the same size as the marker image
    image = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2BGR)

    # Display the marker image in the OpenCV window
    cv2.imshow("aruco", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


draw_aruco_marker()
