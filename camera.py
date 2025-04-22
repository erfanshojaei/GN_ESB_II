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
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    print("Available cameras:")
    for device in devices:
        try:
            ip = device.GetPropertyValue("IpAddress")
            print(f"- {device.GetFriendlyName()} @ {ip}")
        except Exception as e:
            print(f"- Failed to read device IP: {e}")

    camera = None
    for device in devices:
        try:
            if device.GetPropertyValue("IpAddress") == ip_address:
                camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                break
        except Exception:
            continue

    if not camera:
        raise RuntimeError(f"Camera with IP address {ip_address} not found.")

    try:
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        try:
            if grab_result.GrabSucceeded():
                frame = grab_result.Array
            else:
                raise RuntimeError("Error grabbing frame.")
        finally:
            grab_result.Release()

    finally:
        if camera.IsGrabbing():
            camera.StopGrabbing()
        if camera.IsOpen():
            camera.Close()

    return frame
