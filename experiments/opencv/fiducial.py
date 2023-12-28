import tempfile

import cv2
import numpy as np
from fpdf import FPDF

dict_name = cv2.aruco.DICT_4X4_50  # 6x6 doesn't seem hugely better based on my testing
dict = cv2.aruco.getPredefinedDictionary(dict_name)
detect_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dict, detect_params)


def make_marker(marker_id=1, marker_size=64) -> np.ndarray:
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

    # Generate the marker image
    tag = np.zeros((marker_size, marker_size, 1), dtype="uint8")
    marker_image = cv2.aruco.generateImageMarker(dict, marker_id, marker_size, tag, 1)

    return marker_image


def render_to_png(image: np.ndarray) -> str:
    """
    Renders an OpenCV image to a temporary PNG file.

    Args:
        image (np.ndarray): The input image.

    Returns:
        str: The path to the temporary PNG file.
    """
    # Create a temporary file with a .png extension
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=True)

    # Write the image to the temporary file
    cv2.imwrite(temp_file.name, image)

    # Return the path to the temporary file
    return temp_file


def render_to_pdf(image: np.ndarray, output_path="/tmp/test.pdf"):
    """
    Renders an OpenCV image to a full-page PDF output file.

    Args:
        image_path (str): The path to the input image.
        output_path (str): The path to the output PDF file.

    Returns:
        None
    """
    # Create a PDF object
    pdf = FPDF(unit="pt", format=(image.shape[1], image.shape[0]))

    # Add a page to the PDF
    pdf.add_page()

    # Calculate the scaling factor to fit the image within the page (but preserve aspect ratio)
    page_width = pdf.w
    page_height = pdf.h
    image_width = image.shape[1]
    image_height = image.shape[0]
    scaling_factor = min(page_width / image_width, page_height / image_height)

    # Calculate the position of the image on the page
    x = (page_width - image_width * scaling_factor) / 2
    y = (page_height - image_height * scaling_factor) / 2

    # Add the image to the PDF
    with render_to_png(image) as temp_file:
        pdf.image(temp_file.name, x, y, w=image_width * scaling_factor, h=image_height * scaling_factor)

    # Save the PDF to the output path
    pdf.output(output_path)


def draw_markers_on_paper():
    """
    Draws ArUco markers in the four corners of a page of paper.

    Returns:
        None
    """
    # Define the marker IDs for the four corners
    marker_ids = [0, 1, 2, 3]

    # Define the size of the markers
    marker_size = 256  # 64 is too small for the camera to detect reliably, 128 was better but still not great

    # Define the size of the paper - assume 8.5" x 11"
    pix_height = 1024
    paper_size = (int(pix_height * 8.5 / 11), pix_height)

    # Create a blank white paper image
    paper = np.ones((paper_size[1], paper_size[0], 3), dtype=np.uint8) * 255

    inset = 16

    # Draw markers in the four corners of the paper
    for i, marker_id in enumerate(marker_ids):
        # Define the corner positions as an array
        corner_positions = [(inset, inset),
                            (paper_size[0] - marker_size - inset, inset),
                            (inset, paper_size[1] - marker_size - inset),
                            (paper_size[0] - marker_size - inset, paper_size[1] - marker_size - inset)]

        # Calculate the position of the marker in each corner
        for i, marker_id in enumerate(marker_ids):
            x, y = corner_positions[i]

            # Generate the marker image
            marker_image = make_marker(marker_id, marker_size)

            # Paste the marker image onto the paper
            paper[y:y + marker_size, x:x + marker_size] = marker_image

    # Display the paper with markers
    # cv2.imshow("paper", paper)
    render_to_pdf(paper)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def find_markers(image: np.ndarray) -> np.ndarray:
    """
    Finds ArUco markers in an OpenCV image and draws bounding boxes around them.

    Args:
        image (np.ndarray): The input OpenCV image.

    Returns:
        np.ndarray: The output image with bounding boxes drawn around the ArUco markers.
    """
    # Convert the image to grayscale - doesn't seem to be needed
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    corners, ids, _ = detector.detectMarkers(image)

    # Draw bounding boxes around the markers
    output_image = image.copy()
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(output_image, corners, ids, (0, 255, 0))

    return output_image


# Example usage
# input_image = cv2.imread("input_image.jpg")
# output_image = find_aruco_markers(input_image)
# cv2.imshow("output", output_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


def draw_marker(marker_id=1):
    """
    Draws an ArUco marker to an OpenCV window.

    Args:
        window_name (str): The name of the OpenCV window.
        marker_id (int): The ID of the ArUco marker.
        marker_size (int): The size of the ArUco marker.

    Returns:
        None
    """
    image = make_marker(marker_id)

    # Create a black image with the same size as the marker image
    # image = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2BGR)

    # Display the marker image in the OpenCV window
    cv2.imshow("aruco", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def show_camera_feed():
    # Open the camera
    cap = cv2.VideoCapture(3)
    exp = cap.get(cv2.CAP_PROP_EXPOSURE)  # my crummy cheap webcam defaults to 157, but that setting shows banding with LED lights
    fps = exp = cap.get(cv2.CAP_PROP_FPS)
    print(f"Default exposure: {exp}, fps: {fps}")
    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    # cap.set(cv2.CAP_PROP_EXPOSURE, 200)
    exp = cap.get(cv2.CAP_PROP_EXPOSURE)
    print(f"Exposure: {exp}")

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        marked = find_markers(frame)

        # Display the frame in a window
        cv2.imshow("Camera Feed", marked)

        # Wait for a key press
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()


# Call the function to start showing the camera feed
draw_markers_on_paper()
show_camera_feed()
