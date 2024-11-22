import logging
from process_frames import process_frames
from check_cameras import check_cameras
from opcua_connection import connectOPCUA

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the IP addresses of the cameras
camera_ips = ['169.254.207.1', '169.254.207.2']

# Define the path for the PLC variables
run_program = "run_program"

# Define the path for the PLC variables
plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]


def planting_operation():
    try:
        temp_path = plcVarPath.copy()  # Avoid modifying the original list
        temp_path[-1] = f"4:{run_program}"
        var_path = objects.get_child(temp_path)
        return var_path.get_value()
    except Exception as e:
        logging.error(f"Failed to retrieve planting operation value: {e}")
        return None


if __name__ == "__main__":
    try:
        # Connect to the OPC UA server
        objects = connectOPCUA()
        if objects is None:
            logging.error("Failed to connect to OPC UA server. Exiting program.")
            exit(1)

        # Check the cameras before proceeding
        camera_status = check_cameras(camera_ips)

        if camera_status:
            logging.info("All cameras are accessible. Proceeding with frame processing...")
            while(1):
                if planting_operation():
                    logging.info("Planting operation is active.")
                    process_frames(camera_ips)
                else:
                    logging.info("Planting operation is not active. Skipping frame processing.")
        else:
            logging.error("One or more cameras are not accessible. Exiting the program.")
            exit(1)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)
