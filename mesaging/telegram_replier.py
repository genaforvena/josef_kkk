import os
import base64
import time
import pyautogui
import numpy as np
from PIL import Image
from groq import Groq
import keyboard
import threading
import sys
import argparse
import pytesseract
import pygetwindow as gw

def capture_telegram_window():
    active_window = gw.getActiveWindow()

    if active_window is None:
        print("No active window found. Make sure you selected the Telegram window.")
        return None

    # Get window position and size
    left, top = active_window.left, active_window.top
    width, height = active_window.width, active_window.height

    # Capture the screenshot
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    text_area = extract_chat_area(screenshot)
    temp_file = "temp_telegram_chat.png"
    screenshot.save(temp_file)
    
    print(f"Screenshot captured: {temp_file}")
    return temp_file

def extract_chat_area(image):
    # Convert the image to numpy array
    img_array = np.array(image)

    # Define the color range for the chat area (dark blue-grey)
    lower_bound = np.array([30, 39, 50])
    upper_bound = np.array([34, 43, 54])

    # Create a mask where the color is within the specified range
    mask = np.all((lower_bound <= img_array) & (img_array <= upper_bound), axis=-1)

    # Find the coordinates of the chat area
    y_coords, x_coords = np.where(mask)

    if len(y_coords) == 0 or len(x_coords) == 0:
        return None

    # Define the boundaries of the chat area
    left = x_coords.min()
    top = y_coords.min()
    right = x_coords.max()
    bottom = y_coords.max()

    # Crop the image to the chat area
    chat_area = image.crop((left, top, right, bottom))

    return chat_area

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Tesseract extracted text: " + text)
    return text

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_with_groq(image_path, api_key, general_instruction=None):
    client = Groq(api_key=api_key)

    chat_history = []
    if general_instruction:
        chat_history.append({
            'role': 'system',
            'content': general_instruction
        })
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract each message from it this Telegram chat screenshot. Come up with 10 short replies to continue this conversation as numbered list (number followed by dot) with quotation marks."
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
    text_analysis = response.choices[0].message.content
    print("Chat analysis: " + text_analysis)
 
    return response.choices[0].message.content

def send_to_telegram(response):
    pyautogui.typewrite(response)
    pyautogui.press('enter')

def process_and_reply(general_instruction=None):
    try:
        print("Processing...")
        screenshot_path = capture_telegram_window()
        if screenshot_path is None:
            print("Failed to capture Telegram window.")
            return

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        response = process_with_groq(screenshot_path, api_key, general_instruction)
        print("Groq's response:", response)

        import random

        lines = response.split('\n')
        start_index = next(i for i, line in enumerate(lines) if line.startswith('1. '))

        short_replies = [line.split('"')[1] for line in lines[start_index:start_index+10]]
        # Pick a random item from the list
        random_response = random.choice(short_replies)
        print("Random response:", random_response)
        response = random_response
        
        send_to_telegram(response)
        print("Response sent to Telegram.")
        
        os.remove(screenshot_path)
    except Exception as e:
        print(f"An error occurred: {e}")

def on_hotkey(general_instruction=None):
    threading.Thread(target=process_and_reply, args=(general_instruction,)).start()

def main():
    parser = argparse.ArgumentParser(description="Telegram chat analysis and response automation.")
    parser.add_argument("--instruction", type=str, help="Optional general instruction for the Groq call.")
    args = parser.parse_args()

    print("Starting Telegram chat analysis and response automation...")
    print("Select the Telegram window, then press Ctrl+Shift+G.")
    print("Press Ctrl+C to exit.")

    keyboard.add_hotkey('ctrl+shift+g', lambda: on_hotkey(args.instruction))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
