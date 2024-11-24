import logging

# Define the path for the PLC variables
plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]

def exit_operation(objects, exit_script):
    """
    Checks if the exit operation is triggered by querying the PLC variable.
    """
    try:
        temp_path = plcVarPath.copy()  # Avoid modifying the original list
        temp_path[-1] = f"4:{exit_script}"
        var_path = objects.get_child(temp_path)
        return var_path.get_value()
    except Exception as e:
        logging.error(f"Failed to check exit operation: {e}")
        return None
