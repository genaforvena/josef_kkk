import recorder
import threading
import queue
import ollama
import json
from speaker import speak_stream
import re
import argparse

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

def sentence_generator(text_stream):
    sentence = ""
    for chunk in text_stream:
        sentence += chunk
        sentences = re.split(r'(?<=[.!?])\s+', sentence)
        if len(sentences) > 1:
            for s in sentences[:-1]:
                yield s.strip()
            sentence = sentences[-1]
    if sentence:
        yield sentence.strip()

def main(instruction, use_second_response):
    print("Starting conversation. Press Enter to stop speech recognition and get Ollama's response...")
    
    input_queue = queue.Queue()
    conversation_history = []
    client = ollama.Client()
    recording_stop_event = threading.Event()

    # Add initial system message to set the behavior
    conversation_history.append({
        'role': 'system',
        'content': instruction
    })

    while True:
        if not use_second_response:
            input_thread = threading.Thread(target=lambda q: q.put(input()), args=(input_queue,))
            input_thread.start()

            recording_stop_event.clear()
            collected_text = collect_input(input_queue, recording_stop_event)
            
            input_thread.join()
            input_queue.get()  # Clear the queue
            recording_stop_event.set()  # Stop recording when Enter is pressed
        else:
            collected_text = "Continue the conversation."

        if collected_text:
            print("Ollama prompt: " + collected_text)
            conversation_history.append({
                'role': 'user',
                'content': collected_text
            })

            print("\nProcessing collected text with Ollama (llama3.2 model)...")
            print("\nOllama's response:")
            print("Press Space to stop the response..." if not use_second_response else "Generating response...")

            stop_event = threading.Event()
            response_stream = stream_ollama_response(client, 'llama3.2', conversation_history, stop_event)
            sentence_stream = sentence_generator(response_stream)
            
            speak_thread = threading.Thread(target=speak_stream, args=(sentence_stream, stop_event))
            speak_thread.start()

            while speak_thread.is_alive():
                if input() == ' ':
                    stop_event.set()
                    break

            speak_thread.join()

            # Add Ollama's response to conversation history
            conversation_history.append({
                'role': 'assistant',
                'content': ' '.join(sentence_stream) 
            })

            if use_second_response:
                print("\nGenerating second response...")
                stop_event.clear()
                second_response_stream = stream_ollama_response(client, 'llama3.2:1b', conversation_history, stop_event)
                second_sentence_stream = sentence_generator(second_response_stream)
                
                speak_thread = threading.Thread(target=speak_stream, args=(second_sentence_stream, stop_event))
                speak_thread.start()

                while speak_thread.is_alive():
                    if input() == ' ':
                        stop_event.set()
                        break

                speak_thread.join()

                conversation_history.append({'role': 'user', 'content': ' '.join(second_sentence_stream) })

            print("\n\nResponse ended.")

        if not use_second_response:
            print("\nContinue speaking. Press Enter to stop speech recognition and get the next response...")
            recording_stop_event.clear()
        else:
            print("\nPress Enter to continue the conversation between Ollamas...")
            input()  # Wait for Enter press before continuing

    # Don't forget to stop and join the speaker thread at the end
    speaker.stop()
    speaker.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ollama conversation script")
    parser.add_argument("--instruction", type=str, default="You are Ilya Mozerov. You are in a phone conversation with German bureaucracy. You reply and speak only in English. Reply naturally as if human would.", 
                        help="Instruction for Ollama's behavior")
    parser.add_argument("--use_second_response", action="store_true", help="Use second response as input for next iteration")
    args = parser.parse_args()
    
    main(args.instruction, args.use_second_response)
