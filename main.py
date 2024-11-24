# main.py

import logging
import time
from process_frames import process_frames
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation
from session_utils import getSessionNumber  # Importing the function

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the IP addresses of the cameras
camera_ips = ['169.254.207.1', '169.254.207.2']

# Define the PLC variable names
run_program = "run_program"
exit_script = "exit_script"
sessionNumber = "sessionNumber"

MAX_SESSION_NUMBER = 5

if __name__ == "__main__":
    try:
        # Connect to the OPC UA server
        logging.info("Connecting to the OPC UA server...")
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            exit(1)

        # Initialize session number
        lastSession = getSessionNumber(objects)
        if lastSession is None:
            logging.error("Failed to retrieve initial session number. Exiting program.")
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

                session_value = getSessionNumber(objects)
                if session_value is None:
                    logging.warning("Session number retrieval failed. Skipping iteration.")
                    continue

                if planting_operation(objects, run_program) and lastSession != session_value:
                    if session_value == MAX_SESSION_NUMBER:
                        lastSession = 0
                    else:
                        lastSession = session_value

                    logging.info("Planting operation is active.")
                    process_frames(camera_ips)
                else:
                    logging.info("Planting operation is not active. Skipping frame processing.")

                # Add a small delay to avoid 100% CPU usage
                time.sleep(3)
        else:
            logging.error("One or more cameras are not accessible. Exiting the program.")
            exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Cleanup resources (if any)
        logging.info("Cleaning up resources before exiting...")
