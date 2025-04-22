import logging
from pypylon import pylon

def check_cameras(camera_ips, objects, plcVarPath,
                  camera_status_code_1, camera_status_code_2,
                  camera_status_code_3, camera_status_code_4,
                  camera_status_code_5, camera_status_code_6):
    """
    Checks if the cameras are connected and able to capture frames.
    Sends each camera's status code to its respective OPC UA variable.
    Returns a list of status codes for each camera.
    """
    status_codes = []  # Store status codes for all 6 cameras

    for ip in camera_ips:
        camera_check_code = 99  # Default to 99 (not set)

        try:
            logging.info(f"Checking camera with IP: {ip}")

            tl_factory = pylon.TlFactory.GetInstance()
            devices = tl_factory.EnumerateDevices()

            camera = None
            for device in devices:
                if hasattr(device, "GetIpAddress") and device.GetIpAddress() == ip:
                    camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                    break

            if not camera:
                logging.error(f"Camera with IP {ip} not found.")
                status_codes.append(camera_check_code)
                continue

            camera.Open()
            camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grab_result.GrabSucceeded():
                logging.info(f"Camera {ip} connected successfully.")
                camera_check_code = 1
                grab_result.Release()
            else:
                logging.error(f"Failed to grab a frame from camera with IP {ip}.")
                grab_result.Release()

            camera.StopGrabbing()
            camera.Close()

        except Exception as e:
            logging.error(f"Unexpected error while checking camera {ip}: {e}")
        finally:
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
        except Exception as e:
            logging.error(f"Error sending status for {camera_ips[idx]} to CODESYS: {e}")

    return status_codes
