import logging
from pypylon import pylon

def grab_frame_from_camera(camera_name, timeout=10000):
    """
    Attempts to grab a single frame from the camera with the specified user-defined name.
    Returns the frame (numpy array) if successful.
    Raises RuntimeError if the camera is not found or frame cannot be grabbed.
    """
    logging.info(f"Attempting to grab frame from camera named: {camera_name}")

    # Create the transport layer factory instance
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    logging.info(f"Devices found: {len(devices)}")

    camera = None

    for device in devices:
        try:
            name = device.GetUserDefinedName()
            logging.debug(f"Found device name: {name}")
            if name == camera_name:
                camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
                break
        except Exception as e:
            logging.warning(f"Could not read user-defined name from device: {e}")
            continue

    if not camera:
        raise RuntimeError(f"Camera with name '{camera_name}' not found.")

    try:
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            logging.info(f"Successfully grabbed frame from camera {camera_name}")
        else:
            raise RuntimeError(f"Failed to grab frame from camera {camera_name}.")
    finally:
        if 'grab_result' in locals() and grab_result.IsValid():
            grab_result.Release()
        if camera.IsGrabbing():
            camera.StopGrabbing()
        if camera.IsOpen():
            camera.Close()

    return frame
