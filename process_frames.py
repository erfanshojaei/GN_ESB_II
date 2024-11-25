import cv2
import os
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
    tree_is_vertical = {}

    # Process each camera
    for ip in camera_ips:
        try:
            # Grab frame from the camera
            frame = grab_frame_from_camera(ip)

            # Check if the frame is valid
            if frame is not None and frame.size > 0:
                print(f"Original frame size from camera {ip}: {frame.shape[0]} x {frame.shape[1]}")

                # Crop the frame
                coordinates = crop_coordinates[ip]
                cropped_frame = crop_frame(frame, coordinates)

                # Convert cropped frame to binary and apply morphological opening
                opened_binary_image = process_image(cropped_frame)

                # Calculate the centroid
                centroid = process_cnt(opened_binary_image)

                # Convert binary image to color for visualization
                color_binary_image = cv2.cvtColor(opened_binary_image, cv2.COLOR_GRAY2BGR)

                # Overlay the centroid
                if centroid is not None:
                    cv2.circle(color_binary_image, centroid, 5, (0, 0, 255), -1)  # Red dot for centroid
                    print(f"Camera {ip}: Centroid at {centroid}")

                # Overlay the ROI rectangle
                roi_coords = roi_coordinates[ip]
                x, y, w, h = roi_coords
                cv2.rectangle(color_binary_image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle for ROI

                # Check if the centroid is within the ROI for the current camera
                if centroid is not None and (x <= centroid[0] <= x + w and y <= centroid[1] <= y + h):
                    tree_is_vertical[ip] = True
                    print(f"Camera {ip}: Tree is vertical.")
                else:
                    tree_is_vertical[ip] = False
                    print(f"Camera {ip}: Tree is not vertical.")

                # Save frames locally
                original_frame_filename = f"original_frame_{ip.replace('.', '_')}_run{run_count}.png"
                cropped_frame_filename = f"cropped_frame_{ip.replace('.', '_')}_run{run_count}.png"
                binary_frame_filename = f"binary_frame_{ip.replace('.', '_')}_run{run_count}.png"

                original_path = os.path.join(local_output_path, original_frame_filename)
                cropped_path = os.path.join(local_output_path, cropped_frame_filename)
                binary_path = os.path.join(local_output_path, binary_frame_filename)

                cv2.imwrite(original_path, frame)
                cv2.imwrite(cropped_path, cropped_frame)
                cv2.imwrite(binary_path, color_binary_image)

                print(f"Frames saved locally: {original_path}, {cropped_path}, {binary_path}")

                # Save frames to USB if connected
                if usb_connected:
                    usb_original_path = os.path.join(usb_path, original_frame_filename)
                    usb_cropped_path = os.path.join(usb_path, cropped_frame_filename)
                    usb_binary_path = os.path.join(usb_path, binary_frame_filename)

                    cv2.imwrite(usb_original_path, frame)
                    cv2.imwrite(usb_cropped_path, cropped_frame)
                    cv2.imwrite(usb_binary_path, color_binary_image)

                    print(f"Frames saved to USB: {usb_original_path}, {usb_cropped_path}, {usb_binary_path}")

        except Exception as e:
            print(f"Error processing frame for camera {ip}: {e}")
            tree_is_vertical[ip] = False

    # Return the overall status of the tree after checking all cameras
    if all(tree_is_vertical.values()):
        print("The tree is planted vertically.")
        return "The tree is planted vertically."
    else:
        print("The tree is not planted vertically.")
        return "The tree is not planted vertically."
