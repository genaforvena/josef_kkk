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

def identify_telegram_chat_area(image):
    img_np = np.array(image)
    lower_bound = np.array([30, 39, 50])
    upper_bound = np.array([34, 43, 54])
    mask = np.all((lower_bound <= img_np) & (img_np <= upper_bound), axis=-1)
    y_coords, x_coords = np.where(mask)
    
    if len(y_coords) == 0 or len(x_coords) == 0:
        return None
    
    left = x_coords.min()
    top = y_coords.min()
    right = x_coords.max()
    bottom = y_coords.max()
    
    padding = 10
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    
    return (left, top, right, bottom)

def capture_telegram_chat():
    full_screenshot = pyautogui.screenshot()
    chat_area = identify_telegram_chat_area(full_screenshot)
    
    if chat_area:
        cropped_chat = full_screenshot.crop(chat_area)
        temp_file = "temp_telegram_chat.png"
        cropped_chat.save(temp_file)
        return temp_file
    else:
        raise Exception("Telegram chat area not found in the screenshot")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_with_groq(image_path, api_key, general_instruction=None):
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
                        "text": "Please analyze this Telegram chat screenshot. Provide a summary of the conversation and the message to reply to."
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

    chat_history = []
    if general_instruction:
        chat_history.append(
                {
                    'role': 'assistant',
                    'content': general_instruction
                }
        )
    chat_history.append(
            {
                'role': 'assistant',
                'content': text_analysis
            }
    )
    chat_history.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Make the one paragraph of the best, short, witty, funny and suitable reply to the conversation in the previous message that follows the style of conversation."
                    }
                ]
            }
    )
    response = client.chat.completions.create(
        model="llama-3.2-90b-text-preview",
        messages=chat_history
    )

    return response.choices[0].message.content

def send_to_telegram(response):
    # Assume the active window is Telegram
    # Type the response
    pyautogui.typewrite(response)
    
    # Press Enter to send the message    pyautogui.press('enter')

def process_and_reply(general_instruction=None):
    try:
        print("Processing...")
        screenshot_path = capture_telegram_chat()
        
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        response = process_with_groq(screenshot_path, api_key, general_instruction)
        print("Groq's response:", response)
        
        send_to_telegram(response)
        print("Response sent to Telegram.")
        
        os.remove(screenshot_path)
    except Exception as e:
        print(f"An error occurred: {e}")

def on_hotkey(general_instruction=None):
    # Run the process in a separate thread to keep the script responsive
    threading.Thread(target=process_and_reply, args=(general_instruction,)).start()

def main():
    parser = argparse.ArgumentParser(description="Telegram chat analysis and response automation.")
    parser.add_argument("--instruction", type=str, help="Optional general instruction for the second Groq call.")
    args = parser.parse_args()

    print("Starting Telegram chat analysis and response automation...")
    print("Press Ctrl+Shift+G to capture, analyze, and reply.")
    print("Press Ctrl+C to exit.")

    # Set up the hotkey
    keyboard.add_hotkey('ctrl+shift+g', lambda: on_hotkey(args.instruction))

    try:
        # Keep the script running
        keyboard.wait()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()