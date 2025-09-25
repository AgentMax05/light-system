# SK9822 SPI LED Strip Wiring Guide

## Hardware Connections

### SK9822 vs WS2812B
- **WS2812B**: Single data line (DI only)
- **SK9822**: SPI protocol (DI + CI required)

### Wiring Diagram

```
Raspberry Pi          SK9822 LED Strip
─────────────────     ──────────────────
MOSI (Pin 19)    →   DI (Data In)
SCLK (Pin 23)    →   CI (Clock In)
GND (Pin 6)      →   GND (Ground)
                   
External 5V PSU  →   +5V (Power)
```

## Pin Assignments

### Raspberry Pi SPI Pins
- **MOSI (Pin 19)**: Master Out Slave In (data)
- **SCLK (Pin 23)**: Serial Clock (clock)
- **GND (Pin 6)**: Ground reference
- **3.3V (Pin 1)**: Power for level shifter (if needed)

### SK9822 LED Strip
- **DI (Data In)**: Data signal from MOSI
- **CI (Clock In)**: Clock signal from SCLK
- **GND**: Ground connection
- **+5V**: Power input (external supply)

## SPI Configuration

### Enable SPI on Raspberry Pi
```bash
sudo raspi-config
# Navigate to: Interfacing Options → SPI → Enable
```

### Check SPI Interface
```bash
# List SPI devices
ls /dev/spi*

# Should show:
# /dev/spidev0.0
# /dev/spidev0.1
```

### Set SPI Permissions
```bash
# Add user to spi group
sudo usermod -a -G spi pi

# Check group membership
groups pi
```

## Power Requirements

### Calculation
```
Total Power = LED_COUNT × 60mA × 5V
```

### Examples
- **30 LEDs**: 1.8A at 5V = 9W
- **60 LEDs**: 3.6A at 5V = 18W
- **100 LEDs**: 6A at 5V = 30W

### Recommended Power Supplies
- **30 LEDs**: 5V 3A (15W)
- **60 LEDs**: 5V 5A (25W)
- **100 LEDs**: 5V 8A (40W)

## Level Shifter (Optional)

### For Long Strips (30+ LEDs)
```
Raspberry Pi          Level Shifter        SK9822 LED Strip
─────────────────     ────────────────     ──────────────────
MOSI (Pin 19)    →   LV1 (3.3V Input) →   DI (Data In)
SCLK (Pin 23)    →   LV2 (3.3V Input) →   CI (Clock In)
3.3V (Pin 1)     →   VCC
GND (Pin 6)      →   GND            →   GND (Ground)
                   
External 5V PSU  →   HV1 (5V Input)  →   +5V (Power)
                   HV2 (5V Input)
```

## Testing the Setup

### 1. Check SPI Interface
```bash
# Test SPI communication
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0b00
print('SPI interface working')
spi.close()
"
```

### 2. Run LED Test
```bash
cd test
pip install spidev
python sk9822_led_test.py
```

## Protocol Differences

### WS2812B Protocol
- **Single wire**: Data only
- **Timing**: 800kHz embedded timing
- **Library**: rpi-ws281x

### SK9822 Protocol
- **Two wires**: Data + Clock
- **Timing**: SPI clock signal
- **Library**: spidev

## Common Issues

### 1. SPI Not Enabled
```bash
# Enable SPI
sudo raspi-config
# Interfacing Options → SPI → Enable
sudo reboot
```

### 2. Permission Denied
```bash
# Add user to spi group
sudo usermod -a -G spi pi
# Log out and back in
```

### 3. No SPI Devices
```bash
# Check if SPI is enabled
lsmod | grep spi
# Should show spi_bcm2835
```

### 4. Wrong Wiring
- **MOSI → DI**: Data signal
- **SCLK → CI**: Clock signal
- **GND → GND**: Ground
- **5V PSU → +5V**: Power

## Safety Notes

### ⚠️ Critical Safety Rules

1. **NEVER connect LED +5V to Raspberry Pi 5V pin**
   - Raspberry Pi cannot provide enough current
   - Will damage the Pi and/or LED strip

2. **Use appropriate power supply**
   - Must be 5V DC
   - Current rating must exceed calculated requirements
   - Include 20% headroom for safety

3. **Use level shifter for long strips**
   - Required for strips longer than 30 LEDs
   - Converts 3.3V SPI signal to 5V
   - Prevents signal degradation

4. **Proper grounding**
   - Connect all grounds together
   - Use thick ground wires for high current

## Expected Results

When working correctly, you should see:
- **Solid colors**: Red, Green, Blue, White
- **Rainbow pattern**: Moving rainbow effect
- **Chase pattern**: Light chasing around the strip
- **Breathing pattern**: Gentle breathing effect
- **All LEDs clear**: When test completes

## Troubleshooting

### No Lights
1. Check power supply connections
2. Verify SPI wiring (MOSI→DI, SCLK→CI)
3. Ensure SPI is enabled
4. Check user permissions

### Wrong Colors
1. Verify data wire connection (MOSI→DI)
2. Check clock wire connection (SCLK→CI)
3. Test with known good configuration

### Permission Errors
1. Add user to spi group
2. Check file permissions
3. Run with sudo if needed

---

**Remember**: SK9822 strips require BOTH data AND clock signals, unlike WS2812B which only needs data!
