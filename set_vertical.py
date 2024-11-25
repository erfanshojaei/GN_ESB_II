import logging

# Function to set the 'tree_vertical' variable in the PLC
def set_vertical(objects, plcVarPath, tree_vertical):
    try:
        # Copy the path and update the last element to refer to 'tree_vertical'
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{tree_vertical}"
        
        # Get the PLC variable using the updated path
        var_path = objects.get_child(temp_path)
        
        # Get the data type of the variable and set it to True
        var_type = var_path.get_data_type_as_variant_type()
        var_path.set_value(True, var_type)
        
        logging.info(f"Successfully set {tree_vertical} to True.")
        return True
    except Exception as e:
        logging.error(f"Failed to set {tree_vertical}: {e}")
        return False
