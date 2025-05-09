from opcua import ua
import logging

def send_tree_status_to_codesys(connected_cameras, status_dict, all_camera_ips, objects, plc_var_path, plc_vars):
    """
    Sends tree status to CODESYS for each camera:
        - 0: Camera not connected
        - 1: Tree is vertical
        - 99: Tree is not vertical

    Args:
        connected_cameras (list): IPs of cameras currently connected.
        status_dict (dict): {ip: True/False} where True = vertical.
        all_camera_ips (list): Full list of camera IPs (from config).
        objects: OPC UA root object.
        plc_var_path (list): Path to PLC variables.
        plc_vars (dict): plc_variables from config.yaml.
    """
    for i, ip in enumerate(all_camera_ips, start=1):
        var_name = plc_vars.get(f"tree_status_code_{i}")
        var_path = plc_var_path.copy()
        var_path[-1] = f"4:{var_name}"

        if ip not in connected_cameras:
            status_code = 0
        elif status_dict.get(ip) is True:
            status_code = 1
        elif status_dict.get(ip) is False:
            status_code = 99
        else:
            status_code = 0  # Default fallback

        try:
            node = objects.get_child(var_path)
            # ✅ Use Byte for USINT type
            node.set_value(ua.DataValue(ua.Variant(status_code, ua.VariantType.Byte)))
            logging.info(f"{var_name} set to {status_code} for camera {ip}")
        except Exception as e:
            logging.error(f"Failed to set tree status for {ip} ({var_name}): {e}")
