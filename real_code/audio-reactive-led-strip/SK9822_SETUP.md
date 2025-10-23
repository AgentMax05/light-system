# SK9822/APA102 Audio-Reactive LED Strip Setup for Raspberry Pi 5

This guide explains how to use the adapted audio-reactive-led-strip library with SK9822/APA102 LED strips on a Raspberry Pi 5.

## What Changed?

The original library was designed for WS2812B/NeoPixel LEDs and ESP8266. This adaptation adds support for:
- **SK9822/APA102 LED strips** (using SPI communication)
- **Raspberry Pi 5** (and other Raspberry Pi models)
- Maintained compatibility with all original visualization effects

## Hardware Requirements

- Raspberry Pi 5 (or Pi 3/4)
- SK9822 or APA102 LED strip (300 LEDs as configured)
- 5V power supply (capable of powering your LED strip)
- USB audio input device (USB microphone or sound card)
- Jumper wires for connections

## Hardware Connections

### SK9822 LED Strip Wiring

SK9822 LEDs use SPI communication with 4 wires:

| SK9822 Pin | Raspberry Pi Pin | Notes |
|------------|------------------|-------|
| VCC (5V)   | External 5V PSU  | **DO NOT** connect to Pi 5V pin |
| GND        | GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39) | Common ground with Pi |
| Data (DI)  | MOSI - GPIO 10 (Pin 19) | SPI data out |
| Clock (CI) | SCLK - GPIO 11 (Pin 23) | SPI clock |

**IMPORTANT:**
- Use an external 5V power supply for the LED strip. The Pi cannot supply enough current.
- Ensure the Pi and power supply share a common ground connection.
- SK9822 LEDs work with 3.3V logic from the Pi, so no level shifter is needed.

### Audio Input

Connect a USB microphone or USB sound card to any USB port on the Raspberry Pi.

## Software Installation

### 1. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
```

- Navigate to: **Interface Options** → **SPI** → **Enable**
- Reboot if prompted

### 2. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-numpy python3-scipy portaudio19-dev
```

### 3. Install Python Dependencies

```bash
cd ~/audio-reactive-led-strip
pip3 install --upgrade pip
pip3 install numpy scipy pyaudio spidev
```

**Note:** `pyqtgraph` is optional and only needed for GUI visualization (not recommended on Pi due to performance):

```bash
# Optional - only if you want GUI
pip3 install pyqtgraph
```

## Configuration

The configuration is in `python/config.py`. Key settings for SK9822:

```python
DEVICE = 'pi-sk9822'          # Use SK9822 mode
N_PIXELS = 300                # Number of LEDs in your strip
SPI_BUS = 0                   # SPI bus (usually 0)
SPI_DEVICE = 0                # SPI device (usually 0)
SPI_SPEED_HZ = 1000000        # 1 MHz (can go up to 4 MHz)
SK9822_BRIGHTNESS = 31        # 0-31, where 31 is max
SOFTWARE_GAMMA_CORRECTION = True
USE_GUI = False               # Disable GUI for better performance
DISPLAY_FPS = True            # Show FPS in console
```

### Adjusting Settings

- **Brightness**: `SK9822_BRIGHTNESS` (0-31) - Lower for less power consumption
- **SPI Speed**: `SPI_SPEED_HZ` - Increase to 2000000 or 4000000 for faster refresh
- **LED Count**: `N_PIXELS` - Must match your actual LED strip length
- **Frequency Range**: `MIN_FREQUENCY` and `MAX_FREQUENCY` - Adjust for music type
- **FPS**: Target frame rate (default 60, may be lower on Pi 5 with 300 LEDs)

## Running the Visualizer

### Quick Start

```bash
cd ~/audio-reactive-led-strip
python3 run_sk9822.py
```

### Advanced Usage

To run the original visualization script directly:

```bash
cd ~/audio-reactive-led-strip/python
python3 visualization.py
```

### Change Visualization Effects

There are three built-in effects:
1. **Spectrum** (default): Frequency spectrum bars
2. **Energy**: Expands from center based on energy
3. **Scroll**: Scrolling color effect from center

To change effects, edit `python/visualization.py`:

```python
# At the bottom of the file, change this line:
visualization_effect = visualize_spectrum  # or visualize_energy or visualize_scroll
```

