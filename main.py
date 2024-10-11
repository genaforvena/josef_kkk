import speech_recognition as sr
import pyttsx3
import anthropic
import json
import os
import requests
from datetime import datetime

class AICallAssistant:
    def __init__(self, use_ollama=False, ollama_model="llama2"):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.conversation_history = []
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        
        if not self.use_ollama:
            self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def transcribe_audio(self, audio_file=None):
        if audio_file:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
        else:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
        
        try:
            text = self.recognizer.recognize_google(audio, language="de-DE")
            print("Transcribed: ", text)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""

    def generate_response(self, user_input):
        self.conversation_history.append({"role": "human", "content": user_input})
        
        if self.use_ollama:
            prompt = "Du bist ein KI-Assistent, der bei einem Telefonat mit der deutschen Bürokratie hilft. Bitte antworte immer auf Deutsch und gib präzise, relevante Antworten.\n\n"
            for message in self.conversation_history:
                prompt += f"{message['role'].capitalize()}: {message['content']}\n"
            prompt += "Assistant: "

            response = requests.post('http://localhost:11434/api/generate', 
                                     json={
                                         "model": self.ollama_model,
                                         "prompt": prompt,
                                         "stream": False
                                     })
            if response.status_code == 200:
                ai_response = response.json()['response']
            else:
                ai_response = "Error: Could not generate response from Ollama."
        else:
            messages = [
                {"role": "system", "content": "Du bist ein KI-Assistent, der bei einem Telefonat mit der deutschen Bürokratie hilft. Bitte antworte immer auf Deutsch und gib präzise, relevante Antworten."},
                *self.conversation_history
            ]
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                messages=messages,
                max_tokens=300
            )
            
            ai_response = response.content[0].text
        
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response

    def text_to_speech(self, text):
        self.engine.setProperty('voice', 'german')
        self.engine.say(text)
        self.engine.runAndWait()

    def save_transcript(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gespraechsprotokoll_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        print(f"Protokoll gespeichert als {filename}")

    def run(self, audio_file=None):
        print("Anruf gestartet. Was ist das Ziel dieses Gesprächs?")
        goal = input()
        self.conversation_history.append({"role": "system", "content": f"Das Ziel des Benutzers für dieses Gespräch ist: {goal}"})
        
        print("Der Anrufassistent ist bereit. Beginnen Sie Ihr Gespräch.")
        
        while True:
            agent_speech = self.transcribe_audio(audio_file)
            if agent_speech:
                print("Agent:", agent_speech)
                suggested_response = self.generate_response(agent_speech)
                print("Vorgeschlagene Antwort:", suggested_response)
                
                user_choice = input("Diese Antwort verwenden? (j/n/ä für ändern): ").lower()
                if user_choice == 'j':
                    self.text_to_speech(suggested_response)
                elif user_choice == 'n':
                    custom_response = input("Geben Sie Ihre Antwort ein: ")
                    self.text_to_speech(custom_response)
                    self.conversation_history.append({"role": "assistant", "content": custom_response})
                else:
                    modified_response = input("Geben Sie die geänderte Antwort ein: ")
                    self.text_to_speech(modified_response)
                    self.conversation_history.append({"role": "assistant", "content": modified_response})
            
            if input("Fortfahren? (j/n): ").lower() != 'j':
                break
        
        print("Anruf beendet.")
        self.save_transcript()

def check_ollama_model(model_name):
    response = requests.get(f'http://localhost:11434/api/show', params={'name': model_name})
    return response.status_code == 200

def download_ollama_model(model_name):
    print(f"Downloading Ollama model {model_name}...")
    response = requests.post('http://localhost:11434/api/pull', json={'name': model_name, 'stream': False})
    if response.status_code == 200:
        print(f"Model {model_name} downloaded successfully.")
    else:
        print(f"Failed to download model {model_name}. Error: {response.text}")

if __name__ == "__main__":
    use_ollama = input("Use Ollama for local testing? (y/n): ").lower() == 'y'
    
    if use_ollama:
        ollama_model = input("Enter Ollama model name (default: llama2): ") or "llama2"
        if not check_ollama_model(ollama_model):
            if input(f"Model {ollama_model} not found. Download it? (y/n): ").lower() == 'y':
                download_ollama_model(ollama_model)
            else:
                print("Exiting as the required model is not available.")
                exit()
    else:
        ollama_model = None

    audio_file = input("Enter path to audio file (or press Enter to use microphone): ").strip() or None
    
    assistant = AICallAssistant(use_ollama=use_ollama, ollama_model=ollama_model)
    assistant.run(audio_file)