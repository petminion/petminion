import importlib
from importlib.resources import as_file, files
import cv2
from cv2.typing import MatLike
import imutils
import numpy as np
from imutils.perspective import four_point_transform
from . import resources
import logging

"""
**HEAVILY** based on:

Image White Balancing using CV2 and COlor Correction Cards with ArUCo Markers
Author: https://pyimagesearch.com/2021/02/15/automatic-color-correction-with-opencv-and-python/

Modify Stephan Krol 
G-Mail: Stephan.Krol.83[at]
Website: https://CouchBoss.de

via https://github.com/dazzafact/image_color_correction
"""

logger = logging.getLogger()


def find_color_card(image) -> MatLike:
    # load the ArUCo dictionary, grab the ArUCo parameters, and
    # detect the markers in the input image
    arucoDict = cv2.aruco.DICT_ARUCO_ORIGINAL
    dict = cv2.aruco.getPredefinedDictionary(arucoDict)
    detect_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dict, detect_params)

    (corners, ids, _) = detector.detectMarkers(image)

    if ids is None:
        raise Exception('No markers found')

    # try to extract the coordinates of the color correction card
    # otherwise, we've found the four ArUco markers, so we can
    # continue by flattening the ArUco IDs list
    ids = ids.flatten()

    # extract the top-left marker
    i = np.squeeze(np.where(ids == 923))
    if not i.size:
        raise Exception('Top-left marker not found')
    topLeft = np.squeeze(corners[i])[0]

    # extract the top-right marker
    i = np.squeeze(np.where(ids == 1001))
    if not i.size:
        raise Exception('Top-right marker not found')
    topRight = np.squeeze(corners[i])[1]

    # extract the bottom-right marker
    i = np.squeeze(np.where(ids == 241))
    if not i.size:
        raise Exception('Bottom-right marker not found')
    bottomRight = np.squeeze(corners[i])[2]

    # extract the bottom-left marker
    i = np.squeeze(np.where(ids == 1007))
    if not i.size:
        raise Exception('Bottom-left marker not found')
    bottomLeft = np.squeeze(corners[i])[3]

    # build our list of reference points and apply a perspective
    # transform to obtain a top-down, bird’s-eye view of the color
    # matching card
    cardCoords = np.array([topLeft, topRight,
                           bottomRight, bottomLeft])
    card = four_point_transform(image, cardCoords)
    # return the color matching card to the calling function
    return card


def _match_cumulative_cdf_mod(source: MatLike, template: MatLike):
    """
    Return modified full image array so that the cumulative density function of
    source array matches the cumulative density function of the template.
    """
    src_values, _, src_counts = np.unique(source.ravel(),
                                          return_inverse=True,
                                          return_counts=True)
    tmpl_values, tmpl_counts = np.unique(template.ravel(), return_counts=True)

    # calculate normalized quantiles for each array
    src_quantiles = np.cumsum(src_counts) / source.size
    tmpl_quantiles = np.cumsum(tmpl_counts) / template.size

    interp_a_values = np.interp(src_quantiles, tmpl_quantiles, tmpl_values)

    # Here we compute values which the channel RGB value of full image will be modified to.
    interpb = []
    for i in range(0, 256):
        interpb.append(-1)

    # first compute which values in src image transform to and mark those values.

    for i in range(0, len(interp_a_values)):
        frm = src_values[i]
        to = interp_a_values[i]
        interpb[frm] = to

    # some of the pixel values might not be there in interp_a_values, interpolate those values using their
    # previous and next neighbours
    prev_value = -1
    prev_index = -1
    for i in range(0, 256):
        if interpb[i] == -1:
            next_index = -1
            next_value = -1
            for j in range(i + 1, 256):
                if interpb[j] >= 0:
                    next_value = interpb[j]
                    next_index = j
            if prev_index < 0:
                interpb[i] = (i + 1) * next_value / (next_index + 1)
            elif next_index < 0:
                interpb[i] = prev_value + ((255 - prev_value) * (i - prev_index) / (255 - prev_index))
            else:
                interpb[i] = prev_value + (i - prev_index) * (next_value - prev_value) / (next_index - prev_index)
        else:
            prev_value = interpb[i]
            prev_index = i

    return interpb


def _fix_colors(interpb, full: np.ndarray):
    # finally transform pixel values in full image using interpb interpolation values.
    # FIXME use fast matrix numpy operations to do this instead of loops
    wid = full.shape[1]
    hei = full.shape[0]
    ret2 = np.zeros((hei, wid))
    for i in range(0, hei):
        for j in range(0, wid):
            ret2[i][j] = interpb[full[i][j]]
    return ret2


def match_histograms_mod(inputCard: MatLike, referenceCard: MatLike, fullImage: np.ndarray) -> np.ndarray:
    """
        Return modified full image, by using histogram equalizatin on input and
         reference cards and applying that transformation on fullImage.
    """
    if inputCard.ndim != referenceCard.ndim:
        raise ValueError('Image and reference must have the same number '
                         'of channels.')
    matched = np.empty(fullImage.shape, dtype=fullImage.dtype)
    for channel in range(inputCard.shape[-1]):
        matched_channel = _match_cumulative_cdf_mod(inputCard[..., channel], referenceCard[..., channel],
                                                    fullImage[..., channel])
        matched[..., channel] = matched_channel
    return matched


class ColorCorrector():
    def __init__(self):
        with as_file(files(resources).joinpath("ref-pantone.jpg")) as ref_path:
            self.ref_image = cv2.imread(str(ref_path.absolute()))
            self.ref_card = find_color_card(self.ref_image)

    def look_for_card(self, image: np.ndarray) -> bool:
        """
        Looks for a color card in an image.  If found, uses that to update cur_lighting_card.

        Args:
            image (np.ndarray): The input image.

        Returns:
            true if a color card was found, false otherwise.
        """
        try:
            self.cur_lighting_card = find_color_card(image)
            # FIXME save to file for future use
            return True
        except Exception as e:
            logger.debug(f'No color card found: {e}')
            return False

    def correct_image(self, image: np.ndarray) -> np.ndarray:
        """
        Corrects the colors of an image.

        Args:
            image (np.ndarray): The input image.

        Returns:
            np.ndarray: The corrected image.
        """
        return None
