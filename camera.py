import logging
from pypylon import pylon

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def grab_frame_from_camera(ip_address, timeout=10000):
    """
    Attempts to grab a single frame from the camera with the specified IP address.
    Returns the frame (numpy array) if successful.
    Raises RuntimeError if the camera is not found or frame cannot be grabbed.
    """
    logging.info(f"Attempting to grab frame from camera with IP: {ip_address}")

    # Create the transport layer factory instance
    tl_factory = pylon.TlFactory.GetInstance()

    # Enumerate connected devices
    devices = tl_factory.EnumerateDevices()
    logging.info(f"Devices found: {len(devices)}")

    # Check all detected devices and log their IP addresses
    for device in devices:
        try:
            device_ip = device.GetIpAddress()
            logging.info(f"Found device with IP: {device_ip}")
            if device_ip == ip_address:
                camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                logging.info(f"Camera with IP {ip_address} found.")
                break
        except Exception as e:
            logging.warning(f"Could not read IP from device: {e}")
            continue
    else:
        raise RuntimeError(f"Camera with IP address {ip_address} not found.")

    try:
        # Open camera and start grabbing frames
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        # Check if the frame was successfully grabbed
        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            logging.info(f"Successfully grabbed frame from camera {ip_address}")
        else:
            raise RuntimeError(f"Failed to grab frame from camera {ip_address}.")
    finally:
        # Release result and clean up camera resources
        if 'grab_result' in locals() and grab_result.IsValid():
            grab_result.Release()
        if camera.IsGrabbing():
            camera.StopGrabbing()
        if camera.IsOpen():
            camera.Close()

    return frame
