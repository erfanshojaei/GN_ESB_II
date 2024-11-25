import logging
import time
import os
import yaml

from process_frames import process_frames
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation
from session_utils import getSessionNumber  # Importing the function
from set_vertical import set_vertical  # Importing the set_vertical function
from set_non_vertical import set_non_vertical  # Importing the set_non_vertical function

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC variable path (this is the base path used to access PLC variables)
plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]

# Load configuration from YAML file
def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        exit(1)

# Main function
if __name__ == "__main__":
    # Load configuration
    config = load_config()

    # Extract values from configuration
    camera_ips = config["camera_ips"]
    run_program = config["plc_variables"]["run_program"]
    exit_script = config["plc_variables"]["exit_script"]
    session_number_key = config["plc_variables"]["session_number"]
    tree_vertical = config["plc_variables"]["tree_vertical"]  # Now loaded from the config
    tree_non_vertical = config["plc_variables"]["tree_non_vertical"]  # Assuming added in config.yaml
    MAX_SESSION_NUMBER = config["max_session_number"]

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
                # Check for exit condition
                if exit_operation(objects, exit_script):
                    logging.info("Exit operation triggered. Closing script.")
                    break  # Gracefully exit the loop

                # Retrieve the current session number
                session_value = getSessionNumber(objects)
                if session_value is None:
                    logging.warning("Session number retrieval failed. Skipping iteration.")
                    continue

                # Process frames if planting operation is active and session number has changed
                if planting_operation(objects, run_program) and lastSession != session_value:
                    if session_value == MAX_SESSION_NUMBER:
                        lastSession = 0
                    else:
                        lastSession = session_value

                    logging.info("Planting operation is active.")

                    # Process frames and capture the returned status
                    tree_status = process_frames(camera_ips)
                    logging.info(tree_status)  # Log the status returned from process_frames

                    # Check if tree is planted vertically and set the corresponding PLC variable
                    if tree_status == "The tree is planted vertically.":
                        set_vertical(objects, plcVarPath, tree_vertical)
                    elif tree_status == "The tree is not planted vertically.":
                        set_non_vertical(objects, plcVarPath, tree_non_vertical)
                    else:
                        logging.info("Unknown situation.")

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
