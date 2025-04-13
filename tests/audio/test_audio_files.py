import os
import soundfile as sf
import numpy as np

def test_audio_files():
    """Testuje wygenerowane pliki audio"""
    test_results = {}
    
    # Sprawdź czy pliki istnieją
    expected_files = [
        'audio-mono-16-bit-44100Hz.wav',
        'audio-mono-24-bit-44100Hz.wav',
        'audio-mono-32-bit-44100Hz.wav',
        'audio-stereo-16-bit-44100Hz.wav', 
        'audio-stereo-24-bit-44100Hz.wav',
        'audio-stereo-32-bit-44100Hz.wav'
    ]
    
    for file in expected_files:
        path = os.path.join('tests/audio', file)
        if not os.path.exists(path):
            test_results[file] = f"BŁĄD: Plik {file} nie istnieje"
            continue
            
        # Sprawdź parametry pliku
        try:
            data, samplerate = sf.read(path)
            test_results[file] = {
                'status': 'OK',
                'channels': data.shape[1] if len(data.shape) > 1 else 1,
                'samplerate': samplerate,
                'duration': len(data)/samplerate
            }
        except Exception as e:
            test_results[file] = f"BŁĄD: {str(e)}"
    
    # Wyświetl wyniki testów
    print("\n=== WYNIKI TESTÓW PLIKÓW AUDIO ===")
    for file, result in test_results.items():
        print(f"\nPlik: {file}")
        if isinstance(result, dict):
            print(f"Status: {result['status']}")
            print(f"Kanały: {result['channels']}")
            print(f"Sample rate: {result['samplerate']} Hz")
            print(f"Czas trwania: {result['duration']:.2f} s")
        else:
            print(f"Status: {result}")
    
    return test_results

if __name__ == '__main__':
    test_audio_files()
