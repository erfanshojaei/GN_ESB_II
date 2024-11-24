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

def planting_operation(objects, run_program):
    """
    Checks if the planting operation is active by querying the PLC variable.
    """
    try:
        temp_path = plcVarPath.copy()  # Avoid modifying the original list
        temp_path[-1] = f"4:{run_program}"
        var_path = objects.get_child(temp_path)
        return var_path.get_value()
    except Exception as e:
        logging.error(f"Failed to retrieve planting operation value: {e}")
        return None
