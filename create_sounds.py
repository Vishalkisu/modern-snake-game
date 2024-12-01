import wave
import struct
import math

def create_beep(filename, frequency=440, duration=0.1, volume=0.5):
    # Audio parameters
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Create WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Generate samples
        for i in range(num_samples):
            t = float(i) / sample_rate
            sample = volume * math.sin(2 * math.pi * frequency * t)
            # Convert to 16-bit integer
            packed_value = struct.pack('h', int(sample * 32767.0))
            wav_file.writeframes(packed_value)

# Create eat sound (higher pitch, shorter duration)
create_beep('sounds/eat.wav', frequency=880, duration=0.1, volume=0.3)

# Create crash sound (lower pitch, longer duration)
create_beep('sounds/crash.wav', frequency=220, duration=0.3, volume=0.4)

print("Sound files created successfully!")
