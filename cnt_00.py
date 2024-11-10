import cv2
import numpy as np

# Load the image in color
image = cv2.imread('f1.jpg')

# Check if the image is loaded successfully
if image is None:
    print("Error: Unable to load image.")
    exit(1)  # Exit if the image cannot be loaded

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Invert the grayscale image
inverted_gray_image = cv2.bitwise_not(gray_image)

# Create binary image by thresholding (for dark objects)
_, binary_image = cv2.threshold(inverted_gray_image, 128, 255, cv2.THRESH_BINARY)

# Define ROI coordinates (x, y, width, height)
roi_x, roi_y, roi_width, roi_height = 360, 340, 140, 70

# Extract the ROI region
roi = binary_image[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

# Apply morphological opening to remove small objects
kernel_size = 3  # Example kernel size
iterations = 1  # Example number of iterations
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
roi_opened = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel, iterations=iterations)

# Update the binary image with the processed ROI
processed_image = binary_image.copy()
processed_image[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width] = roi_opened

# Calculate moments of the processed binary image
moments = cv2.moments(processed_image)

# Calculate the center of mass (centroid)
if moments['m00'] != 0:
    centroid_x = int(moments['m10'] / moments['m00'])
    centroid_y = int(moments['m01'] / moments['m00'])
else:
    centroid_x, centroid_y = 0, 0

# Draw a green rectangle around the ROI on the original image for visualization
cv2.rectangle(image, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

# Convert binary images to BGR so we can draw colored rectangles and circles on them
binary_image_with_roi = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
processed_image_with_roi = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)

# Draw a green rectangle around the ROI on the binary image for visualization
cv2.rectangle(binary_image_with_roi, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

# Draw a green rectangle around the ROI on the processed binary image for visualization
cv2.rectangle(processed_image_with_roi, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

# Draw the centroid on all images
cv2.circle(image, (centroid_x, centroid_y), 10, (0, 0, 255), -1)
cv2.circle(binary_image_with_roi, (centroid_x, centroid_y), 10, (0, 0, 255), -1)
cv2.circle(processed_image_with_roi, (centroid_x, centroid_y), 10, (0, 0, 255), -1)

# Check if the centroid is within the ROI and classify
if (roi_x <= centroid_x <= roi_x + roi_width) and (roi_y <= centroid_y <= roi_y + roi_height):
    classification = "The tree is planted vertically"
else:
    classification = "The tree is NOT planted vertically"

# Print the classification result
print(classification)

# Display the original image, binary image, and processed binary image
cv2.imshow('Original Image', image)
cv2.imshow('Binary Image', binary_image_with_roi)
cv2.imshow('Processed Binary Image', processed_image_with_roi)

# Wait for a key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
