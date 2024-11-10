import cv2
import numpy as np

# Load the image in color
image = cv2.imread('f1.jpg')

# Check if the image is loaded successfully
if image is None:
    print("Error: Unable to load image.")
else:
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert the grayscale image
    inverted_gray_image = cv2.bitwise_not(gray_image)

    # Create binary image by thresholding (for dark objects)
    _, binary_image = cv2.threshold(inverted_gray_image, 128, 255, cv2.THRESH_BINARY)

    # Define ROI coordinates (x, y, width, height)
    roi_x, roi_y, roi_width, roi_height = 200, 10, 1000, 700

    # Extract the ROI region
    roi = binary_image[roi_y:roi_y + roi_height, roi_x:roi_x + roi_width]

    # Apply morphological opening to remove small objects
    kernel_size = 1  # Initial kernel size
    iterations = 0  # Initial number of iterations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    roi_opened = cv2.morphologyEx(roi, cv2.MORPH_OPEN, kernel, iterations=iterations)

    # Find contours within the ROI after morphological opening
    contours, _ = cv2.findContours(roi_opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables to store the largest contour and its area
    max_contour = None
    max_contour_area = 0

    # Find the contour with the largest area
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_contour_area:
            max_contour_area = area
            max_contour = contour

    # Create a blank image with the same size as the original image
    ellipse_image = np.zeros_like(image)

    # Draw the convex hull of the largest contour
    if max_contour is not None:
        convex_hull = cv2.convexHull(max_contour)
        cv2.drawContours(ellipse_image, [convex_hull], -1, (255), thickness=cv2.FILLED)

        # Fit an ellipse to the convex hull
        if len(convex_hull) >= 5:
            ellipse = cv2.fitEllipse(convex_hull)
            cv2.ellipse(ellipse_image, ellipse, (0, 255, 255), 2)  # Change color to yellow

            # Draw major and minor axes
            center, axes, angle = ellipse
            major_axis_length = int(axes[1] / 2)
            minor_axis_length = int(axes[0] / 2)
            major_axis_endpoint1 = (int(center[0] + major_axis_length * np.cos(np.radians(angle))),
                                    int(center[1] + major_axis_length * np.sin(np.radians(angle))))
            major_axis_endpoint2 = (int(center[0] - major_axis_length * np.cos(np.radians(angle))),
                                    int(center[1] - major_axis_length * np.sin(np.radians(angle))))
            minor_axis_endpoint1 = (int(center[0] + minor_axis_length * np.cos(np.radians(angle + 90))),
                                    int(center[1] + minor_axis_length * np.sin(np.radians(angle + 90))))
            minor_axis_endpoint2 = (int(center[0] - minor_axis_length * np.cos(np.radians(angle + 90))),
                                    int(center[1] - minor_axis_length * np.sin(np.radians(angle + 90))))
            cv2.line(ellipse_image, major_axis_endpoint1, major_axis_endpoint2, (0, 0, 255), 2)
            cv2.line(ellipse_image, minor_axis_endpoint1, minor_axis_endpoint2, (0, 0, 255), 2)

            # Calculate the angle of the minor axis
            minor_axis_angle = angle - 90 if angle >= 90 else angle + 90

            # Calculate the position for the angle text
            text_position = (400, 300)  # Adjust these coordinates as needed

            # Display the angle text
            cv2.putText(ellipse_image, f"Angle: {minor_axis_angle:.2f}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Create a copy of the binary image with the ROI
    image_with_roi = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(image_with_roi, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)

    # Display the original image, binary image with green ROI, and convex hull image with fitted ellipse
    cv2.imshow('Original Image', image)
    cv2.imshow('Binary Image with Green ROI', image_with_roi)
    cv2.imshow('Binary Image with Morphological Opening in ROI', roi_opened)
    cv2.imshow('Convex Hull of Binary Image with Morphological Opening in ROI with Fitted Yellow Ellipse', ellipse_image)

    # Wait for a key press and close all windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()