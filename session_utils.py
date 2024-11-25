# session_utils.py

import logging
import time


# Define the path for the PLC variables
plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]

sessionNumber = "sessionNumber"

def getSessionNumber(objects, retries=3, delay=1):
    try:
        temp_path = plcVarPath.copy()  # Avoid modifying the original list
        temp_path[-1] = f"4:{sessionNumber}"
        var_path = objects.get_child(temp_path)
        return var_path.get_value()
    except Exception as e:
        logging.error(f"Failed to retrieve session number: {e}")
        if retries > 0:
            logging.info(f"Retrying... ({retries} attempts left)")
            time.sleep(delay)
            return getSessionNumber(objects, retries - 1, delay)
        return None
