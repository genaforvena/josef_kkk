import os
import json
import sys
from typing import List, Dict

import ollama
from form_extractor import extract_fields
from groq import GroqClient
def predict_text_generation_sample(content: str, api_key: str):
    """Predicts text generation with Groq API using GroqClient."""
    client = GroqClient(api_key=api_key)
    response = client.generate(prompt=content)
    return response["content"]


def fill_form_with_model(form_data: List[Dict], model: str):
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
    if model == 'ollama':
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
        reply = predict_text_generation_sample(content=prompt, api_key=api_key)
    else:
        raise ValueError("Invalid model")

    try:
        filled_form = json.loads(reply)
        return filled_form
    except json.JSONDecodeError:
        print("Error: Could not parse LLM response as JSON. Raw response:")
        print(reply)
        return {}

def fill_form(image_path, model='ollama'):
    input_data = extract_fields(image_path)
    
    print("Original form data:")
    print(json.dumps(input_data, indent=2))
    
    filled_form = fill_form_with_model(input_data, model)
    
    print("\nFilled form data:")
    print(json.dumps(filled_form, indent=2))
    
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
    
    filled_form = fill_form(image_path, model)
    display_filled_form(filled_form)
