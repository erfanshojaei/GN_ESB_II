from pypylon import pylon

def test_camera_connection(ip_address, timeout=5000):
    """
    Test connection to a camera by IP address.

    Args:
        ip_address (str): The IP address of the camera.
        timeout (int): Timeout in milliseconds for frame retrieval.

    Returns:
        bool: True if the camera was successfully connected and frame was grabbed, False otherwise.
    """
    try:
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
            print(f"ERROR: Camera with IP address {ip_address} not found.")
            return False

        # Try to open the camera and grab a frame
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Attempt to retrieve a frame
        grab_result = camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            print(f"Camera with IP {ip_address} connected successfully and frame grabbed.")
            grab_result.Release()
            return True
        else:
            print(f"ERROR: Failed to grab a frame from camera with IP {ip_address}.")
            grab_result.Release()
            return False

    except Exception as e:
        print(f"ERROR: Exception occurred while testing camera with IP {ip_address}: {e}")
        return False

    finally:
        if camera and camera.IsGrabbing():
            camera.StopGrabbing()
        if camera and camera.IsOpen():
            camera.Close()


def main():
    # Camera IPs
    camera_ips = [
        "169.254.207.1",  # Camera 1 IP
        "169.254.207.2",  # Camera 2 IP
        "169.254.207.3",  # Camera 3 IP
        "169.254.207.4",  # Camera 4 IP
        "169.254.207.5",  # Camera 5 IP
        "169.254.207.6",  # Camera 6 IP
    ]

    # Test each camera
    for ip in camera_ips:
        print(f"\nTesting camera with IP: {ip}")
        success = test_camera_connection(ip)
        if success:
            print(f"Camera with IP {ip} is connected and working.")
        else:
            print(f"Camera with IP {ip} failed to connect.")


if __name__ == "__main__":
    main()
