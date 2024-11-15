# camera.py
from pypylon import pylon

def grab_frame_from_camera(ip_address, timeout=5000):
    """
    Grabs a single frame from a camera with the specified IP address.

    Args:
        ip_address (str): The IP address of the camera.
        timeout (int): Timeout in milliseconds for frame retrieval.

    Returns:
        np.ndarray: The grabbed frame as an image array.

    Raises:
        RuntimeError: If the camera is not found or frame grab fails.
    """
    # Create an instance of the camera factory
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    # Find the device that matches the specified IP address
    camera = None
    for device in devices:
        if hasattr(device, "GetIpAddress") and device.GetIpAddress() == ip_address:
            camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
            break

    if not camera:
        raise RuntimeError(f"Camera with IP address {ip_address} not found.")

    try:
        # Open the camera
        camera.Open()

        # Start grabbing frames
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Retrieve a frame
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        try:
            if grab_result.GrabSucceeded():
                # Convert the image to a format suitable for OpenCV
                frame = grab_result.Array
            else:
                raise RuntimeError("Error grabbing frame.")
        finally:
            # Ensure grab result is released
            grab_result.Release()
    finally:
        # Ensure resources are released
        if camera.IsGrabbing():
            camera.StopGrabbing()
        if camera.IsOpen():
            camera.Close()

    return frame
