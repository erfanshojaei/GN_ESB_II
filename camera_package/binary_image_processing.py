import cv2

def process_image(image):
    """Convert a monochrome (grayscale) image to a binary image for dark objects and apply morphological opening."""
    if image is None:
        raise ValueError("Invalid image provided for processing. The image cannot be None.")

    # Define kernel size and iterations
    kernel_size = 3
    iterations = 1

    # Invert the monochrome image
    inverted_image = cv2.bitwise_not(image)

    # Create binary image by thresholding (for dark objects)
    # This thresholding will consider dark objects as white in the binary image
    _, binary_image = cv2.threshold(inverted_image, 128, 255, cv2.THRESH_BINARY)

    # Create a rectangular structuring element
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    
    # Apply morphological opening to remove small objects
    opened_binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel, iterations=iterations)

    return opened_binary_image
