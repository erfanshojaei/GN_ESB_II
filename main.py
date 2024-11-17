import logging
from process_frames import process_frames
from check_cameras import check_cameras  # Import the check_cameras function
from opcua_connection import connectOPCUA  # Import the connectOPCUA function from the new file

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the IP addresses of the cameras
camera_ips = ['169.254.207.1', '169.254.207.2']

if __name__ == "__main__":
    try:
        # Connect to the OPC UA server
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            exit(1)  # Exit if OPC UA connection fails

        # Check the cameras before proceeding
        camera_status = check_cameras(camera_ips)

        if camera_status:
            logging.info("All cameras are accessible. Proceeding with frame processing...")
            process_frames(camera_ips)
        else:
            logging.error("One or more cameras are not accessible. Exiting the program.")
            exit(1)  # Exit if cameras are not accessible

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)  # Exit on any other unexpected errors
