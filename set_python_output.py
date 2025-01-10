import logging

def set_python_output(objects, plcVarPath, variable_name, value_to_set=True):
    """
    Sets the value of a specific variable in the PLC using OPC UA.

    :param objects: OPC UA objects node (connected client root).
    :param plcVarPath: List representing the path to the PLC variables.
    :param variable_name: Name of the variable to update (e.g., "python_terminal_output").
    :param value_to_set: The value to set (default is True).
    :return: True if the operation is successful, False otherwise.
    """
    try:
        # Create a temporary path to the variable
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{variable_name}"  # Update the last path segment with the variable name
        
        # Get the variable node using the updated path
        var_node = objects.get_child(temp_path)
        
        # Get the data type of the variable
        var_type = var_node.get_data_type_as_variant_type()
        
        # Set the variable value
        var_node.set_value(ua.Variant(value_to_set, var_type))
        
        logging.info(f"Successfully set {variable_name} to {value_to_set}.")
        return True
    except Exception as e:
        logging.error(f"Failed to set variable '{variable_name}' to '{value_to_set}': {e}")
        return False