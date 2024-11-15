# check_cameras.py
from camera import grab_frame_from_camera

def check_cameras(camera_ips):
    """
    Checks if the cameras are connected and able to capture frames.

    Parameters:
        camera_ips (list): List of IP addresses for the cameras to check.

    Returns:
        dict: A dictionary with IP addresses as keys and status messages as values.
    """
    results = {}

    for ip in camera_ips:
        try:
            print(f"Checking camera with IP: {ip}")
            frame = grab_frame_from_camera(ip)
            if frame is not None:
                results[ip] = "Connection successful, frame captured."
            else:
                results[ip] = "Failed to capture frame."
        except RuntimeError as e:
            results[ip] = f"Error: {e}"
        except Exception as e:
            results[ip] = f"Unexpected error: {e}"
    
    return results
