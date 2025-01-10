import logging

# Function to set the 'python_run' variable in the PLC to True (indicating the program is running)
def set_python_program_running(objects, plcVarPath, python_run):
    try:
        # Copy the path and update the last element to refer to 'python_run'
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{python_run}"
        
        # Get the PLC variable using the updated path
        var_path = objects.get_child(temp_path)
        
        # Get the data type of the variable and set it to True
        var_type = var_path.get_data_type_as_variant_type()
        var_path.set_value(True, var_type)
        
        logging.info(f"Successfully set {python_run} to True. Python program is running.")
        return True
    except Exception as e:
        logging.error(f"Failed to set {python_run}: {e}")
        return False

# Function to set the 'python_run' variable in the PLC to False (indicating the program is not running)
def set_python_program_stopped(objects, plcVarPath, python_run):
    try:
        # Copy the path and update the last element to refer to 'python_run'
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{python_run}"
        
        # Get the PLC variable using the updated path
        var_path = objects.get_child(temp_path)
        
        # Get the data type of the variable and set it to False
        var_type = var_path.get_data_type_as_variant_type()
        var_path.set_value(False, var_type)
        
        logging.info(f"Successfully set {python_run} to False. Python program is stopped.")
        return True
    except Exception as e:
        logging.error(f"Failed to set {python_run}: {e}")
        return False
