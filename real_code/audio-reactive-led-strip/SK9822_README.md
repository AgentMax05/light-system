# Audio-Reactive LED Strip - SK9822 Adaptation Summary

## Overview

This adaptation enables the audio-reactive-led-strip library to work with SK9822/APA102 LED strips on Raspberry Pi 5 using SPI communication.

## Files Created/Modified

### New Files
1. **`python/led_sk9822.py`**
   - SK9822Controller class for SPI-based LED control
   - Handles start/end frames, brightness control, and gamma correction
   - Compatible with the existing visualization pipeline
   - Based on your `custom_test.py` code

2. **`run_sk9822.py`**
   - Simple launcher script for the visualizer
   - Displays configuration and status
   - Handles clean shutdown

3. **`SK9822_SETUP.md`**
   - Complete setup and configuration guide
   - Hardware wiring diagrams
   - Troubleshooting tips
   - Performance optimization suggestions

### Modified Files
1. **`python/config.py`**
   - Added `DEVICE = 'pi-sk9822'` option
   - Added SPI configuration variables:
     - `SPI_BUS`, `SPI_DEVICE`, `SPI_SPEED_HZ`
     - `SK9822_BRIGHTNESS` (0-31)
   - Changed default `N_PIXELS` to 300 (your strip length)

2. **`python/led.py`**
   - Added SK9822 initialization in device setup
   - Added `_update_pi_sk9822()` function
   - Integrated SK9822 into the `update()` dispatcher

## Key Features

✅ **Full compatibility** with all original visualization effects (spectrum, energy, scroll)  
✅ **Hardware brightness control** using SK9822's built-in brightness (0-31)  
✅ **Optimized performance** with change detection and SPI speeds up to 4MHz  
✅ **Easy configuration** via `config.py`  
✅ **Robust wiring** - SK9822 is more reliable than WS2812B  
✅ **Maintained compatibility** with original library structure  

## Quick Start Guide

### 1. Hardware Setup
```
SK9822 Strip:
  VCC → 5V Power Supply (NOT Pi)
  GND → Pi GND + Power Supply GND (common ground)
  DI  → Pi GPIO 10 (MOSI, Pin 19)
  CI  → Pi GPIO 11 (SCLK, Pin 23)
  
Audio:
  USB Microphone → Any USB port
```

### 2. Software Setup
```bash
# Enable SPI
sudo raspi-config  # Interface Options → SPI → Enable

# Install dependencies
sudo apt-get install python3-pip python3-numpy python3-scipy portaudio19-dev
pip3 install numpy scipy pyaudio spidev

# Configure
cd audio-reactive-led-strip/python
nano config.py  # Verify DEVICE = 'pi-sk9822' and N_PIXELS = 300
```

### 3. Run
```bash
cd audio-reactive-led-strip
python3 run_sk9822.py
```

## Configuration Options

```python
# In python/config.py
DEVICE = 'pi-sk9822'          # Enable SK9822 mode
N_PIXELS = 300                # Your LED count
SPI_SPEED_HZ = 1000000        # SPI speed (1-4 MHz)
SK9822_BRIGHTNESS = 31        # Global brightness (0-31)
USE_GUI = False               # Disable for performance
FPS = 60                      # Target frame rate
MIN_FREQUENCY = 200           # Low frequency cutoff
MAX_FREQUENCY = 12000         # High frequency cutoff
N_FFT_BINS = 24              # Frequency bins
```

## How It Works

1. **Audio Capture** (`microphone.py`)
   - Captures audio from USB device at `MIC_RATE` (44.1kHz)
   
2. **Audio Processing** (`dsp.py`, `visualization.py`)
   - FFT transforms audio to frequency domain
   - Mel filterbank separates into frequency bins
   - Visualization effects map frequencies to RGB values
   
3. **LED Output** (`led.py` → `led_sk9822.py`)
   - Receives RGB array (3, N_PIXELS)
   - Applies gamma correction
   - Formats data for SK9822 (start frame, LED data, end frame)
   - Sends via SPI at configured speed

## Advantages of SK9822 over WS2812B

| Feature | SK9822 | WS2812B |
|---------|--------|---------|
| Protocol | SPI (robust) | PWM timing (sensitive) |
| Speed | Up to 4MHz | Limited by timing |
| Brightness | Hardware + PWM | PWM only |
| Wiring | Clock + Data | Data only |
| Reliability | Higher | Lower |
| Pi Compatibility | Direct 3.3V | May need level shifter |

## Visualization Effects

### 1. Spectrum (default)
Displays frequency spectrum as colored bars expanding from center.

### 2. Energy
Expands from center based on overall sound energy in frequency bands.

### 3. Scroll
Colors scroll outward from center, creating a flowing effect.

**To change:** Edit `python/visualization.py` and modify:
```python
visualization_effect = visualize_spectrum  # or visualize_energy, visualize_scroll
```

## Testing

### LED Test Only
```bash
cd python
python3 led_sk9822.py
```
This runs a crawling LED and rainbow cycle test.

### Full Visualization
```bash
python3 run_sk9822.py
```
Play music and watch the LEDs react!

## Troubleshooting

**LEDs don't light up?**
- Check SPI enabled: `lsmod | grep spi`
- Verify wiring (MOSI=GPIO10, SCLK=GPIO11)
- Check power supply is adequate
- Ensure common ground

**No audio detected?**
- List devices: `arecord -l`
- Check PyAudio can see it
- Try different `MIC_RATE` values

**Low FPS?**
- Disable GUI: `USE_GUI = False`
- Increase SPI speed: `SPI_SPEED_HZ = 2000000`
- Lower FPS target: `FPS = 40`
- Reduce LED count for testing

## Performance Tips

For best performance on Raspberry Pi 5 with 300 LEDs:
- Use `SPI_SPEED_HZ = 2000000` (2 MHz)
- Set `SK9822_BRIGHTNESS = 15` (saves power, still bright)
- Disable GUI and FPS display
- Close other applications
- Consider overclocking Pi if needed

## What's NOT Changed

✅ All visualization algorithms  
✅ Audio processing pipeline  
✅ FFT and frequency analysis  
✅ Color mapping and effects  
✅ Configuration structure  

Only the LED output method was changed from WS2812B/PWM to SK9822/SPI.

## Next Steps

1. Test LED strip with `python3 python/led_sk9822.py`
2. Verify audio input works
3. Run full visualizer with `python3 run_sk9822.py`
4. Tune settings in `config.py` for your setup
5. Choose your favorite visualization effect
6. Optional: Set up auto-start on boot (see SK9822_SETUP.md)

## Credits

- Original library: https://github.com/scottlawsonbc/audio-reactive-led-strip
- SK9822 adaptation: Based on your `custom_test.py` implementation
- All visualization and audio processing code: Original library authors

Enjoy your audio-reactive LED strip! 🎵💡
