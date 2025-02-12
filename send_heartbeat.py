import logging

# Define a global variable for the heartbeat value
heartbeat_value = 0

# Function to send heartbeat to the PLC
def send_heartbeat(objects, plcVarPath, python_heartbeat):
    global heartbeat_value  # Use the global variable to keep the state

    try:
        # Toggle the heartbeat value between 0 and 1
        heartbeat_value = 1 if heartbeat_value == 0 else 0

        # Ensure the value is either 0 or 1
        if heartbeat_value not in [0, 1]:
            raise ValueError("Heartbeat value must be 0 or 1.")

        # Copy the path and update the last element to refer to 'Python_Heartbeat'
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{python_heartbeat}"
        
        # Get the PLC variable using the updated path
        var_path = objects.get_child(temp_path)
        
        # Get the data type of the variable and set it to the toggled value
        var_type = var_path.get_data_type_as_variant_type()
        var_path.set_value(heartbeat_value, var_type)
        
        logging.info(f"Heartbeat sent successfully: {heartbeat_value}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send heartbeat for '{python_heartbeat}': {e}")
        return False
