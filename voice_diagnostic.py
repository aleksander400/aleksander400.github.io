import speech_recognition as sr
import pyttsx3
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_diagnostic.log'),
        logging.StreamHandler()
    ]
)

def test_microphones():
    """Test all available microphones"""
    r = sr.Recognizer()
    mics = sr.Microphone.list_microphone_names()
    
    print("\nTesting microphones:")
    for i, name in enumerate(mics):
        try:
            print(f"\nMicrophone {i}: {name}")
            with sr.Microphone(device_index=i) as source:
                print("Adjusting for noise...")
                r.adjust_for_ambient_noise(source)
                print("Say something...")
                audio = r.listen(source, timeout=3, phrase_time_limit=3)
                
                try:
                    text = r.recognize_google(audio, language="pl-PL")
                    print(f"Recognized: {text}")
                    return i  # Return first working microphone
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Recognition error: {e}")
                    
        except Exception as e:
            print(f"Microphone {i} error: {e}")
    
    return None

def test_tts():
    """Test text-to-speech"""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        print("\nTesting TTS...")
        engine.say("Test syntezy mowy")
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"TTS error: {e}")
        return False

if __name__ == "__main__":
    print("Starting voice system diagnostics...")
    
    # Test TTS first
    if not test_tts():
        print("\nTTS test failed!")
    else:
        print("\nTTS test passed!")
    
    # Test microphones
    working_mic = test_microphones()
    if working_mic is not None:
        print(f"\nWorking microphone found: {working_mic}")
    else:
        print("\nNo working microphones found!")
    
    print("\nCheck voice_diagnostic.log for detailed logs")
