import pyttsx3
import threading

def speak_stream(stream_generator, stop_event):
    engine = pyttsx3.init()
    
    for text in stream_generator:
        if stop_event.is_set():
            break
        
        # Remove any leading/trailing whitespace and newline characters
        text = text.strip()
        
        if text:
            engine.say(text)
            engine.runAndWait()
    
    engine.stop()
