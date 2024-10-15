import ollama
from form_extractor import extract_fields
import sys
import json

def fill_form_with_llama(form_data):
    chat_history = []
    
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
    
    chat_history.append({
        'role': 'user',
        'content': prompt
    })
    
    print("Sending prompt to Ollama...")
    response = ollama.chat(model='llama3.2:1b', messages=chat_history)
    reply = response['message']['content']
    
    try:
        filled_form = json.loads(reply)
        return filled_form
    except json.JSONDecodeError:
        print("Error: Could not parse LLM response as JSON. Raw response:")
        print(reply)
        return {}

def fill_form(image_path):
    input_data = extract_fields(image_path)
    
    print("Original form data:")
    print(json.dumps(input_data, indent=2))
    
    filled_form = fill_form_with_llama(input_data)
    
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
    if len(sys.argv) != 2:
        image_path = 'visa.png'
    else:
        image_path = sys.argv[1]
    
    filled_form = fill_form(image_path)
    display_filled_form(filled_form)
