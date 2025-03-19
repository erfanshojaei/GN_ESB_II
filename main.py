import logging
import time
import os
import yaml
import atexit

from process_frames import process_frames
from frame_config import get_frame_config
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation
from session_utils import getSessionNumber
from set_vertical import set_vertical
from set_non_vertical import set_non_vertical
from send_heartbeat import send_heartbeat

# Disable logging from the opcua library (if needed)
logging.getLogger("opcua").setLevel(logging.WARNING)

# Set up logging to capture only your own messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC variable path (this is the base path used to access PLC variables)
plcVarPath = [
    "0:Objects", "2:DeviceSet", "4:CODESYS Control Win V3 x64", 
    "3:Resources", "4:Application", "3:Programs", "4:PLC_PRG", "var"
]

# Load configuration from YAML file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        exit(1)

# Graceful cleanup
def cleanup(objects, python_run):
    """
    Gracefully clean up by setting the appropriate PLC variable value to indicate that the Python program stopped.
    """
    try:
        logging.info("Python program stopped. Updating PLC variable...")

        # Ensure python_run is a valid PLC variable name (it should be a string from the config)
        temp_path = plcVarPath.copy()  # Make a copy of the base path
        temp_path[-1] = f"4:{python_run}"  # Replace last element with the actual variable name

        # Retrieve the OPC UA node for the variable we want to set
        var_node = objects.get_child(temp_path)  # Get the node by using the full path

        if var_node is None:
            logging.error(f"Failed to retrieve PLC variable '{python_run}'. Skipping cleanup.")
            return

        # Set the value of the PLC variable (e.g., setting it to 0)
        var_node.set_value(0)  # Set value to 0 or any value to indicate cleanup status

        logging.info("Cleanup complete. Resources have been cleaned up.")

    except Exception as e:
        logging.error(f"Error during cleanup: {e}")


# Main function
def main():
    # Load configuration
    config = load_config()

    # Extract values from configuration
    camera_ips = config["camera_ips"]
    run_code = config["plc_variables"]["run_code"]  # Change from 'run_program' to 'run_code'
    exit_script = config["plc_variables"]["exit_code"]
    session_number_key = config["plc_variables"]["session_number"]
    tree_vertical = config["plc_variables"]["tree_vertical"]
    tree_non_vertical = config["plc_variables"]["tree_non_vertical"]
    python_heartbeat = config["plc_variables"]["python_heartbeat"]  # Added to use from config
    MAX_SESSION_NUMBER = config["max_session_number"]
    acc_mode = config["plc_variables"]["acc_mode"]  # Added the acc_code from the config

    try:
        # Connect to the OPC UA server
        logging.info("Connecting to the OPC UA server...")
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            exit(1)

        # Register cleanup function for graceful exit
        atexit.register(cleanup, objects, python_heartbeat)

        # Initialize session number
        lastSession = getSessionNumber(objects)
        if lastSession is None:
            logging.error("Failed to retrieve initial session number. Exiting program.")
            exit(1)

        # Check the cameras before proceeding
        logging.info("Checking camera accessibility...")
        camera_status = check_cameras(camera_ips)

        if not camera_status:
            logging.error("One or more cameras are not accessible. Exiting the program.")
            exit(1)

        logging.info("All cameras are accessible. Proceeding with frame processing...")

        # Main loop for frame processing
        while True:
            exit_code = exit_operation(objects)
            if exit_code == 99:
                logging.info("Exit code 99 received. Closing script.")
                break

            # Retrieve the current session number
            session_value = getSessionNumber(objects)
            if session_value is None:
                logging.warning("Session number retrieval failed. Skipping iteration.")
                continue

            # Process frames if planting operation is active and session number has changed
            if planting_operation(objects, run_code) and lastSession != session_value:
                lastSession = session_value if session_value != MAX_SESSION_NUMBER else 0
                logging.info("Planting operation is active.")

                try:
                    # Pass acc_code to get_frame_config
                    frame_config = get_frame_config(objects, acc_mode)
                except Exception as e:
                    logging.error(f"Failed to retrieve frame configuration: {e}")
                    continue

                # Process frames and capture the returned status
                tree_status = process_frames(camera_ips, frame_config)
                logging.info(tree_status)

                # Check if tree is planted vertically and set the corresponding PLC variable
                if tree_status == "The tree is planted vertically.":
                    set_vertical(objects, plcVarPath, tree_vertical)
                elif tree_status == "The tree is not planted vertically.":
                    set_non_vertical(objects, plcVarPath, tree_non_vertical)
                else:
                    logging.info("Unknown situation.")
            else:
                logging.info("Planting operation is not active. Skipping frame processing.")

            # Send heartbeat using the configured heartbeat variable name
            send_heartbeat(objects, plcVarPath, python_heartbeat)

            # Add a small delay to avoid 100% CPU usage
            time.sleep(3)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        cleanup(objects, python_heartbeat)

if __name__ == "__main__":
    main()
