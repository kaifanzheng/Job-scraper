import cv2
import pytesseract
import numpy as np

# Set the Tesseract-OCR path if necessary
pytesseract.pytesseract.tesseract_cmd = "tesseract"

def detect_show_more_button(image_path, output_path="debug_show_more.png"):
    """Detects and highlights the 'Show More' button in the bottom half of the image."""
    
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print("⚠️ Error: Unable to load the image.")
        return

    # Get image dimensions
    height, width, _ = image.shape

    # Focus only on the bottom half where the "Show More" button is likely located
    bottom_half = image[height // 2 :, :]

    # Convert image to grayscale
    gray = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY)

    # Apply OCR to detect text
    extracted_text = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    # Find occurrences of "Show More"
    for i, text in enumerate(extracted_text["text"]):
        if "Show" in text or "More" in text:  # Allow some OCR tolerance
            x, y, w, h = (
                extracted_text["left"][i],
                extracted_text["top"][i],
                extracted_text["width"][i],
                extracted_text["height"][i],
            )

            # Adjust y-coordinates to original image
            y += height // 2

            # Draw a red circle around the detected button
            cv2.circle(image, (x + w // 2, y + h // 2), 20, (0, 0, 255), 3)

            print(f"✅ 'Show More' button detected at: ({x}, {y})")

    # Save and display the debug image
    cv2.imwrite(output_path, image)
    print(f"🖼 Debug image saved as: {output_path}")

# Run detection on the provided screenshot
detect_show_more_button("job_details_0.png")
