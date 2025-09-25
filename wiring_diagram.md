# LED Strip Wiring Diagram

## Hardware Connections

### Basic Wiring (Short Strips < 30 LEDs)

```
Raspberry Pi          LED Strip (WS2812B)
─────────────────     ──────────────────
GPIO 18 (Pin 12)  →   DI (Data In)
GND (Pin 6)       →   GND (Ground)
                   
External 5V PSU   →   +5V (Power)
```

### Advanced Wiring (Long Strips 30+ LEDs)

```
Raspberry Pi          Level Shifter        LED Strip (WS2812B)
─────────────────     ────────────────     ──────────────────
GPIO 18 (Pin 12)  →   LV (3.3V Input)  →   DI (Data In)
3.3V (Pin 1)      →   VCC
GND (Pin 6)       →   GND            →   GND (Ground)
                   
External 5V PSU   →   HV (5V Input)   →   +5V (Power)
```

## Pin Assignments

### Raspberry Pi GPIO Pins
- **GPIO 18**: Data signal (PWM capable)
- **GND**: Ground reference
- **3.3V**: Power for level shifter (if used)

### LED Strip Connections
- **DI (Data In)**: Data signal from GPIO 18
- **GND**: Ground connection
- **+5V**: Power input (external supply)
- **CI (Clock In)**: Not used for WS2812B

## Power Supply Requirements

### Calculation Formula
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

## Safety Considerations

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
   - Converts 3.3V GPIO signal to 5V
   - Prevents signal degradation

4. **Proper grounding**
   - Connect all grounds together
   - Use thick ground wires for high current

## Wiring Diagrams

### Diagram 1: Basic Setup (Short Strips)
```
                    ┌─────────────────┐
                    │   Raspberry Pi   │
                    │                 │
                    │  GPIO 18 ───────┼─── DI
                    │  GND ───────────┼─── GND
                    └─────────────────┘
                                       
                    ┌─────────────────┐
                    │  5V Power Supply │
                    │                 │
                    │  +5V ───────────┼─── +5V
                    │  GND ───────────┼─── GND
                    └─────────────────┘
```

### Diagram 2: Advanced Setup (Long Strips)
```
                    ┌─────────────────┐
                    │   Raspberry Pi   │
                    │                 │
                    │  GPIO 18 ───────┼─── LV ──── DI
                    │  3.3V ──────────┼─── VCC
                    │  GND ───────────┼─── GND ──── GND
                    └─────────────────┘
                                       
                    ┌─────────────────┐
                    │  5V Power Supply │
                    │                 │
                    │  +5V ───────────┼─── HV ──── +5V
                    │  GND ───────────┼─── GND ──── GND
                    └─────────────────┘
                                       
                    ┌─────────────────┐
                    │  Level Shifter  │
                    │   (3.3V→5V)     │
                    └─────────────────┘
```

## Component Specifications

### Level Shifter (Recommended)
- **Type**: Bi-directional level shifter
- **Input**: 3.3V (Raspberry Pi)
- **Output**: 5V (LED Strip)
- **Channels**: 1 (minimum)
- **Example**: TXS0108E, 74HCT245

### Power Supply Requirements
- **Voltage**: 5V DC (±5%)
- **Current**: As calculated above + 20% headroom
- **Connector**: Barrel jack or screw terminals
- **Protection**: Fuse recommended

### Wire Specifications
- **Data wire**: 22 AWG minimum
- **Power wires**: 18 AWG minimum (for 60+ LEDs)
- **Ground wire**: Same as power wires
- **Length**: Keep as short as possible

## Troubleshooting Wiring

### Common Issues

1. **LEDs not lighting up**
   - Check power supply connections
   - Verify data wire connection
   - Test power supply output voltage

2. **Intermittent operation**
   - Check all connections for looseness
   - Verify ground connections
   - Test with shorter data wire

3. **Wrong colors or patterns**
   - Check data wire connection
   - Verify GPIO pin assignment
   - Test with known good configuration

4. **Power supply issues**
   - Measure output voltage (should be 5V)
   - Check current capacity
   - Verify proper grounding

### Testing Procedures

1. **Power Supply Test**
   ```bash
   # Measure voltage with multimeter
   # Should read 5V ± 0.25V
   ```

2. **Data Signal Test**
   ```bash
   # Test GPIO output
   python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(18, GPIO.OUT); GPIO.output(18, GPIO.HIGH)"
   ```

3. **LED Strip Test**
   ```bash
   # Run basic LED test
   python3 led_controller.py
   ```

## Mounting Considerations

### Heat Management
- **Ventilation**: Ensure adequate airflow
- **Heat sinks**: Consider for high-power strips
- **Temperature monitoring**: Use thermal sensors

### Cable Management
- **Strain relief**: Secure connections
- **Cable routing**: Avoid sharp bends
- **Protection**: Use conduit for exposed wires

### Environmental Protection
- **Waterproofing**: Use appropriate enclosures
- **UV protection**: Shield from direct sunlight
- **Temperature range**: Check component specifications

## Advanced Configurations

### Multiple Strips
- **Parallel connection**: Connect data lines together
- **Series connection**: Connect end of one strip to start of next
- **Separate control**: Use multiple GPIO pins

### Long Distance Control
- **RS485**: For distances over 100m
- **Wireless**: Use ESP32 or similar
- **Ethernet**: Use network-based controllers

### Professional Installations
- **DMX512**: For theater/venue applications
- **Art-Net**: For network-based control
- **Custom protocols**: For specific requirements

---

**Remember**: Always double-check your wiring before powering on, and start with a small test to verify everything works correctly!
