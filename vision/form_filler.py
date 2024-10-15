import os
import json
import sys
from typing import List, Dict

import ollama
from form_extractor import extract_fields
from google.api_core import client_options
from google.cloud import aiplatform_v1beta1 as aiplatform
def _get_client_options() -> client_options.ClientOptions:
    """Creates client options with endpoint set to use US region."""
    return client_options.ClientOptions(api_endpoint="us-central1-aiplatform.googleapis.com")


def predict_text_generation_sample(
    project_id: str,
    endpoint_id: str,
    content: str,
    location: str = "us-central1",
    api_key: str = None,  # Replace with your API key
):
    """Predicts text generation with a Large Language Model."""

    # Initialize the API client
    client_options = _get_client_options()
    client = aiplatform.PredictionServiceClient(client_options=client_options)

    endpoint = f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}"

    response = client.predict(
        endpoint=endpoint,
        instances=[{"content": content}],
        parameters={},
    )
    print(response.predictions)
    return response.predictions[0]["content"]


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
    elif model == 'gemini':
        project_id = os.getenv("PROJECT_ID", "")
        endpoint_id = os.getenv("ENDPOINT_ID", "")
        api_key = os.getenv("API_KEY", "")
        reply = predict_text_generation_sample(
            project_id=project_id, endpoint_id=endpoint_id, content=prompt, api_key=api_key
        )
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
        model = 'gemini'
    else:
        image_path = sys.argv[1]
        model = sys.argv[2]
    
    filled_form = fill_form(image_path, model)
    display_filled_form(filled_form)
