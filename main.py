import os
import recorder
import threading
import queue
import ollama
from windows_speaker import speak_async_sapi
import re
import argparse
from groq import Groq

def predict_text_generation_sample(chat_history: list, api_key: str):
    """Predicts text generation with Groq API using Groq."""
    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        messages=chat_history,
        model="llama-3.1-8b-instant",
    )
    return response.choices[0].message.content

def collect_input(input_queue, stop_event):
    collected_text = ""
    for original, translation in recorder.transcribe_and_translate():
        if stop_event.is_set():
            break
        collected_text += original
        print(f"Recorded: {original}")
        print("-----------------------")
        if not input_queue.empty():
            return collected_text
    return collected_text

def stream_ollama_response(client, model, messages, stop_event):
    stream = client.chat(model=model, messages=messages, stream=True)
    
    for chunk in stream:
        if stop_event.is_set():
            break
        if 'message' in chunk:
            yield chunk['message']['content']

def paragraph_generator(text_stream):
    paragraph = ""
    for chunk in text_stream:
        paragraph += chunk
        if '\n\n' in paragraph:
            parts = paragraph.split('\n\n')
            for part in parts[:-1]:
                yield part.strip()
            paragraph = parts[-1]
    if paragraph:
        yield paragraph.strip()

def main(instruction, self_talk, model='ollama'):
    print("Starting conversation...")
    
    input_queue = queue.Queue()
    conversation_history = []
    second_conversation_history = []
    client = ollama.Client()
    recording_stop_event = threading.Event()

    # Add initial system message to set the behavior
    conversation_history.append({
        'role': 'system',
        'content': instruction
    })
    if self_talk:
        second_conversation_history.append({
            'role': 'system',
            'content': "Reply only in English as a German beuracrat. Speak only English!" 
        })
    
    collected_text = ''
    second_response = ''
    while True:
        if not self_talk:
            print("Press Enter to stop speech recognition and get Ollama's response...")
            input_thread = threading.Thread(target=lambda q: q.put(input()), args=(input_queue,))
            input_thread.start()

            recording_stop_event.clear()
            collected_text = collect_input(input_queue, recording_stop_event)
            
            input_thread.join()
            input_queue.get()  # Clear the queue
            recording_stop_event.set()  # Stop recording when Enter is pressed
        else:
            if len(second_response) == 0:
                collected_text = "Ask as Ilya Mozerov"
            else:
                collected_text = "Reply to the following as Ilya Mozerov: " + second_response
            
        if collected_text:
            print("Ollama prompt: " + collected_text)
            conversation_history.append({
                'role': 'user',
                'content': collected_text
            })

            print("\nProcessing collected text with Ollama (llama3.2 model)...")
            print("\nOllama's response:")
            print("Press Space to stop the response..." if not self_talk else "Generating response...")

            stop_event = threading.Event()
            if model == 'ollama':
                response_stream = stream_ollama_response(client, 'llama3.2', conversation_history, stop_event)
            elif model == 'groq':
                api_key = os.getenv("GROQ_API_KEY", "")
                response_stream = predict_text_generation_sample(conversation_history, api_key)
            else:
                raise ValueError("Invalid model")

            first_response = ''.join(response_stream)
            
            print("Ilya says: " + first_response)
            speak_async_sapi(first_response).join()

            # Add Ollama's response to conversation history
            if not self_talk:
                message_to_append = first_response
                conversation_history.append({
                    'role': 'assistant',
                    'content': message_to_append
                })
            else:
                # Ensure first_response is added to second_conversation_history
                second_conversation_history.append({
                    'role': 'assistant',
                    'content': first_response  # This line ensures the response is recorded
                })
                message_to_append = "Reply to the message: " + first_response
                second_conversation_history.append({
                    'role': 'user',
                    'content': message_to_append 
                })
                
            # Ensure that the first_response is used in the next iteration
            collected_text = first_response  # Use first_response as input for next iteration

            if self_talk:
                recording_stop_event.clear()

                print("\nGenerating second response...")
                stop_event.clear()
                if model == 'ollama':
                    second_response_stream = stream_ollama_response(client, 'llama3.2:1b', second_conversation_history, stop_event)
                elif model == 'groq':
                    second_response_stream = predict_text_generation_sample(second_conversation_history, api_key)
                else:
                    raise ValueError("Invalid model")

                
                second_response = ''.join(second_response_stream)

                print("Germany says: " + second_response)
                speak_async_sapi(second_response).join() 

                conversation_history.append({'role': 'assistant', 'content': second_response})
                second_conversation_history.append({'role': 'assistant', 'content': second_response})
                collected_text = second_response  # Use second response as input for next iteration
                recording_stop_event.clear()

            print("\n\nResponse ended.")

        if not self_talk:
            print("\nContinue speaking. Press Enter to stop speech recognition and get the next response...")
            recording_stop_event.clear()

    # Don't forget to stop and join the speaker thread at the end
    if speak_thread:
        speak_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ollama conversation script")
    parser.add_argument("--instruction", type=str, default="You are Ilya Mozerov in phone conversation with German bureaucracy. You speak only in English, inquiring how to get citizenship. Your replies contain only Ilya's speech.", 
                        help="Instruction for Ollama's behavior")
    parser.add_argument("--self-talk", default=True, action="store_true", help="Self-talking mode.")
    parser.add_argument("--model", type=str, default="groq", choices=["ollama", "groq"], help="Model to use for text generation")
    args = parser.parse_args()
    
    main(args.instruction, args.self_talk, args.model)
