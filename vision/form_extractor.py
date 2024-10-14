import argparse
import cv2
import numpy as np
import pytesseract
from PIL import Image
import pdf2image
import os

def read_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.pdf':
        try:
            return pdf2image.convert_from_path(file_path)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return []
    else:
        image = read_image(file_path)
        return [image] if image is not None else []

def read_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
    return image

def preprocess_image(image):
    # Convert PIL Image to numpy array if necessary
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    
    return dilate

def extract_form_data(processed_image):
    # Perform OCR on the processed image
    text = pytesseract.image_to_string(Image.fromarray(processed_image))
    print(text)
    
    # Split the text into lines
    lines = text.split('\n')
    
    # Extract field labels (assuming labels end with ':')
    fields = [line.strip() for line in lines if ':' in line]
    
    # Group fields into pairs, with the last one alone if odd number
    grouped_fields = [fields[i:i+2] for i in range(0, len(fields), 2)]
    if len(fields) % 2 != 0:
        grouped_fields[-1] = [grouped_fields[-1][0]]
    
    return grouped_fields

def main(file_path):
    images = read_file(file_path)
    
    if not images:
        print(f"Error: Could not read file {file_path}")
        return

    for i, image in enumerate(images):
        processed_image = preprocess_image(image)
        extracted_data = extract_form_data(processed_image)
        
        print(f"Extracted form fields from page {i+1}:")
        for group in extracted_data:
            print(group)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract form data from an image or PDF")
    parser.add_argument("file_path", type=str, help="Path to the form image or PDF")
    args = parser.parse_args()
    main(args.file_path)
