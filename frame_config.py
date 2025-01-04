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

def get_frame_config(objects):
    """
    Returns crop and ROI coordinates for each camera based on active accuracy mode.

    Args:
        objects: The OPC UA objects node.

    Returns:
        tuple: A dictionary of crop coordinates and a dictionary of ROI coordinates.
    """
    try:
        # Query each accuracy setting from the PLC
        accuracy_vars = ["set_vry_low_acc", "set_low_acc", "set_nrml_acc", "set_hgh_acc", "set_vry_hgh_acc"]
        active_mode = None

        for var in accuracy_vars:
            temp_path = plcVarPath.copy()
            temp_path[-1] = f"4:{var}"
            var_path = objects.get_child(temp_path)
            value = var_path.get_value()
            
            if value:  # If the variable is True
                active_mode = var
                logging.info(f"Active accuracy mode found: {active_mode}")
                print(f"Active accuracy mode: {active_mode}")  # Printing the active mode
                break

        # Define crop coordinates based on the active mode
        if active_mode == "set_vry_low_acc":
            crop_coordinates = {
                '169.254.207.1': (100, 100, 1200, 1200),
                '169.254.207.2': (200, 100, 1200, 1200),
            }
        elif active_mode == "set_low_acc":
            crop_coordinates = {
                '169.254.207.1': (300, 200, 1400, 1400),
                '169.254.207.2': (400, 200, 1400, 1400),
            }
        elif active_mode == "set_nrml_acc":
            crop_coordinates = {
                '169.254.207.1': (400, 300, 1500, 1500),
                '169.254.207.2': (500, 300, 1500, 1500),
            }
        elif active_mode == "set_hgh_acc":
            crop_coordinates = {
                '169.254.207.1': (600, 400, 1600, 1600),
                '169.254.207.2': (700, 400, 1600, 1600),
            }
        elif active_mode == "set_vry_hgh_acc":
            crop_coordinates = {
                '169.254.207.1': (800, 500, 1700, 1700),
                '169.254.207.2': (900, 500, 1700, 1700),
            }
        else:
            # Default crop coordinates set to "set_vry_low_acc" if no mode is active
            crop_coordinates = {
                '169.254.207.1': (100, 100, 1200, 1200),  # Same as set_vry_low_acc
                '169.254.207.2': (200, 100, 1200, 1200),  # Same as set_vry_low_acc
            }
            logging.warning("No active accuracy mode found, using 'set_vry_low_acc' default crop coordinates.")
            print("No active accuracy mode found, using 'set_vry_low_acc' default crop coordinates.")  # Print for fallback

        # Define ROI coordinates
        roi_coordinates = {
            '169.254.207.1': (550, 50, 300, 1000),  # x, y, width, height for ROI Camera 1
            '169.254.207.2': (250, 50, 300, 1000),  # x, y, width, height for ROI Camera 2
        }

        return crop_coordinates, roi_coordinates

    except Exception as e:
        logging.error(f"Failed to retrieve frame configuration: {e}")
        print(f"Failed to retrieve frame configuration: {e}")  # Print error message
        return None, None