Or modify the GUI to switch effects in real-time (if USE_GUI = True).

## Testing LED Strip Only

To test just the SK9822 controller without audio:

```bash
cd ~/audio-reactive-led-strip/python
python3 led_sk9822.py
```

This will run a test pattern (crawling LED and rainbow cycle).

## Troubleshooting

### LEDs don't light up

1. **Check SPI is enabled:**
   ```bash
   lsmod | grep spi
   ```
   Should show `spi_bcm2835` or similar

2. **Check wiring:**
   - Data pin: GPIO 10 (Pin 19)
   - Clock pin: GPIO 11 (Pin 23)
   - Common ground between Pi and power supply

3. **Check power supply:**
   - 300 LEDs at full brightness can draw ~18A at 5V
   - Use adequate power supply (5V 20A recommended)

4. **Test SPI communication:**
   ```bash
   # Check SPI devices exist
   ls -l /dev/spidev*
   ```

### No audio detected

1. **List audio devices:**
   ```bash
   python3 -c "import pyaudio; p=pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())])"
   ```

2. **Check microphone input:**
   ```bash
   arecord -l
   ```

3. **Adjust `MIC_RATE` in `config.py`** if your device doesn't support 44100 Hz

### Poor performance / Low FPS

1. **Disable GUI:** Set `USE_GUI = False` in `config.py`
2. **Reduce LED count:** Test with fewer LEDs first
3. **Increase SPI speed:** Set `SPI_SPEED_HZ = 2000000` or higher
4. **Lower FPS target:** Set `FPS = 30` in `config.py`
5. **Close other programs:** Free up CPU resources

### Colors look wrong

1. **Check gamma correction:** Try toggling `SOFTWARE_GAMMA_CORRECTION`
2. **Check brightness:** Lower `SK9822_BRIGHTNESS` if colors are washed out
3. **Verify wiring:** Ensure Data and Clock aren't swapped

## Performance Optimization

For Raspberry Pi 5 with 300 LEDs:

```python
# Recommended settings in config.py
SPI_SPEED_HZ = 2000000        # 2 MHz
SK9822_BRIGHTNESS = 15        # 50% brightness saves power
USE_GUI = False               # Don't use GUI
FPS = 40                      # Lower FPS target
DISPLAY_FPS = False           # Disable FPS printing
```

## Differences from WS2812B/NeoPixel

| Feature | WS2812B | SK9822 |
|---------|---------|--------|
| Protocol | PWM timing | SPI |
| Data pins | Single GPIO | Data + Clock |
| Speed | Limited | Up to 4 MHz |
| Brightness | PWM only | Global + PWM |
| Wiring | More sensitive | More robust |
| Cost | Cheaper | Slightly more expensive |

## Files Modified/Added

- **Added:** `python/led_sk9822.py` - SK9822 controller class
- **Modified:** `python/config.py` - Added `pi-sk9822` device type and SPI settings
- **Modified:** `python/led.py` - Added SK9822 update function
- **Added:** `run_sk9822.py` - Simple launcher script
- **Added:** `SK9822_SETUP.md` - This documentation

## Original Library

This is adapted from: https://github.com/scottlawsonbc/audio-reactive-led-strip

All visualization algorithms and audio processing code remain the same. Only the LED output method was changed to support SK9822 via SPI.

## Need Help?

1. Check this guide's troubleshooting section
2. Review the original library's documentation
3. Check your wiring and power supply
4. Test with the LED-only test script first
5. Verify SPI is working with simple test code

## Auto-Start on Boot (Optional)

To run the visualizer automatically on boot:

1. Create a systemd service:
   ```bash
   sudo nano /etc/systemd/system/led-visualizer.service
   ```

2. Add this content:
   ```ini
   [Unit]
   Description=LED Audio Visualizer
   After=network.target sound.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/audio-reactive-led-strip
   ExecStart=/usr/bin/python3 /home/pi/audio-reactive-led-strip/run_sk9822.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable led-visualizer
   sudo systemctl start led-visualizer
   ```

4. Check status:
   ```bash
   sudo systemctl status led-visualizer
   ```

## License

Same as original library (see LICENSE.txt in repository)
