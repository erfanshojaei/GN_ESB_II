from process_frames import process_frames
from check_cameras import check_cameras  # Import the check_cameras function

# Define the IP addresses of the cameras
camera_ips = ['169.254.207.1', '169.254.207.2']

if __name__ == "__main__":
    # Check the cameras before proceeding
    camera_status = check_cameras(camera_ips)

    # If all cameras are accessible, call the process_frames function
    if camera_status:
        print("All cameras are accessible. Proceeding with frame processing...")
        process_frames(camera_ips)
    else:
        print("One or more cameras are not accessible. Exiting the program.")
