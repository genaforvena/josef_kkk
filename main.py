import recorder
import threading
import queue
import ollama
import json
from speaker import speak_stream
import re

def collect_input(input_queue):
    collected_text = ""
    for original, translation in recorder.transcribe_and_translate():
        collected_text += f"Original: {original}\nTranslation: {translation}\n\n"
        print(f"Original: {original}")
        print(f"Translation: {translation}")
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

def main():
    print("Starting conversation. Press Enter to get Ollama's response...")
    
    input_queue = queue.Queue()
    conversation_history = []
    client = ollama.Client()

    while True:
        input_thread = threading.Thread(target=lambda q: q.put(input()), args=(input_queue,))
        input_thread.start()

        collected_text = collect_input(input_queue)
        
        input_thread.join()
        input_queue.get()  # Clear the queue

        if collected_text:
            conversation_history.append({
                'role': 'user',
                'content': collected_text
            })

            print("\nProcessing collected text with Ollama (llama3.2:1b model)...")
            print("\nOllama's response:")
            print("Press Space to stop the response...")

            stop_event = threading.Event()
            response_stream = stream_ollama_response(client, 'llama3.2:1b', conversation_history, stop_event)
            sentence_stream = sentence_generator(response_stream)
            
            response_thread = threading.Thread(target=lambda: [print(sentence, end=' ', flush=True) for sentence in sentence_stream])
            response_thread.start()

            speak_thread = threading.Thread(target=speak_stream, args=(sentence_generator(stream_ollama_response(client, 'llama3.2:1b', conversation_history, stop_event)), stop_event))
            speak_thread.start()

            while response_thread.is_alive() or speak_thread.is_alive():
                if input() == ' ':
                    stop_event.set()
                    break

            response_thread.join()
            speak_thread.join()

            # Add Ollama's response to conversation history
            conversation_history.append({
                'role': 'assistant',
                'content': ''.join(stream_ollama_response(client, 'llama3.2:1b', conversation_history, threading.Event()))
            })

            print("\n\nResponse ended.")

        print("\nContinue speaking. Press Enter for the next response...")

if __name__ == "__main__":
    main()
