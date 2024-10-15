import pyttsx3
import threading

def init_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # You can change the voice by index. 0 is usually the default male voice, 1 is usually the default female voice.
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 150)  # Speed of speech
    return engine

def speak_stream(sentence_generator, stop_event):
    engine = init_engine()
    
    for sentence in sentence_generator:
        if stop_event.is_set():
            break
        print("Saying: " + sentence)
        engine.say(sentence)
        engine.runAndWait()
        if engine._inLoop:
            engine.endLoop()
    print("Done speaking...")

def speak_async(text):
    engine = init_engine()
    
    def run_speech():
        engine.say(text)
        engine.runAndWait()
        if engine._inLoop:
            engine.endLoop()
    
    thread = threading.Thread(target=run_speech)
    thread.start()
    return thread

if __name__ == "__main__":
    # Test the TTS
    speak_async("This is a test of the Windows text to speech engine.").join()