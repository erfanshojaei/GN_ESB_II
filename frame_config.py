import logging

plcVarPath = ["0:Objects",
              "2:DeviceSet",
              "4:CODESYS Control Win V3 x64",
              "3:Resources",
              "4:Application",
              "3:Programs",
              "4:PLC_PRG",
              "var"]


def get_frame_config(objects, acc_mode):
    """
    Retrieves crop and ROI coordinates for each camera based on the accuracy mode received from CODESYS.

    Args:
        objects: The OPC UA client object.
        acc_code: The accuracy code retrieved from the CODESYS.

    Returns:
        tuple: A dictionary of crop coordinates and a dictionary of ROI coordinates.
    """
    try:
        # Define the path to access the 'acc_code' from the PLC
        temp_path = plcVarPath.copy()
        temp_path[-1] = f"4:{acc_mode}"  # Correctly reference the 'acc_code' variable from CODESYS

        # Get the PLC variable node
        var_node = objects.get_child(temp_path)
        if var_node is None:
            logging.error(f"Failed to retrieve 'acc_code' variable. Path: {temp_path}")
            return None, None

        # Get the value of 'acc_code' (this is the code sent from CODESYS)
        acc_mode_value = var_node.get_value()
        logging.info(f"Retrieved 'acc_code' value: {acc_mode_value}")

        # Determine active mode based on the received code
        accuracy_map = {
            200: "set_vry_low_acc",
            210: "set_low_acc",
            220: "set_nrml_acc",
            230: "set_hgh_acc",
            240: "set_vry_hgh_acc"
        }
        
        # Default to "set_vry_low_acc" if the code is not recognized
        active_mode = accuracy_map.get(acc_mode_value, "set_vry_low_acc")
        logging.info(f"Active accuracy mode: {active_mode}")

        # Define crop coordinates based on the active mode
        crop_coordinates_map = {
            "set_vry_low_acc": {
                '169.254.207.1': (100, 100, 1200, 1200),
                '169.254.207.2': (200, 100, 1200, 1200),
            },
            "set_low_acc": {
                '169.254.207.1': (300, 200, 1400, 1400),
                '169.254.207.2': (400, 200, 1400, 1400),
            },
            "set_nrml_acc": {
                '169.254.207.1': (400, 300, 1500, 1500),
                '169.254.207.2': (500, 300, 1500, 1500),
            },
            "set_hgh_acc": {
                '169.254.207.1': (600, 400, 1600, 1600),
                '169.254.207.2': (700, 400, 1600, 1600),
            },
            "set_vry_hgh_acc": {
                '169.254.207.1': (800, 500, 1700, 1700),
                '169.254.207.2': (900, 500, 1700, 1700),
            }
        }

        # Get the crop coordinates for the active mode
        crop_coordinates = crop_coordinates_map.get(active_mode)
        if not crop_coordinates:
            logging.warning(f"Invalid accuracy mode received: {acc_mode_value}, using default 'set_vry_low_acc'.")
            crop_coordinates = crop_coordinates_map["set_vry_low_acc"]

        # Define ROI coordinates (these remain constant)
        roi_coordinates = {
            '169.254.207.1': (550, 50, 300, 1000),  # x, y, width, height for ROI Camera 1
            '169.254.207.2': (250, 50, 300, 1000),  # x, y, width, height for ROI Camera 2
        }

        return crop_coordinates, roi_coordinates

    except Exception as e:
        logging.error(f"Failed to retrieve frame configuration: {e} | Path: {temp_path}")
        return None, None
