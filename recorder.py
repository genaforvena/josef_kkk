import speech_recognition as sr
import threading
import pyaudio
import wave
import os
import time
from typing import Generator, Tuple  

# Initialize recognizer and translator
recognizer: sr.Recognizer = sr.Recognizer()

# Audio recording parameters
CHUNK: int = 1024
FORMAT: int = pyaudio.paInt16
CHANNELS: int = 1
RATE: int = 44100
RECORD_SECONDS: int = 5
WAVE_OUTPUT_FILENAME: str = "temp_audio.wav"

# Function to record audio
def record_audio() -> None:
    p: pyaudio.PyAudio = pyaudio.PyAudio()
    stream: pyaudio.Stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("* Recording")
    frames: list = []
    
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data: bytes = stream.read(CHUNK)
        frames.append(data)
    
    print("* Done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf: wave.Wave_write = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to transcribe and translate
def transcribe_and_translate() -> Generator[Tuple[str, str], None, None]:
    while True:
        record_audio()
        
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio: sr.AudioData = recognizer.record(source)
        
        try:
            text: str = recognizer.recognize_google(audio)
            translation: str = ''
 #           if len(text) > 1:
#                translation: str = translator.translate(text, dest='en').text
            yield (text, translation)
            print(f"Original: {text}")
            print(f"Translation: {translation}")
            print("-----------------------")
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
        
        # Remove temporary audio file
        os.remove(WAVE_OUTPUT_FILENAME)
        
        time.sleep(0.1)  # Short pause to prevent CPU overload

if __name__ == '__main__':
    transcribe_and_translate()
