import cv2
import os
import numpy as np
from datetime import datetime
from camera_package.binary_image_processing import process_image
from camera_package.crop_frame import crop_frame
from camera_package.centroid import process_cnt
from camera import grab_frame_from_camera

def process_frames(camera_ips):
    # Define paths
    usb_path = 'E:\\'  # Adjust path for your USB device
    local_output_path = 'camera_outputs'  # Local folder for saving frames
    run_count_file = os.path.join(usb_path, 'run_count.txt')  # Save run_count in the USB directory

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

    # Initialize tree vertical status
    tree_is_vertical = {ip: True for ip in camera_ips}

    # Process each camera in the pair
    for ip in camera_ips:
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

                # Create file paths for saving frames on USB and local folder with run_count and current_date
                original_file_path_local = os.path.join(local_output_path, f"original_{ip}.png")
                cropped_file_path_local = os.path.join(local_output_path, f"cropped_{ip}.png")
                binary_file_path_local = os.path.join(local_output_path, f"binary_{ip}.png")
                final_binary_file_path_local = os.path.join(local_output_path, f"final_binary_{ip}.png")

                # Use run_count and current_date in filenames for saving images to USB to prevent overwriting
                current_date = datetime.now().strftime('%Y-%m-%d')
                original_file_path_usb = os.path.join(usb_path, f"original_{current_date}_{ip}_{run_count}.png")
                cropped_file_path_usb = os.path.join(usb_path, f"cropped_{current_date}_{ip}_{run_count}.png")
                binary_file_path_usb = os.path.join(usb_path, f"binary_{current_date}_{ip}_{run_count}.png")
                final_binary_file_path_usb = os.path.join(usb_path, f"final_binary_{current_date}_{ip}_{run_count}.png")

                # Save original frame both locally and on USB with run_count and current_date
                cv2.imwrite(original_file_path_local, frame)
                if usb_connected:
                    cv2.imwrite(original_file_path_usb, frame)

                # Save resized original frame for display
                cv2.imshow(f"Resized Original Frame {ip}", resized_frame)

                # Crop the frame
                coordinates = crop_coordinates[ip]
                cropped_frame = crop_frame(frame, coordinates)

                # Save cropped frame both locally and on USB with run_count and current_date
                cv2.imwrite(cropped_file_path_local, cropped_frame)
                if usb_connected:
                    cv2.imwrite(cropped_file_path_usb, cropped_frame)

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

                # Save the final binary image with ROI and centroid to the local folder and USB with run_count and current_date
                cv2.imwrite(final_binary_file_path_local, opened_binary_image_colored)
                if usb_connected:
                    cv2.imwrite(final_binary_file_path_usb, opened_binary_image_colored)

                # Display the processed frame
                cv2.imshow(f"Cropped Frame {ip}", cropped_frame)
                cv2.imshow(f"Binary Frame with Centroid & ROI {ip}", opened_binary_image_colored)

        except Exception as e:
            print(f"Error processing frame for camera {ip}: {e}")

    # Print the vertical status of the tree after checking both cameras
    if all(tree_is_vertical.values()):
        print("The tree is planted vertically.")
    else:
        print("The tree is not planted vertically.")

   # cv2.waitKey(0)  # Wait for a key press to close the OpenCV windows
   # cv2.destroyAllWindows()
