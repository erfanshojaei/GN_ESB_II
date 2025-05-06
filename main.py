import logging
import time
import os
import sys
import yaml
import atexit

from opcua import ua

# Custom module imports
from process_frames import process_frames
from frame_config import get_frame_config
from check_cameras import check_cameras
from opcua_connection import connectOPCUA
from exit_operation import exit_operation
from planting_operation import planting_operation
from session_utils import getSessionNumber
from send_heartbeat import send_heartbeat

# --- Logging Configuration ---
logging.getLogger("opcua").setLevel(logging.WARNING)  # Suppress OPC UA library logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
PLC_VAR_PATH = [
    "0:Objects", "2:DeviceSet", "4:CODESYS Control Win V3 x64", 
    "3:Resources", "4:Application", "3:Programs", "4:PLC_PRG", "var"
]
EXIT_CODE = 99


# --- Configuration Loader ---
def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        sys.exit(1)


# --- Cleanup Function ---
def cleanup(objects, heartbeat_var):
    try:
        logging.info("Python program stopped. Updating PLC variable...")

        var_path = PLC_VAR_PATH.copy()
        var_path[-1] = f"4:{heartbeat_var}"
        var_node = objects.get_child(var_path)

        if var_node is None:
            logging.error(f"Failed to retrieve PLC variable '{heartbeat_var}'. Skipping cleanup.")
            return

        var_node.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
        logging.info("Cleanup complete. Resources have been cleaned up.")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")


# --- Main Function ---
def main():
    config = load_config()

    camera_ips = config["camera_ips"]
    plc_vars = config["plc_variables"]
    max_session = config["max_session_number"]

    try:
        logging.info("Connecting to the OPC UA server...")
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting.")
            sys.exit(1)

        atexit.register(cleanup, objects, plc_vars["python_heartbeat"])

        last_session = getSessionNumber(objects)
        if last_session is None:
            logging.error("Unable to fetch initial session number. Exiting.")
            sys.exit(1)

        while True:
            if exit_operation(objects) == EXIT_CODE:
                logging.info(f"Exit code {EXIT_CODE} received. Closing script.")
                break

            session_value = getSessionNumber(objects)
            if session_value is None:
                logging.warning("Failed to retrieve session number. Skipping this iteration.")
                continue

            logging.info("Checking camera accessibility...")
            camera_status, connected_cameras, not_connected_cameras = check_cameras(
                camera_ips, objects, PLC_VAR_PATH,
                plc_vars["camera_status_code_1"],
                plc_vars["camera_status_code_2"],
                plc_vars["camera_status_code_3"],
                plc_vars["camera_status_code_4"],
                plc_vars["camera_status_code_5"],
                plc_vars["camera_status_code_6"]
            )

            if not camera_status:
                logging.error("Camera check failed. Skipping iteration.")
                time.sleep(3)
                continue

            if planting_operation(objects, plc_vars["run_code"]) and last_session != session_value:
                last_session = session_value if session_value != max_session else 0
                logging.info("Planting operation is active.")

                try:
                    frame_config = get_frame_config(objects, plc_vars["acc_mode"])
                except Exception as e:
                    logging.error(f"Error retrieving frame config: {e}")
                    continue

                # Only process frames for the connected cameras
                if connected_cameras:
                    logging.info(f"Processing frames for connected cameras: {connected_cameras}")
                    status = process_frames(connected_cameras, frame_config)
                    logging.info(status)
                    
                else:
                    logging.warning("No connected cameras. Skipping frame processing.")
            else:
                logging.info("Planting not active. Skipping frame processing.")

            send_heartbeat(objects, PLC_VAR_PATH, plc_vars["python_heartbeat"])
            time.sleep(3)

    except Exception as e:
        logging.error(f"Unhandled error: {e}")
    finally:
        if 'objects' in locals() and objects is not None:
            cleanup(objects, plc_vars["python_heartbeat"])


# --- Entry Point ---
if __name__ == "__main__":
    main()
