import time
import numpy as np
import pyaudio
import config


def start_stream(callback):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(config.MIC_RATE / config.FPS)
    
    # Try to open audio stream with error handling for sample rate
    stream = None
    
    # First, try to find and use the specific device (HD Pro Webcam C920)
    input_device_index = None
    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        if dev_info['maxInputChannels'] > 0:
            print(f"Found input device {i}: {dev_info['name']}")
            if input_device_index is None:
                input_device_index = i
                print(f"  → Using this device")
    
    sample_rates_to_try = [config.MIC_RATE, 16000, 48000, 44100]
    
    for rate in sample_rates_to_try:
        try:
            print(f"Trying to open audio stream at {rate} Hz...")
            stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=rate,
                          input=True,
                          input_device_index=input_device_index,
                          frames_per_buffer=int(rate / config.FPS))
            config.MIC_RATE = rate  # Update config with working rate
            frames_per_buffer = int(rate / config.FPS)
            print(f"✓ Audio stream opened successfully at {rate} Hz")
            break
        except (OSError, IOError) as e:
            print(f"✗ Failed at {rate} Hz: {e}")
            continue
    
    if stream is None:
        p.terminate()
        raise RuntimeError("Could not open audio stream at any sample rate. Check your microphone connection.")
    
    overflows = 0
    prev_ovf_time = time.time()
    while True:
        try:
            y = np.fromstring(stream.read(frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
            y = y.astype(np.float32)
            stream.read(stream.get_read_available(), exception_on_overflow=False)
            callback(y)
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    stream.stop_stream()
    stream.close()
    p.terminate()
