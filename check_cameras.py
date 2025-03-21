import logging
from camera import grab_frame_from_camera

def check_cameras(camera_ips, objects, plcVarPath, camera_status_code):
    """
    Checks if the cameras are connected and able to capture frames.

    Parameters:
        camera_ips (list): List of IP addresses for the cameras to check.

    Returns:
        dict: A dictionary with IP addresses as keys and status messages as values.
    """
    results = {}

    for ip in camera_ips:
        last_octet = ip.split('.')[-1]  # Extract the last octet of the IP
        camera_check_code = 444  # Default to success (444) initially

        try:
            print(f"Checking camera with IP: {ip}")
            frame = grab_frame_from_camera(ip)
            if frame is None:
                raise ValueError("Failed to capture frame.")  # Simplified handling of frame failure

            results[ip] = "Connection successful, frame captured."

        except ValueError:
            results[ip] = "Failed to capture frame."
            camera_check_code = 555  # Failed to capture frame

        except RuntimeError as e:
            results[ip] = f"Error: {e}"
            camera_check_code = 666  # Runtime error

        except Exception as e:
            results[ip] = f"Unexpected error: {e}"
            camera_check_code = 666  # General error

        # Construct the number to send to CODESYS
        number_to_send = int(f"{last_octet}{camera_check_code}")
        print(f"Sending number {number_to_send} to CODESYS")
        
        # Update the PLC variable path with the new status code
        temp_path = plcVarPath[:-1] + [f"4:{camera_status_code}"]
        
        # Get the PLC variable and set the value
        var_path = objects.get_child(temp_path)
        var_path.set_value(number_to_send, var_path.get_data_type_as_variant_type())

    return results
