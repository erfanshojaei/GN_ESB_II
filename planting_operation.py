import logging

# Define the base path for PLC variables
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

        # Get the PLC variable node
        var_node = objects.get_child(temp_path)
        if var_node is None:
            logging.error(f"Failed to retrieve '{run_code}' variable. Path: {temp_path}")
            return False

        # Get the value of 'run_code'
        run_code_value = var_node.get_value()
        #print(run_code_value)
        logging.info(f"Retrieved '{run_code}' value: {run_code_value}")

        # Check if run_code is 100 (start planting operation)
        return run_code_value == 100
    except Exception as e:
        logging.error(f"Error retrieving '{run_code}' value: {e} | Path: {temp_path}")
        return False
