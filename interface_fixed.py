import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import messagebox
from queue import Queue
import threading

# Initialize speech queue and lock
speech_queue = Queue()
speech_lock = threading.Lock()

def speech_worker():
    """Worker thread for speech synthesis"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    
    while True:
        text = speech_queue.get()
        try:
            print(f"Nova mówi: {text}")
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Błąd syntezy mowy: {e}")
            try:
                messagebox.showwarning("Komunikat", text)
            except:
                print(text)
        speech_queue.task_done()

# Start speech worker thread
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def speak_to_user(text):
    """Add text to speech queue"""
    with speech_lock:
        speech_queue.put(text)

def list_microphones():
    """List available microphones"""
    print("Dostępne mikrofony:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone {index}: {name}")

def listen_to_user():
    """Listen to user's voice input and return as text"""
    r = sr.Recognizer()
    try:
        list_microphones()
        with sr.Microphone(device_index=0) as source:
            print("Słucham...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio, language="pl-PL")
        print("Rozpoznano: " + text)
        return text
    except sr.WaitTimeoutError:
        messagebox.showwarning("Timeout", "Nie wykryto żadnego dźwięku")
        return ""
    except sr.UnknownValueError:
        messagebox.showwarning("Błąd", "Nie rozpoznano mowy")
        return ""
    except sr.RequestError as e:
        messagebox.showerror("Błąd", f"Błąd usługi rozpoznawania mowy: {e}")
        return ""
    except Exception as e:
        messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {e}")
        return ""

def show_voice_error(message):
    """Show voice error message in GUI"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Błąd głosu", message)
    root.destroy()
