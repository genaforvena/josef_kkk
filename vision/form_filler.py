import ollama
from form_extractor import extract_fields
import sys

def fill_form_with_llama(form_data):
    # Initialize the chat history
    chat_history = []
    
    filled_form = {}
    for i in range(0, len(form_data)):
        chunk = form_data[i]
        prompt = f"Please explain each field in English and fill out the following form fields with fictional data in German:\n\n"
        for field in chunk:
            prompt += f"{field}\n"
        
        # Add the prompt to the chat history
        chat_history.append({
            'role': 'user',
            'content': prompt
        })
        
        print("Prompt: " + prompt)
        # Call the Ollama API to generate a response
        response = ollama.chat(model='llama3.2:1b', messages=chat_history)
        reply = response['message']['content']
        print("Response: \n" + reply)
        
        # Update the chat history with the response
        chat_history.append({
            'role': 'assistant',
            'content': reply})
        
        # Parse the response and update the form data
        for line in reply.split('\n'):
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
        fill_form('https://asserts-marketing.s3.eu-central-1.amazonaws.com/Public/Blog+Images/steuererklaerung.de/muster-lstb-2023.jpg') 
    else:
        fill_form(sys.argv[1])