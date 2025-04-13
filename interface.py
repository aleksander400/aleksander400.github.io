import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import messagebox
import time

def list_microphones():
    """List available microphones with proper encoding"""
    print("Dostępne mikrofony:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        try:
            name = name.encode('latin1').decode('cp1250')
        except:
            pass
        print(f"Microphone {index}: {name}")

def listen_to_user():
    """Improved voice recognition with multiple attempts and microphone testing"""
    r = sr.Recognizer()
    max_attempts = 3
    mics = sr.Microphone.list_microphone_names()
    
    for attempt in range(max_attempts):
        try:
            # Try different microphones
            for device_index in [None] + list(range(len(mics))):
                try:
                    with sr.Microphone(device_index=device_index) as source:
                        print(f"Próba {attempt+1}: Słucham (mikrofon {device_index})...")
                        r.adjust_for_ambient_noise(source, duration=0.5)
                        audio = r.listen(source, timeout=3, phrase_time_limit=3)
                        text = r.recognize_google(audio, language="pl-PL")
                        print("Rozpoznano:", text)
                        return text
                except Exception as e:
                    print(f"Błąd mikrofonu {device_index}: {str(e)}")
                    continue
            
            print("Nie udało się użyć żadnego mikrofonu, próbuję ponownie...")
            
        except sr.UnknownValueError:
            print("Nie rozpoznano mowy")
        except sr.RequestError as e:
            print("Błąd usługi rozpoznawania:", e)
        except Exception as e:
            print("Nieoczekiwany błąd:", e)
            
        if attempt < max_attempts - 1:
            print("Ponowna próba za 1 sekundę...")
            time.sleep(1)
    
    print("Przekroczono maksymalną liczbę prób")
    return ""

def speak_to_user(text):
    """Speak the given text using text-to-speech"""
    def _speak():
        try:
            print(f"Nova mówi: {text}")
            # Create new engine instance for each call
            local_engine = pyttsx3.init()
            local_engine.setProperty('rate', 150)
            voices = local_engine.getProperty('voices')
            # Try to find Polish voice if available
            for voice in voices:
                if 'polish' in voice.languages or 'pl' in voice.languages:
                    local_engine.setProperty('voice', voice.id)
                    break
            else:
                local_engine.setProperty('voice', voices[0].id)
                
            local_engine.say(text)
            local_engine.runAndWait()
            local_engine.stop()
        except Exception as e:
            print(f"Błąd syntezy mowy: {e}")
            try:
                # Fallback to simple print if TTS fails
                messagebox.showwarning("Komunikat", text)
            except:
                print(text)

    # Run in separate thread to avoid GIL issues
    import threading
    t = threading.Thread(target=_speak)
    t.daemon = True
    t.start()

def show_voice_error(message):
    """Show voice error message in GUI"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Błąd głosu", message)
    root.destroy()
