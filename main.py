import speech_recognition as sr
from googletrans import Translator
import threading
import pyaudio
import wave
import os
import time

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

# Function to record audio
def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("* Recording")
    frames = []
    
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("* Done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe and translate
def transcribe_and_translate():
    while True:
        record_audio()
        
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            translation = translator.translate(text, dest='en')
            print(f"Original: {text}")
            print(f"Translation: {translation.text}")
            print("-----------------------")
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
        
        # Remove temporary audio file
        os.remove(WAVE_OUTPUT_FILENAME)
        
        time.sleep(0.1)  # Short pause to prevent CPU overload

# Start the transcription and translation process
transcribe_and_translate()