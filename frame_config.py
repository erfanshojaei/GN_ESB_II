def get_frame_config():
    """
    Returns crop and ROI coordinates for each camera.
    """
    # Define crop coordinates for each camera
    crop_coordinates = {
        '169.254.207.1': (400, 300, 1500, 1500),  # x, y, width, height for Camera 1
        '169.254.207.2': (700, 300, 1500, 1500),  # x, y, width, height for Camera 2
    }

    # Define ROI coordinates for each camera
    roi_coordinates = {
        '169.254.207.1': (550, 50, 300, 1000),  # x, y, width, height for ROI Camera 1
        '169.254.207.2': (250, 50, 300, 1000),  # x, y, width, height for ROI Camera 2
    }

    return crop_coordinates, roi_coordinates
