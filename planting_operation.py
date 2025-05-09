import logging

plcVarPath = [
    "0:Objects",
    "2:DeviceSet",
    "4:CODESYS Control Win V3 x64",
    "3:Resources",
    "4:Application",
    "3:Programs",
    "4:PLC_PRG",
    "var"
]

def planting_operation(opcua_client, run_code):
    """
    Checks if the planting operation should start by reading the given 'run_code' variable from CODESYS.

    Args:
        opcua_client: OPC UA client object.
        run_code (str): The name of the PLC variable that stores the operation status.

    Returns:
        bool: True if 'run_code' equals 1 (start planting), otherwise False.
    """
    temp_path = plcVarPath.copy()
    temp_path[-1] = f"4:{run_code}"

    try:
        var_node = opcua_client.get_child(temp_path)
        if var_node is None:
            logging.error(f"Variable '{run_code}' not found. Path: {temp_path}")
            return False

        run_code_value = var_node.get_value()
        if not isinstance(run_code_value, int):
            logging.error(f"Unexpected type for '{run_code}': {type(run_code_value)}. Expected int.")
            return False

        logging.debug(f"Retrieved '{run_code}' value: {run_code_value}")
        return run_code_value == 1

    except Exception as e:
        logging.error(f"Error retrieving '{run_code}' value: {e} | Path: {temp_path}")
        return False
