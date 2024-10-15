import pyaudio
import wave
import os
import time
import threading
import queue
from groq import Groq

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

class AudioRecorder:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()
        self.stop_recording = threading.Event()
        self.client = Groq()

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        while not self.stop_recording.is_set():
            data = stream.read(CHUNK)
            self.audio_queue.put(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio(self, frames):
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def transcribe(self):
        with open(WAVE_OUTPUT_FILENAME, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(WAVE_OUTPUT_FILENAME, file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
            )
            return transcription.text

    def transcribe_audio(self):
        while not self.stop_recording.is_set():
            frames = []
            start_time = time.time()
            
            while time.time() - start_time < 5 and not self.stop_recording.is_set():  # Collect 5 seconds of audio
                try:
                    frames.append(self.audio_queue.get(timeout=0.1))
                except queue.Empty:
                    continue
            
            if frames:
                self.save_audio(frames)
                text = self.transcribe()
                if text:
                    self.transcription_queue.put(text)
                os.remove(WAVE_OUTPUT_FILENAME)

    def continuous_transcribe(self):
        self.stop_recording.clear()
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()

        record_thread = threading.Thread(target=self.record_audio)
        transcribe_thread = threading.Thread(target=self.transcribe_audio)

        record_thread.start()
        transcribe_thread.start()

        try:
            while not self.stop_recording.is_set():
                try:
                    yield self.transcription_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
        finally:
            self.stop_recording.set()
            record_thread.join()
            transcribe_thread.join()

    def stop(self):
        self.stop_recording.set()

recorder = AudioRecorder()

def continuous_transcribe():
    return recorder.continuous_transcribe()

def stop_recording():
    recorder.stop()