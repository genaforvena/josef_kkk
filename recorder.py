import pyaudio
import wave
import os
import time
from groq import Groq

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

client = Groq()

def transcribe():
    with open(WAVE_OUTPUT_FILENAME, "rb") as file:
        transcription = client.audio.transcriptions.create(
        file=(WAVE_OUTPUT_FILENAME, file.read()),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        )
        yield transcription.text
        
def transcribe_and_translate():
    while True:
        record_audio()
        
        text: str = transcribe()
        yield text
        
        # Remove temporary audio file
        os.remove(WAVE_OUTPUT_FILENAME)
        
        time.sleep(0.01)  # Short pause to prevent CPU overload

if __name__ == '__main__':
    for original in transcribe_and_translate():
        if original:
            print(f"Original: {''.join(original)}")
            print("-----------------------")
        else:
            print("No speech detected")
