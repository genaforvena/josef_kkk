import os
import json
import sys
from typing import List, Dict

import ollama
from form_extractor import extract_fields
from groq import Groq
import base64

def predict_text_generation_sample(content: str, api_key: str):
    """Predicts text generation with Groq API using Groq."""
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="llama3-8b-8192",
    )
    return response.choices[0].message.content


def fill_form_with_model(form_data: str, image_path: str, model: str):

    chat_history = []
    if model == 'ollama':
        prompt = f"""You are an assistant helping to fill out a German form. For each field in the form:
            1. Provide an English explanation of what the field means.
            2. Give an example of how to fill it out in German.
            3. If possible, provide a suggestion for filling out the field based on common responses.

            Here are the form fields:

            {json.dumps(form_data, indent=2)}

            Please format your response as JSON with the following structure for each field:
            {{
                "field_name": {{
                    "explanation": "English explanation here",
                    "example": "German example here",
                    "suggestion": "German suggestion here (if applicable)"
                }}
            }}
            """
        chat_history.append(
            {
                'role': 'user',
                'content': prompt
            }
        )

        print("Sending prompt to Ollama...")
        response = ollama.chat(model='llama3.2:1b', messages=chat_history)
        reply = response['message']['content']
    elif model == 'groq':
        api_key = os.getenv("GROQ_API_KEY", "")
        with open(image_path, "rb") as file:
            image_data = file.read()
        client = Groq(api_key=api_key)
        image_data_base64 = base64.b64encode(image_data).decode('utf-8')  # Encode to base64 and decode to string
        chat_history.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": ""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data_base64}"  # Use the base64 encoded string
                        }
                    }
                ]
            }
        )
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=chat_history,
            stream=False,
            stop=None
        )
        reply = completion.choices[0].message.content
        print("Image response: " + reply)
        chat_history.append(
            {
                'role': 'assistant',
                'content': reply
            }
        )
        prompt = f"""You are an assistant helping to fill out a German form. The image of the form is provided. Please process the image and provide step by step guide in JSON format with the following structure for each field:
        {{
            "field_name": {{
                "explanation": "English explanation here",
                "example": "German example here",
                "suggestion": "German suggestion here (if applicable)"
            }}
        }}
        """

        client = Groq()
        chat_history.append(
                    {
                        "role": "user",
                        "content": prompt
                    }
                )
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=chat_history,
            stream=False,
        )
        reply = completion.choices[0].message.content
    else:
        raise ValueError("Invalid model")

    return reply

def fill_form(image_path, model='ollama'):
    form_data = ''
    if model != 'groq':
        print("Original form data:")
        form_data = extract_fields(image_path)
        print(json.dumps(form_data, indent=2))
    
    filled_form = fill_form_with_model(form_data, image_path, model)
    
    print("\n\n\n-----------------------------------------")
    print("\nFilled form data:" + filled_form)
    
    return filled_form

def display_filled_form(filled_form):
    for field, data in filled_form.items():
        print(f"\n{field}:")
        print(f"  Explanation: {data['explanation']}")
        print(f"  Example: {data['example']}")
        if 'suggestion' in data:
            print(f"  Suggestion: {data['suggestion']}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        image_path = 'vision/visa.png'
        model = 'groq'
    else:
        image_path = sys.argv[1]
        model = sys.argv[2]
    
    fill_form(image_path, model)
