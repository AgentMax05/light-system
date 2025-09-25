# LED Strip Test Scripts

Test scripts for different types of individually addressable LED strips.

## Available Tests

### WS2812B Test (Single Data Line)
- **File**: `simple_led_test.py`
- **Protocol**: Single data line (DI only)
- **Library**: rpi-ws281x
- **Wiring**: GPIO 18 → DI, GND → GND, External 5V → +5V

### SK9822 Test (SPI Protocol)
- **File**: `sk9822_led_test.py`
- **Protocol**: SPI (DI + CI required)
- **Library**: spidev
- **Wiring**: MOSI → DI, SCLK → CI, GND → GND, External 5V → +5V

## Quick Setup

### For WS2812B Strips
1. **Install the library:**
   ```bash
   pip install rpi-ws281x
   ```

2. **Run the test:**
   ```bash
   python simple_led_test.py
   ```

### For SK9822 Strips
1. **Install the library:**
   ```bash
   pip install spidev
   ```

2. **Enable SPI:**
   ```bash
   sudo raspi-config
   # Interfacing Options → SPI → Enable
   ```

3. **Run the test:**
   ```bash
   python sk9822_led_test.py
   ```

## What It Tests

- ✅ **Solid Colors**: Red, Green, Blue, White
- ✅ **Rainbow Pattern**: Moving rainbow effect
- ✅ **Chase Pattern**: Red light chasing around the strip
- ✅ **Breathing Pattern**: Purple breathing effect

## Configuration

Edit the variables at the top of `main()` function:

```python
LED_COUNT = 30      # Number of LEDs in your strip
GPIO_PIN = 18       # GPIO pin connected to LED data line
BRIGHTNESS = 128    # Brightness (0-255)
```

## Wiring

```
Raspberry Pi          LED Strip
─────────────────     ──────────────────
GPIO 18 (Pin 12)  →   DI (Data In)
GND (Pin 6)       →   GND (Ground)
                   
External 5V PSU   →   +5V (Power)
```

## Troubleshooting

- **No lights**: Check wiring and power supply
- **Wrong colors**: Check data wire connection
- **Permission error**: Run with `sudo` or check GPIO permissions
- **Import error**: Install rpi-ws281x library

## Expected Output

```
🔌 Simple LED Strip Test
==============================
Configuration:
  LED Count: 30
  GPIO Pin: 18
  Brightness: 128

🔧 Initializing LED strip with 30 LEDs on GPIO 18
✅ LED strip initialized successfully

1️⃣ Testing solid colors...
🎨 Set all LEDs to RGB(255, 0, 0)
🎨 Set all LEDs to RGB(0, 255, 0)
🎨 Set all LEDs to RGB(0, 0, 255)
🎨 Set all LEDs to RGB(255, 255, 255)

2️⃣ Testing rainbow pattern...
🌈 Starting rainbow test...
✅ Rainbow test completed

3️⃣ Testing chase pattern...
🏃 Starting chase test...
✅ Chase test completed

4️⃣ Testing breathing pattern...
🫁 Starting breathing test...
✅ Breathing test completed

🧹 Clearing all LEDs...
🔴 All LEDs cleared

✅ All tests completed successfully!
🎉 Your LED strip is working correctly!
```
