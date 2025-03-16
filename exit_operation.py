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

exit_code = "exit_code"  # The name of the variable you want to access

def exit_operation(objects):
    """
    Reads the exit_code from the PLC and returns it.
    """
    try:
        temp_path = plcVarPath.copy()  # Avoid modifying the original list
        temp_path[-1] = f"4:{exit_code}"    
        var_path = objects.get_child(temp_path)  # Get the PLC variable node
        #print(var_path.get_value())
        return var_path.get_value()
        
    except Exception as e:
        logging.error(f"Failed to read exit_code: {e}")
        return None
