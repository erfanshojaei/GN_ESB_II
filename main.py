import logging
import time
from process_frames import process_frames
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the IP addresses of the cameras
camera_ips = ['169.254.207.1', '169.254.207.2']

# Define the PLC variable names
run_program = "run_program"
exit_script = "exit_script"

if __name__ == "__main__":
    try:
        # Connect to the OPC UA server
        logging.info("Connecting to the OPC UA server...")
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            exit(1)

        # Check the cameras before proceeding
        logging.info("Checking camera accessibility...")
        camera_status = check_cameras(camera_ips)

        if camera_status:
            logging.info("All cameras are accessible. Proceeding with frame processing...")
            while True:
                if exit_operation(objects, exit_script):
                    logging.info("Exit operation triggered. Closing script.")
                    break  # Gracefully exit the loop
                elif planting_operation(objects, run_program):
                    logging.info("Planting operation is active.")
                    process_frames(camera_ips)
                else:
                    logging.info("Planting operation is not active. Skipping frame processing.")
                
                # Add a small delay to avoid 100% CPU usage
                time.sleep(0.5)
        else:
            logging.error("One or more cameras are not accessible. Exiting the program.")
            exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Cleanup resources (if any)
        logging.info("Cleaning up resources before exiting...")
