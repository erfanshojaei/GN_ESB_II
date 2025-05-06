import logging
from pypylon import pylon

def check_cameras(camera_ips, objects, plcVarPath,
                  camera_status_code_1, camera_status_code_2,
                  camera_status_code_3, camera_status_code_4,
                  camera_status_code_5, camera_status_code_6):
    """
    Checks if the cameras are connected and able to capture frames.
    Sends each camera's status code to its respective OPC UA variable.
    Returns a list of status codes for each camera, along with arrays of connected and not connected cameras.
    """
    status_codes = []  # Store status codes for all 6 cameras
    connected_cameras = []  # List to store connected camera IPs
    not_connected_cameras = []  # List to store not connected camera IPs

    for ip in camera_ips:
        camera_check_code = 99  # Default to 99 (not set)

        try:
            logging.info(f"Checking camera with IP: {ip}")

            # Enumerate devices
            tl_factory = pylon.TlFactory.GetInstance()
            devices = tl_factory.EnumerateDevices()
            if not devices:
                logging.error(f"No devices found. Check camera connections. IP: {ip}")
                not_connected_cameras.append(ip)
                status_codes.append(camera_check_code)
                continue

            camera = None
            for device in devices:
                if hasattr(device, "GetIpAddress") and device.GetIpAddress() == ip:
                    camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                    break

            if not camera:
                logging.error(f"Camera with IP {ip} not found or failed to connect.")
                not_connected_cameras.append(ip)
                status_codes.append(camera_check_code)
                continue

            # Attempt to connect to the camera and grab a frame
            camera.Open()
            camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            grab_result = camera.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)  # Increased timeout

            if grab_result and grab_result.GrabSucceeded():
                logging.info(f"Camera {ip} connected successfully.")
                camera_check_code = 1
                connected_cameras.append(ip)
                grab_result.Release()
            else:
                logging.error(f"Failed to grab a frame from camera with IP {ip}. Error: {grab_result.GetErrorDescription()}")
                not_connected_cameras.append(ip)
                grab_result.Release()

            camera.StopGrabbing()
            camera.Close()

        except Exception as e:
            logging.error(f"Unexpected error while checking camera {ip}: {e}")
            not_connected_cameras.append(ip)
        finally:
            # Ensure the camera is properly stopped and closed even if an error occurs
            if camera and camera.IsGrabbing():
                camera.StopGrabbing()
                camera.Close()

            status_codes.append(camera_check_code)

    # Send each camera status to CODESYS individually
    camera_codes = [
        camera_status_code_1, camera_status_code_2,
        camera_status_code_3, camera_status_code_4,
        camera_status_code_5, camera_status_code_6
    ]

    for idx in range(min(len(status_codes), 6)):
        try:
            temp_path = plcVarPath[:-1] + [f"4:{camera_codes[idx]}"]
            var_node = objects.get_child(temp_path)
            var_node.set_value(status_codes[idx], var_node.get_data_type_as_variant_type())
            logging.info(f"Sent status code {status_codes[idx]} for camera with IP {camera_ips[idx]}")
        except Exception as e:
            logging.error(f"Error sending status for {camera_ips[idx]} to CODESYS: {e}")

    return status_codes, connected_cameras, not_connected_cameras
