import os
import numpy as np
import soundfile as sf

SAMPLE_RATE = 44100
DURATION = 1.0  # 1 second files
AMPLITUDE = 0.5

def generate_sine_wave(freq, sample_rate, duration):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return AMPLITUDE * np.sin(2 * np.pi * freq * t)

def generate_test_files():
    # Create directory if not exists
    os.makedirs('tests/audio', exist_ok=True)
    
    # Generate WAV files (only 16, 24, 32 bit as PCM_8 is not supported)
    for bits in [16, 24, 32]:
        for channels in ['mono', 'stereo']:
            filename = f'tests/audio/audio-{channels}-{bits}-bit-44100Hz.wav'
            if channels == 'mono':
                data = generate_sine_wave(440, SAMPLE_RATE, DURATION)  # A4 note
            else:
                left_channel = generate_sine_wave(440, SAMPLE_RATE, DURATION)  # A4
                right_channel = generate_sine_wave(880, SAMPLE_RATE, DURATION)  # A5
                data = np.column_stack((left_channel, right_channel))
            sf.write(
                filename,
                data,
                SAMPLE_RATE,
                subtype=f'PCM_{bits}'
            )
    
    print("Test audio files generated successfully")

if __name__ == '__main__':
    generate_test_files()
