from pypylon import pylon

# Initialize the camera
try:
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()

    if len(devices) == 0:
        print("No cameras found.")
    else:
        # Attempt to grab a frame from the first camera
        camera = pylon.InstantCamera(tl_factory.CreateDevice(devices[0]))
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Grab a single frame
        grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grab_result.GrabSucceeded():
            print("Frame grabbed successfully.")
            # Do something with the frame (for example, print its shape)
            frame = grab_result.Array
            print("Frame shape:", frame.shape)
        else:
            print("Error grabbing frame:", grab_result.ErrorCode)

        grab_result.Release()
        camera.StopGrabbing()
        camera.Close()

except Exception as e:
    print("Error initializing camera:", str(e))
