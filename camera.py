# camera.py
from pypylon import pylon

def grab_frame_from_camera(ip_address):
    # Create an instance of the camera factory
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    # Find the device that matches the specified IP address
    for device in devices:
        if device.GetIpAddress() == ip_address:
            camera = pylon.InstantCamera(tl_factory.CreateDevice(device))
            break
    else:
        raise RuntimeError(f"Camera with IP address {ip_address} not found.")

    # Open the camera
    camera.Open()

    # Start grabbing frames
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # Retrieve a frame
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grab_result.GrabSucceeded():
        # Convert the image to a format suitable for OpenCV
        frame = grab_result.Array
        camera.StopGrabbing()  # Stop grabbing after capturing one frame
        camera.Close()  # Close the camera connection
        return frame
    else:
        raise RuntimeError("Error grabbing frame.")
