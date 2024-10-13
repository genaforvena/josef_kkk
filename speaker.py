import pyttsx3
import threading
import comtypes.client

def speak_stream(stream_generator, stop_event):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    
    # Select a SAPI voice (you may need to adjust the index)
    engine.setProperty('voice', voices[1].id)  # Index 1 is often a female voice
    
    # Adjust speech rate (default is 200)
    engine.setProperty('rate', 150)  # Slower rate for more natural sound
    
    # Adjust volume (default is 1.0)
    engine.setProperty('volume', 0.9)  # Slightly lower volume
    
    # Use SAPI directly for more control
    sapi = comtypes.client.CreateObject("SAPI.SpVoice")
    sapi.Voice = sapi.GetVoices().Item(1)  # Adjust index if needed
    
    for text in stream_generator:
        if stop_event.is_set():
            break
        
        text = text.strip()
        
        if text:
            # Use SSML for more natural pauses and emphasis
            ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">' \
                   f'<prosody rate="slow" pitch="medium">{text}</prosody>' \
                   f'</speak>'
            sapi.Speak(ssml, 8)