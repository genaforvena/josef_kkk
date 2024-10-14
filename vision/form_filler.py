import ollama
from form_extractor import extract_fields
import sys

def fill_form_with_llama(form_data):
    # Prepare the prompt for the language model
    prompt = "Explain the purpose of the following form and provide an example of how to fill it out with fictional data:\n\n"
    for (field, value) in form_data:
        prompt += f"{field}: {value}\n"
    
    # Call the Ollama API to generate a response
    response = ollama.generate(model='llama3.2:1b', prompt=prompt)
    
    # Parse the response and update the form data
    filled_form = {}
    for line in response['response'].split('\n'):
        if ':' in line:
            field, value = line.split(':', 1)
            filled_form[field.strip()] = value.strip()
    
    return filled_form

def fill_form(image_path):
    # Get the input data
    input_data = extract_fields(image_path) 
    
    print("Original form data:")
    print(input_data)
    
    # Fill the form using the Ollama model
    filled_form = fill_form_with_llama(input_data)
    
    print("\nFilled form data:")
    print(filled_form)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
    else:
        fill_form(sys.argv[1])