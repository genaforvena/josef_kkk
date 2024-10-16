import os
import base64
import time
import pyautogui
import numpy as np
from PIL import Image
from groq import Groq
import argparse

def identify_telegram_chat_area(image):
    # Convert PIL Image to numpy array
    img_np = np.array(image)
    
    # Define the color range for Telegram's dark theme background
    # You may need to adjust these values based on your screen
    lower_bound = np.array([30, 39, 50])  # Dark blue-gray
    upper_bound = np.array([34, 43, 54])  # Dark blue-gray
    
    # Create a mask where the color is within the specified range
    mask = np.all((lower_bound <= img_np) & (img_np <= upper_bound), axis=-1)
    
    # Find the coordinates of the matching pixels
    y_coords, x_coords = np.where(mask)
    
    if len(y_coords) == 0 or len(x_coords) == 0:
        return None
    
    # Get the bounding box of the chat area
    left = x_coords.min()
    top = y_coords.min()
    right = x_coords.max()
    bottom = y_coords.max()
    
    # Add some padding
    padding = 10
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    
    return (left, top, right, bottom)

def capture_telegram_chat():
    # Capture the full screen
    full_screenshot = pyautogui.screenshot()
    
    # Identify the Telegram chat area
    chat_area = identify_telegram_chat_area(full_screenshot)
    
    if chat_area:
        # Crop the screenshot to the chat area
        cropped_chat = full_screenshot.crop(chat_area)
        
        # Save the cropped screenshot to a temporary file
        temp_file = "temp_telegram_chat.png"
        cropped_chat.save(temp_file)
        
        return temp_file
    else:
        raise Exception("Telegram chat area not found in the screenshot")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_with_groq(image_path, api_key):
    client = Groq(api_key=api_key)
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please analyze this Telegram chat screenshot. Provide a concise summary of the last few messages. Then, generate an appropriate response to continue the conversation."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    return response.choices[0].message.content

def main(instruction):
    print("Starting Telegram chat capture and Groq interaction...")
    
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    while True:
        input("Press Enter to capture the Telegram chat and process with Groq...")
        
        try:
            # Capture Telegram chat area
            screenshot_path = capture_telegram_chat()
            print("Telegram chat area captured.")

            # Process with Groq
            print("Processing with Groq...")
            response = process_with_groq(screenshot_path, api_key)
            
            # Print and speak Groq's response
            print("\nGroq's response:")
            print(response)

            # Clean up the temporary screenshot file
            os.remove(screenshot_path)

        except Exception as e:
            print(f"An error occurred: {e}")

        print("\nPress Enter to continue or type 'quit' to exit.")
        user_input = input()
        if user_input.lower() == 'quit':
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telegram chat capture and Groq interaction script")
    parser.add_argument("--instruction", type=str, default="You are a helpful assistant analyzing Telegram chats and generating responses.", 
                        help="Instruction for Groq's behavior")
    args = parser.parse_args()
    
    main(args.instruction)