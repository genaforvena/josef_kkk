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

def capture_linkedin_page():
    active_window = gw.getActiveWindow()

    if active_window is None:
        print("No active window found. Make sure you selected the LinkedIn window.")
        return None

    # Get window position and size
    left, top = active_window.left, active_window.top
    width, height = active_window.width, active_window.height

    # Capture the screenshot
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    temp_file = "temp_linkedin_page.png"
    screenshot.save(temp_file)
    
    print(f"Screenshot captured: {temp_file}")
    return temp_file

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Tesseract extracted text: " + text)
    return text

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_message(groq, image_path):
    base64_image = encode_image(image_path)

    response = groq.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze the full LinkedIn page screenshot, focusing on the open chat window in the bottom right corner. 
                        Extract the most recent message in this chat window, including the sender's name, timestamp (if visible), and the full message content. 
                        If the message appears to be cut off, please indicate this in your extraction."""
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

def process_with_groq(image_path, api_key, general_instruction=None):
    client = Groq(api_key=api_key)

    text_analysis = extract_message(client, image_path)
    
    chat_history = []
    chat_history.append(
        {
            'role': 'assistant',
            'content': text_analysis 
        }
    )
    print("Open chat message analysis: " + text_analysis)
    chat_history.append(
            {
                "role": "user",
                "content": """Based on the extracted message from the open chat window, write a reply that:
                1. Is professional, enthusiastic, and confident.
                2. Shows genuine interest in the topic or opportunity mentioned (if applicable).
                3. Highlights relevant skills or experiences if appropriate to the context.
                4. Is concise but informative (2-4 sentences).
                5. Includes a call-to-action or next step if relevant.
                6. Uses a friendly, personable tone to build rapport.
                Respond with only the message text, without quotation marks or any additional context."""
            })
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=chat_history
    )
    return response.choices[0].message.content

def send_to_linkedin(response):
    pyautogui.typewrite(response)

def process_and_reply(general_instruction=None):
    try:
        print("Processing...")
        screenshot_path = capture_linkedin_page()
        if screenshot_path is None:
            print("Failed to capture LinkedIn page.")
            return

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        response = process_with_groq(screenshot_path, api_key, general_instruction)
        print("Groq's response:", response)

        response = response.replace('\n', '') 
        
        send_to_linkedin(response)
        print("Response sent to LinkedIn.")
        
#        os.remove(screenshot_path)
    except Exception as e:
        print(f"An error occurred: {e}")

def on_hotkey(general_instruction=None):
    threading.Thread(target=process_and_reply, args=(general_instruction,)).start()

def main():
    parser = argparse.ArgumentParser(description="LinkedIn chat analysis and response automation.")
    parser.add_argument("--instruction", type=str, help="Optional general instruction for the Groq call.")
    args = parser.parse_args()

    print("Starting LinkedIn chat analysis and response automation...")
    print("Select the LinkedIn window, then press Ctrl+Shift+L.")
    print("Press Ctrl+C to exit.")

    keyboard.add_hotkey('ctrl+shift+l', lambda: on_hotkey(args.instruction))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    client = Groq()
    print(extract_message(client, "temp_linkedin_page.png"))