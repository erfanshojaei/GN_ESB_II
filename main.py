import cv2
import numpy as np
from camera_package.binary_image_processing import process_image
from camera_package.crop_frame import crop_frame
from camera_package.centroid import process_cnt
from camera import grab_frame_from_camera

def process_tree_detection():
    # Pair of cameras used for detecting one tree
    camera_pair = ['169.254.207.1', '169.254.207.2']

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

    # Flags to track if each camera detects the tree as vertical
    camera_flags = {
        '169.254.207.1': False,
        '169.254.207.2': False
    }

    # Iterate through each camera and process the image
    for ip in camera_pair:
        try:
            # Grab frame from the camera
            frame = grab_frame_from_camera(ip)

            # Check if the frame is valid
            if frame is not None and frame.size > 0:
                print(f"Original frame size from camera {ip}: {frame.shape[0]} x {frame.shape[1]}")

                # Show the original frame
                cv2.namedWindow(f"Original Camera {ip}", cv2.WINDOW_NORMAL)
                cv2.imshow(f"Original Camera {ip}", frame)
                cv2.resizeWindow(f"Original Camera {ip}", 800, 600)
                cv2.moveWindow(f"Original Camera {ip}", 100, 100)
                cv2.waitKey(1)

                # Crop the frame
                coordinates = crop_coordinates[ip]
                cropped_frame = crop_frame(frame, coordinates)

                # Show the cropped frame
                cv2.namedWindow(f"Cropped Frame Camera {ip}", cv2.WINDOW_NORMAL)
                cv2.imshow(f"Cropped Frame Camera {ip}", cropped_frame)
                cv2.resizeWindow(f"Cropped Frame Camera {ip}", 800, 600)
                cv2.moveWindow(f"Cropped Frame Camera {ip}", 400, 100)
                cv2.waitKey(1)

                # Convert cropped frame to binary and apply morphological opening
                opened_binary_image = process_image(cropped_frame)

                # Calculate the centroid
                centroid = process_cnt(opened_binary_image)

                # Convert binary image to BGR for ROI and centroid visualization
                opened_binary_image_colored = cv2.cvtColor(opened_binary_image, cv2.COLOR_GRAY2BGR)

                # Get the ROI coordinates
                roi_coords = roi_coordinates[ip]
                x, y, w, h = roi_coords

                # Draw the ROI rectangle
                cv2.rectangle(opened_binary_image_colored, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw the centroid on the opened binary image
                if centroid != (0, 0):
                    cv2.circle(opened_binary_image_colored, centroid, 7, (0, 0, 255), -1)

                # Show the opened binary image with ROI and centroid
                cv2.namedWindow(f"Opened Binary Image with ROI Camera {ip}", cv2.WINDOW_NORMAL)
                cv2.imshow(f"Opened Binary Image with ROI Camera {ip}", opened_binary_image_colored)
                cv2.resizeWindow(f"Opened Binary Image with ROI Camera {ip}", 800, 600)
                cv2.moveWindow(f"Opened Binary Image with ROI Camera {ip}", 700, 100)
                cv2.waitKey(1)

                # Check if the centroid is within the ROI for the current camera
                if x <= centroid[0] <= x + w and y <= centroid[1] <= y + h:
                    camera_flags[ip] = True
                else:
                    camera_flags[ip] = False

        except Exception as e:
            camera_flags[ip] = False
            print(f"Error with camera {ip}: {e}")

    # Final check to see if the tree is vertical
    if camera_flags['169.254.207.1'] and camera_flags['169.254.207.2']:
        print("The tree is planted vertically.")
    else:
        print("The tree is not planted vertically.")

    # Wait indefinitely until a key is pressed
    cv2.waitKey(0)

    # Close all OpenCV windows
    cv2.destroyAllWindows()

# Only run the program if it is the main module
if __name__ == '__main__':
    process_tree_detection()
