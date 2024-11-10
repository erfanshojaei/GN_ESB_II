import cv2
import numpy as np

def process_cnt(binary_image):
    """Calculate the centroid of all white pixels in the opened binary image."""
    if binary_image is None:
        raise ValueError("Invalid binary image provided for processing. The image cannot be None.")

    # Calculate moments of the binary image
    M = cv2.moments(binary_image)

    # Calculate centroid
    if M['m00'] != 0:  # Prevent division by zero
        cX = int(M['m10'] / M['m00'])
        cY = int(M['m01'] / M['m00'])
        centroid = (cX, cY)  # Centroid coordinates
    else:
        centroid = (0, 0)  # Default centroid if no white pixels are found

    return centroid  # Return the centroid
