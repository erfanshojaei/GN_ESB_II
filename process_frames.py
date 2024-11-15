import cv2
import os
import numpy as np
from datetime import datetime
from camera_package.binary_image_processing import process_image
from camera_package.crop_frame import crop_frame
from camera_package.centroid import process_cnt
from camera import grab_frame_from_camera

def process_frames():
    # Define paths
    usb_path = 'E:\\'  # Adjust path for your USB device
    local_output_path = 'camera_outputs'  # Local folder for saving frames
    run_count_file = os.path.join(usb_path, 'run_count.txt')

    # Check if the USB device is connected
    if not os.path.exists(usb_path):
        print("WARNING: USB is not connected. The program will continue using local storage.")
        usb_connected = False
    else:
        usb_connected = True

    # Create the local output directory if it does not exist
    if not os.path.exists(local_output_path):
        os.makedirs(local_output_path)
    else:
        # Clear the local output folder before saving new frames
        for file_name in os.listdir(local_output_path):
            file_path = os.path.join(local_output_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Read the current run count from a file (or initialize if it doesn't exist)
    if usb_connected and os.path.exists(run_count_file):
        with open(run_count_file, 'r') as file:
            run_count = int(file.read())  # Read the current run count
    else:
        run_count = 0  # Initialize run count to 0 if the file does not exist or USB is not connected

    # Increment the run count
    run_count += 1

    # Save the updated run count back to the file if USB is connected
    if usb_connected:
        with open(run_count_file, 'w') as file:
            file.write(str(run_count))

    # Pair of cameras used for detecting one tree
    camera_pair = ('169.254.207.1', '169.254.207.2')

    # Define crop coordinates for each camera (example coordinates)
    crop_coordinates = {
        '169.254.207.1': (900, 500, 750, 1000),  # x, y, width, height for Camera 1
        '169.254.207.2': (700, 500, 750, 1000),  # x, y, width, height for Camera 2
    }

    # Define ROI coordinates for each camera (example coordinates)
    roi_coordinates = {
        '169.254.207.1': (200, 0, 100, 1000),  # x, y, width, height for ROI Camera 1
        '169.254.207.2': (200, 0, 100, 1000),  # x, y, width, height for ROI Camera 2
    }

    # Initialize tree vertical status
    tree_is_vertical = {ip: True for ip in camera_pair}

    # Process each camera in the pair
    for ip in camera_pair:
        try:
            # Grab frame from the camera
            frame = grab_frame_from_camera(ip)

            # Add a short delay to ensure the frame is displayed properly
            cv2.waitKey(1)

            # Check if the frame is valid
            if frame is not None and frame.size > 0:
                print(f"Original frame size from camera {ip}: {frame.shape[0]} x {frame.shape[1]}")

                # Convert the grayscale frame to color (BGR) for drawing purposes
                color_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                # Resize the original frame for display (resize width to 640px, maintain aspect ratio)
                height, width = color_frame.shape[:2]
                new_width = 640
                new_height = int((new_width / width) * height)
                resized_frame = cv2.resize(color_frame, (new_width, new_height))

                # Save the frames with the camera IP, run count, and window name to USB and local folders
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

                # Create file paths for saving frames on USB and local folder with run_count
                original_file_path_usb = os.path.join(usb_path, f"original_{ip}_{run_count}_{timestamp}.png")
                cropped_file_path_usb = os.path.join(usb_path, f"cropped_{ip}_{run_count}_{timestamp}.png")
                binary_file_path_usb = os.path.join(usb_path, f"binary_{ip}_{run_count}_{timestamp}.png")

                original_file_path_local = os.path.join(local_output_path, f"original_{ip}_{run_count}.png")
                cropped_file_path_local = os.path.join(local_output_path, f"cropped_{ip}_{run_count}.png")
                binary_file_path_local = os.path.join(local_output_path, f"binary_{ip}_{run_count}.png")

                # Save original frame
                if usb_connected:
                    cv2.imwrite(original_file_path_usb, frame)
                cv2.imwrite(original_file_path_local, frame)

                # Crop the frame
                coordinates = crop_coordinates[ip]
                cropped_frame = crop_frame(frame, coordinates)

                # Save cropped frame
                if usb_connected:
                    cv2.imwrite(cropped_file_path_usb, cropped_frame)
                cv2.imwrite(cropped_file_path_local, cropped_frame)

                # Convert cropped frame to binary and apply morphological opening
                opened_binary_image = process_image(cropped_frame)

                # Convert opened binary image to BGR for drawing
                opened_binary_image_colored = cv2.cvtColor(opened_binary_image, cv2.COLOR_GRAY2BGR)

                # Calculate the centroid
                centroid = process_cnt(opened_binary_image)

                # Get the ROI coordinates
                roi_coords = roi_coordinates[ip]
                x, y, w, h = roi_coords

                # Draw the ROI as a rectangle on the binary image
                cv2.rectangle(opened_binary_image_colored, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw the centroid as a circle on the binary image
                if centroid is not None:
                    cx, cy = centroid
                    cv2.circle(opened_binary_image_colored, (cx, cy), 5, (0, 0, 255), -1)

                # Check if the centroid is within the ROI for the current camera
                if not (x <= centroid[0] <= x + w and y <= centroid[1] <= y + h):
                    tree_is_vertical[ip] = False

                # Save the final binary image with ROI and centroid to local folder
                final_binary_image_path_local = os.path.join(local_output_path, f"final_binary_{ip}_{run_count}.png")
                cv2.imwrite(final_binary_image_path_local, opened_binary_image_colored)

                # Display the processed frames
                cv2.imshow(f"Original Frame from {ip}", resized_frame)
                cv2.imshow(f"Cropped Frame from {ip}", cropped_frame)
                cv2.imshow(f"Binary Frame from {ip}", opened_binary_image_colored)

            else:
                print(f"Invalid frame from camera {ip}: {frame}")

        except Exception as e:
            print(f"Error with camera {ip}: {e}")

    # After processing both cameras, check if the tree is vertical
    for ip in camera_pair:
        if not tree_is_vertical[ip]:
            print(f"The tree from camera {ip} is not planted vertically.")

    # If neither camera detects the tree as not vertical, print the overall status
    if all(tree_is_vertical[ip] for ip in camera_pair):
        print("The tree is planted vertically.")
    else:
        print("The tree is NOT planted vertically.")

    # Wait indefinitely until a key is pressed
    cv2.waitKey(0)

    # Close all OpenCV windows
    cv2.destroyAllWindows()