import cv2

def crop_frame(frame, crop_coordinates):
    """Crops the frame to the specified coordinates."""
    x, y, width, height = crop_coordinates
    cropped_frame = frame[y:y + height, x:x + width]
    return cropped_frame
