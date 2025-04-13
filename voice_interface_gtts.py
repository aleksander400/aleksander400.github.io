from gtts import gTTS
import playsound
import tempfile
import os
import logging

class VoiceInterface:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def speak(self, text, lang='pl'):
        """Convert text to speech using gTTS"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_path = f.name
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_path)
            
            # Play audio
            playsound.playsound(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
        except Exception as e:
            self.logger.error(f"Error in speech synthesis: {e}")

# Test
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    vi = VoiceInterface()
    vi.speak("Test finalnej implementacji syntezy mowy")
