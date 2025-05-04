import logging
from pypylon import pylon

def grab_frame_from_camera(ip_address, timeout=10000):
    """
    Grabs a single frame from a camera with the specified IP address.
    """
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    logging.info(f"Devices found: {len(devices)}")

    camera = None
    for device in devices:
        try:
            device_ip = device.GetPropertyValue("IpAddress")  # Adjust if necessary
            logging.info(f"Found device with IP: {device_ip}")  # Log device IP
            logging.info(f"Device Info: {device.GetPropertyValue('DeviceName')}")  # Log more info
            if device_ip == ip_address:
                logging.info(f"Matching device found for IP: {ip_address}")
                camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                break
        except Exception as e:
            logging.error(f"Error processing device: {e}")
            continue

    if not camera:
        raise RuntimeError(f"Camera with IP address {ip_address} not found.")

    try:
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            logging.info(f"Frame grabbed successfully. Frame shape: {frame.shape}")
        else:
            raise RuntimeError("Error grabbing frame.")
    finally:
        grab_result.Release()
        if camera.IsGrabbing():
            camera.StopGrabbing()
        if camera.IsOpen():
            camera.Close()

    return frame


def initialize_cameras(camera_ips):
    """
    Initializes cameras with the provided IP addresses.
    """
    cameras = {}
    for ip in camera_ips:
        try:
            logging.info(f"Initializing camera with IP: {ip}")
            cameras[ip] = grab_frame_from_camera(ip)  # Use the grab_frame_from_camera function
        except RuntimeError as e:
            logging.error(f"Error initializing camera with IP {ip}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error for camera with IP {ip}: {e}")
    return cameras

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example usage with a list of IP addresses
    camera_ips = ["169.254.207.1", "169.254.207.2", "169.254.207.3"]
    cameras = initialize_cameras(camera_ips)
