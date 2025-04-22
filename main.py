import logging
import time
import os
import sys
import yaml
import atexit

from process_frames import process_frames
from frame_config import get_frame_config
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation
from session_utils import getSessionNumber
from send_heartbeat import send_heartbeat

# Disable logging from the opcua library
logging.getLogger("opcua").setLevel(logging.WARNING)

# Set up logging to capture only custom messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PLC variable path (hierarchical path to variables)
plcVarPath = [
    "0:Objects", "2:DeviceSet", "4:CODESYS Control Win V3 x64", 
    "3:Resources", "4:Application", "3:Programs", "4:PLC_PRG", "var"
]

# Constants
EXIT_CODE = 99

# Load configuration from YAML file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)

# Graceful cleanup function
def cleanup(objects, python_run):
    try:
        logging.info("Python program stopped. Updating PLC variable...")

        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{python_run}"

        var_node = objects.get_child(temp_path)

        if var_node is None:
            logging.error(f"Failed to retrieve PLC variable '{python_run}'. Skipping cleanup.")
            return

        var_node.set_value(0)
        logging.info("Cleanup complete. Resources have been cleaned up.")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

# Main logic
def main():
    config = load_config()

    camera_ips = config["camera_ips"]
    run_code = config["plc_variables"]["run_code"]
    python_heartbeat = config["plc_variables"]["python_heartbeat"]
    MAX_SESSION_NUMBER = config["max_session_number"]
    acc_mode = config["plc_variables"]["acc_mode"]
    tree_status_code = config["plc_variables"]["tree_status_code"]
    camera_status_code_1 = config["plc_variables"]["camera_status_code_1"]
    camera_status_code_2 = config["plc_variables"]["camera_status_code_2"]
    camera_status_code_3 = config["plc_variables"]["camera_status_code_3"]
    camera_status_code_4 = config["plc_variables"]["camera_status_code_4"]
    camera_status_code_5 = config["plc_variables"]["camera_status_code_5"]
    camera_status_code_6 = config["plc_variables"]["camera_status_code_6"]

    try:
        logging.info("Connecting to the OPC UA server...")
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            sys.exit(1)

        # Register cleanup for safe shutdown
        atexit.register(cleanup, objects, python_heartbeat)

        lastSession = getSessionNumber(objects)
        if lastSession is None:
            logging.error("Failed to retrieve initial session number. Exiting program.")
            sys.exit(1)

        while True:
            if exit_operation(objects) == EXIT_CODE:
                logging.info(f"Exit code {EXIT_CODE} received. Closing script.")
                break

            session_value = getSessionNumber(objects)
            if session_value is None:
                logging.warning("Session number retrieval failed. Skipping iteration.")
                continue

            logging.info("Checking camera accessibility...")
            camera_status = check_cameras(camera_ips, objects, plcVarPath, 
                                          camera_status_code_1, camera_status_code_2, 
                                          camera_status_code_3, camera_status_code_4,
                                          camera_status_code_5, camera_status_code_6)

            if not camera_status:
                logging.error("One or more cameras are not accessible. Skipping this iteration.")
                time.sleep(3)
                continue

            if planting_operation(objects, run_code) and lastSession != session_value:
                lastSession = session_value if session_value != MAX_SESSION_NUMBER else 0
                logging.info("Planting operation is active.")

                try:
                    frame_config = get_frame_config(objects, acc_mode)
                except Exception as e:
                    logging.error(f"Failed to retrieve frame configuration: {e}")
                    continue

                tree_status = process_frames(camera_ips, frame_config, objects, plcVarPath, tree_status_code)
                logging.info(tree_status)
            else:
                logging.info("Planting operation is not active. Skipping frame processing.")

            send_heartbeat(objects, plcVarPath, python_heartbeat)
            time.sleep(3)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'objects' in locals() and objects is not None:
            cleanup(objects, python_heartbeat)

if __name__ == "__main__":
    main()
