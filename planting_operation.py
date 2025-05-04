import logging

plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]


def planting_operation(objects, run_code):
    """
    Checks if the planting operation should start by reading the given 'run_code' variable from CODESYS.

    Args:
        objects: OPC UA client object.
        run_code (str): The name of the PLC variable that stores the operation status.

    Returns:
        bool: True if 'run_code' is 100 (start planting), otherwise False.
    """
    try:
        # Create a copy of the base path and update the last element
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{run_code}"  # Use the provided run_code variable name

        # Get the PLC variable node safely
        try:
            var_node = objects.get_child(temp_path)
        except Exception as e:
            logging.error(f"Failed to access '{run_code}' variable node: {e} | Path: {temp_path}")
            return False

        if var_node is None:
            logging.error(f"Variable '{run_code}' not found. Path: {temp_path}")
            return False

        # Get the value of 'run_code'
        run_code_value = var_node.get_value()

        # Ensure the value is an integer before checking
        if not isinstance(run_code_value, int):
            logging.error(f"Unexpected type for '{run_code}': {type(run_code_value)}. Expected int.")
            return False

        logging.debug(f"Retrieved '{run_code}' value: {run_code_value}")

        # Check if run_code is 1 (start planting operation)
        return run_code_value == 1

    except Exception as e:
        logging.error(f"Error retrieving '{run_code}' value: {e} | Path: {temp_path}")
        return False
