import speech_recognition as sr
import pyttsx3
import anthropic
import json
import os
from datetime import datetime

# Configure Anthropic API (ensure you've set your API key as an environment variable)
client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

class AICallAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.conversation_history = []

    def transcribe_audio(self):
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
        
        messages = [
            {"role": "system", "content": "Du bist ein KI-Assistent, der bei einem Telefonat mit der deutschen Bürokratie hilft. Bitte antworte immer auf Deutsch und gib präzise, relevante Antworten."},
            *self.conversation_history
        ]
        
        response = client.messages.create(
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

    def run(self):
        print("Anruf gestartet. Was ist das Ziel dieses Gesprächs?")
        goal = input()
        self.conversation_history.append({"role": "system", "content": f"Das Ziel des Benutzers für dieses Gespräch ist: {goal}"})
        
        print("Der Anrufassistent ist bereit. Beginnen Sie Ihr Gespräch.")
        
        while True:
            agent_speech = self.transcribe_audio()
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

if __name__ == "__main__":
    assistant = AICallAssistant()
    assistant.run()