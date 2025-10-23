#!/usr/bin/env python
"""
Simple test script for audio-reactive SK9822 LED strip
Run this on your Raspberry Pi 5 to test the audio-reactive visualizations
"""
from __future__ import print_function
from __future__ import division
import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

import config
import microphone
import visualization
import led

def main():
    """Main function to run audio-reactive LED visualization"""
    
    print("=" * 60)
    print("Audio-Reactive SK9822 LED Strip Visualizer")
    print("=" * 60)
    print(f"Device: {config.DEVICE}")
    print(f"Number of LEDs: {config.N_PIXELS}")
    print(f"SPI Speed: {config.SPI_SPEED_HZ} Hz")
    print(f"Brightness: {config.SK9822_BRIGHTNESS}/31")
    print(f"FPS Target: {config.FPS}")
    print(f"Microphone Rate: {config.MIC_RATE} Hz")
    print(f"Frequency Range: {config.MIN_FREQUENCY}-{config.MAX_FREQUENCY} Hz")
    print("=" * 60)
    print("\nAvailable visualizations:")
    print("  - spectrum (default): Frequency spectrum visualization")
    print("  - scroll: Scrolling color effect")
    print("  - energy: Energy-based expansion effect")
    print("\nTo change visualization, modify visualization_effect in visualization.py")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Initialize LEDs
        print("Initializing LED strip...")
        led.update()
        
        # Start listening to audio stream
        print("Starting audio capture...")
        print("Play some music and watch the LEDs react!\n")
        microphone.start_stream(visualization.microphone_update)
        
    except KeyboardInterrupt:
        print("\n\nStopping visualization...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print("Turning off LEDs...")
        if config.DEVICE == 'pi-sk9822':
            led.strip.clear()
            led.strip.close()
        print("Done!")

if __name__ == '__main__':
    # Disable GUI on Raspberry Pi (it's too slow)
    if not hasattr(config, 'USE_GUI'):
        config.USE_GUI = False
    elif config.USE_GUI:
        print("Warning: GUI is enabled. This may cause performance issues on Raspberry Pi.")
        print("Consider setting USE_GUI = False in config.py for better performance.\n")
    
    main()
