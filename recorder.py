import speech_recognition as sr
import pyaudio
import wave
import os
import time
from typing import Generator, Tuple

# Initialize recognizer
recognizer: sr.Recognizer = sr.Recognizer()

# Audio recording parameters
CHUNK: int = 1024
FORMAT: int = pyaudio.paInt16
CHANNELS: int = 1
RATE: int = 44100
RECORD_SECONDS: int = 5  # Reduced from 5 to 2 seconds for more responsive detection
WAVE_OUTPUT_FILENAME: str = "temp_audio.wav"

def record_audio() -> None:
    p: pyaudio.PyAudio = pyaudio.PyAudio()
    stream: pyaudio.Stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames: list = []
    
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data: bytes = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf: wave.Wave_write = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_and_translate() -> Generator[Tuple[str, str], None, None]:
    while True:
        record_audio()
        
        with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
            audio: sr.AudioData = recognizer.record(source)
        
        try:
            text: str = recognizer.recognize_google(audio)
            translation: str = ''
            yield (text, translation)
        except sr.UnknownValueError:
            yield ('.', '')  # Return empty strings if no speech is detected
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            yield ('.', '')
        
        # Remove temporary audio file
        os.remove(WAVE_OUTPUT_FILENAME)
        
        time.sleep(0.01)  # Short pause to prevent CPU overload

if __name__ == '__main__':
    for original, translation in transcribe_and_translate():
        if original:
            print(f"Original: {original}")
            print(f"Translation: {translation}")
            print("-----------------------")
        else:
            print("No speech detected")
