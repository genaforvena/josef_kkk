import win32com.client
import pythoncom
import threading

def get_voices():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    voices = speaker.GetVoices()
    
    voice_list = []
    for voice in voices:
        voice_list.append({
            'name': voice.GetAttribute("Name"),
            'languages': voice.GetAttribute("Language").split(';')
        })
    
    pythoncom.CoUninitialize()
    return voice_list

def find_multilingual_voice(languages):
    return get_voices()

def speak_sapi(text, voice_name=None):
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    
    if voice_name:
        voices = speaker.GetVoices()
        for voice in voices:
            if voice.GetAttribute("Name") == voice_name:
                speaker.Voice = voice
                break
    
    speaker.Speak(text)
    pythoncom.CoUninitialize()

def speak_async_sapi(text, voice_name="Microsoft Zira Desktop"):
    thread = threading.Thread(target=speak_sapi, args=(text, voice_name))
    thread.start()
    return thread

if __name__ == "__main__":
    voice = "Microsoft Zira Desktop"
    print(f"Found multilingual voice: {voice}")
    print("Speaking English:")
    speak_async_sapi("This is a test of the Windows Speech API in English.", voice).join()
    print("Speaking German:")
    speak_async_sapi("Dies ist ein Test der Windows Speech API auf Deutsch.", voice).join()