import cv2
import numpy as np
from camera_package.binary_image_processing import process_image
from camera_package.crop_frame import crop_frame
from camera_package.centroid import process_cnt
from camera import grab_frame_from_camera

# Pair of cameras used for detecting one tree
camera_pair = ('169.254.207.1', '169.254.207.2')

# Define crop coordinates for each camera (example coordinates)
crop_coordinates = {
    '169.254.207.1': (700, 500, 750, 1000),  # x, y, width, height for Camera 1
    '169.254.207.2': (700, 500, 750, 1000),  # x, y, width, height for Camera 2
}

# Define ROI coordinates for each camera (example coordinates)
roi_coordinates = {
    '169.254.207.1': (200, 0, 100, 1000),  # x, y, width, height for ROI Camera 1
    '169.254.207.2': (200, 0, 100, 1000),  # x, y, width, height for ROI Camera 2
}

# Flag to check if the tree is planted vertically (True only if centroids are in ROI for both cameras)
tree_is_vertical = True

for ip in camera_pair:
    try:
        # Grab frame from the camera
        frame = grab_frame_from_camera(ip)

        # Add a short delay to ensure the frame is displayed properly
        cv2.waitKey(1)

        # Check if the frame is valid
        if frame is not None and frame.size > 0:
            print(f"Original frame size from camera {ip}: {frame.shape[0]} x {frame.shape[1]}")

            # Create and display the original frame window
            cv2.namedWindow(f"Original Camera {ip}", cv2.WINDOW_NORMAL)  # Ensure window is movable and resizable
            cv2.imshow(f"Original Camera {ip}", frame)
            cv2.resizeWindow(f"Original Camera {ip}", 800, 600)
            cv2.moveWindow(f"Original Camera {ip}", 100, 100)  # Move to specific position
            cv2.waitKey(1)  # Allow some time for rendering

            # Crop the frame
            coordinates = crop_coordinates[ip]
            cropped_frame = crop_frame(frame, coordinates)

            # Create and display the cropped frame window
            cv2.namedWindow(f"Cropped Frame Camera {ip}", cv2.WINDOW_NORMAL)
            cv2.imshow(f"Cropped Frame Camera {ip}", cropped_frame)
            cv2.resizeWindow(f"Cropped Frame Camera {ip}", 800, 600)
            cv2.moveWindow(f"Cropped Frame Camera {ip}", 400, 100)  # Move to specific position
            cv2.waitKey(1)

            # Convert cropped frame to binary and apply morphological opening
            opened_binary_image = process_image(cropped_frame)

            # Calculate the centroid
            centroid = process_cnt(opened_binary_image)

            # Convert opened binary image to BGR for coloring
            opened_binary_image_colored = cv2.cvtColor(opened_binary_image, cv2.COLOR_GRAY2BGR)

            # Get the ROI coordinates
            roi_coords = roi_coordinates[ip]
            x, y, w, h = roi_coords

            # Draw the ROI rectangle on the opened binary image
            cv2.rectangle(opened_binary_image_colored, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green color for ROI

            # Draw the centroid on the opened binary image in red
            if centroid != (0, 0):
                cv2.circle(opened_binary_image_colored, centroid, 7, (0, 0, 255), -1)  # Red color for centroid

            # Create and display the binary image with ROI and centroid
            cv2.namedWindow(f"Opened Binary Image with ROI Camera {ip}", cv2.WINDOW_NORMAL)
            cv2.imshow(f"Opened Binary Image with ROI Camera {ip}", opened_binary_image_colored)
            cv2.resizeWindow(f"Opened Binary Image with ROI Camera {ip}", 800, 600)
            cv2.moveWindow(f"Opened Binary Image with ROI Camera {ip}", 700, 100)  # Move to specific position
            cv2.waitKey(1)

            # Check if the centroid is within the ROI for the current camera
            if not (x <= centroid[0] <= x + w and y <= centroid[1] <= y + h):
                tree_is_vertical = False

        else:
            print(f"Invalid frame from camera {ip}: {frame}")

    except Exception as e:
        print(f"Error with camera {ip}: {e}")

# After processing both cameras, check if the tree is vertical
if tree_is_vertical:
    print("The tree is planted vertically.")
else:
    print("The tree is not planted vertically.")

# Wait indefinitely until a key is pressed
cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()
