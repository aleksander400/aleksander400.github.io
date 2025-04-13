import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import messagebox
from queue import Queue
import threading

# Initialize speech engine and queue
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
    recognizer = sr.Recognizer()
    try:
        mics = sr.Microphone.list_working_microphones()
        if not mics:
            print("Nie znaleziono działających mikrofonów")
            return []
        print(f"Dostępne mikrofony: {list(mics.keys())}")
        return list(mics.keys())
    except Exception as e:
        print(f"Błąd podczas wyszukiwania mikrofonów: {e}")
        return []

def listen_to_user(timeout=5):
    """Listen to user voice input"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    try:
        with mic as source:
            print("Słucham...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
            
        try:
            text = recognizer.recognize_google(audio, language="pl-PL")
            print(f"Rozpoznano: {text}")
            return text
        except sr.UnknownValueError:
            print("Nie rozpoznano mowy")
            return None
        except sr.RequestError as e:
            print(f"Błąd usługi rozpoznawania mowy: {e}")
            return None
            
    except Exception as e:
        print(f"Błąd nasłuchiwania: {e}")
        return None

def show_voice_error():
    """Show voice error message"""
    messagebox.showerror(
        "Błąd głosu", 
        "Wystąpił problem z rozpoznawaniem mowy. Sprawdź mikrofon i spróbuj ponownie."
    )
