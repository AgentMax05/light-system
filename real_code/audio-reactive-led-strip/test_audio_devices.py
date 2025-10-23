#!/usr/bin/env python3
"""
Test script to find available audio devices and their supported sample rates
"""
import pyaudio

def test_audio_devices():
    p = pyaudio.PyAudio()
    
    print("=" * 60)
    print("AUDIO DEVICES")
    print("=" * 60)
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"\nDevice {i}: {info['name']}")
        print(f"  Max Input Channels: {info['maxInputChannels']}")
        print(f"  Max Output Channels: {info['maxOutputChannels']}")
        print(f"  Default Sample Rate: {info['defaultSampleRate']}")
        
        # Test if this device supports input
        if info['maxInputChannels'] > 0:
            print(f"  ✓ This is an INPUT device (microphone/line-in)")
            
            # Test common sample rates
            sample_rates = [8000, 16000, 22050, 44100, 48000, 96000]
            supported = []
            
            for rate in sample_rates:
                try:
                    supported_test = p.is_format_supported(
                        rate,
                        input_device=i,
                        input_channels=1,
                        input_format=pyaudio.paInt16
                    )
                    if supported_test:
                        supported.append(rate)
                except ValueError:
                    pass
            
            if supported:
                print(f"  Supported Sample Rates: {supported}")
            else:
                print(f"  Could not determine supported rates, try default: {int(info['defaultSampleRate'])}")
    
    p.terminate()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print("\nLook for a device with maxInputChannels > 0")
    print("Note its Device number and a supported sample rate")
    print("Then update config.py with:")
    print("  MIC_RATE = <supported_rate>")
    print("\nIf you want to use a specific device, you may need to")
    print("modify microphone.py to specify input_device_index")

if __name__ == '__main__':
    test_audio_devices()
