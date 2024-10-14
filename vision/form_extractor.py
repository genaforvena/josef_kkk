import cv2
import numpy as np
import pytesseract
from PIL import Image

def preprocess_image(image: np.ndarray) -> np.ndarray:
    # Convert PIL Image to numpy array if necessary
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    return thresh

def detect_lines(image: np.ndarray) -> tuple:
    # Detect horizontal and vertical lines
    horizontal = np.copy(image)
    vertical = np.copy(image)
    
    cols = horizontal.shape[1]
    horizontal_size = cols // 30
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)
    
    rows = vertical.shape[0]
    vertical_size = rows // 30
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)
    
    return horizontal, vertical

def extract_form_fields(image: np.ndarray) -> list:
    # Preprocess the image
    processed = preprocess_image(image)
    
    # Detect lines
    horizontal, vertical = detect_lines(processed)
    
    # Combine horizontal and vertical lines
    mask = horizontal + vertical
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by y-coordinate
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    
    fields = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 10:  # Filter out small contours
            roi = processed[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config='--psm 6')
            text = text.strip()
            if ':' in text:
                label, value = text.split(':', 1)
                fields.append((label.strip(), value.strip()))
            elif text:
                fields.append((text, ''))
    
    return fields

def extract_fields(image_path: str) -> list:
    # Read the image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return list()

    # Extract form fields
    return extract_form_fields(image)

def main(image_path: str):
    extracted_fields = extract_fields(image_path)
    
    print("Extracted form fields:")
    for label, value in extracted_fields:
        print(f"{label}: {value}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
    else:
        main(sys.argv[1])