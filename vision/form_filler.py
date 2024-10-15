import os
import json
import sys
from typing import List, Dict

import ollama
from vision.form_extractor import extract_fields
from groq import Groq

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


def fill_form_with_model(image_path: str, model: str):
    if model == 'ollama':
        form_data = extract_fields(image_path)
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
        chat_history = []

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
        prompt = f"""You are an assistant helping to fill out a German form. The image of the form is provided. Please process the image and provide the filled form data in JSON format with the following structure for each field:
        {{
            "field_name": {{
                "explanation": "English explanation here",
                "example": "German example here",
                "suggestion": "German suggestion here (if applicable)"
            }}
        }}
        """
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llava-v1.5-7b-4096-preview",
            messages=[
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
                                "url": f"data:image/jpeg;base64,{image_data.encode('base64')}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        reply = completion.choices[0].message
    else:
        raise ValueError("Invalid model")

    return reply

def fill_form(image_path, model='ollama'):
    print("Original form data:")
    print(json.dumps(extract_fields(image_path), indent=2))
    
    filled_form = fill_form_with_model(image_path, model)
    
    print("\n\n\n-----------------------------------------")
    print("\nFilled form data:")
    
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
    
    print(fill_form(image_path, model))
