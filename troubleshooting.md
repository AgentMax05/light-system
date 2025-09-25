# Troubleshooting Guide

## Quick Diagnostic Checklist

### ✅ Basic Checks
- [ ] Raspberry Pi is powered on and booted
- [ ] LED strip is connected to external 5V power supply
- [ ] Data wire connected to GPIO 18
- [ ] Ground wire connected to Pi GND
- [ ] Web interface accessible at `http://pi-ip:5000`
- [ ] No error messages in terminal

### ✅ Power Supply Checks
- [ ] Power supply is 5V DC
- [ ] Current rating sufficient for LED count
- [ ] Power supply is working (test with multimeter)
- [ ] All connections secure

### ✅ Software Checks
- [ ] Python virtual environment activated
- [ ] All dependencies installed
- [ ] No permission errors
- [ ] GPIO access enabled

## Common Issues and Solutions

### 1. LEDs Not Lighting Up

#### Symptoms
- No LEDs light up at all
- Web interface shows "Connected" but no visual output
- No error messages in logs

#### Possible Causes & Solutions

**A. Power Supply Issues**
```bash
# Check power supply voltage
# Should read 5V ± 0.25V
multimeter_test_5v_supply
```

**B. Wiring Problems**
- Check data wire connection to GPIO 18
- Verify ground connection to Pi GND
- Ensure +5V connected to external supply (NOT Pi)

**C. GPIO Pin Issues**
```bash
# Test GPIO 18 output
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
print('GPIO 18 set HIGH')
GPIO.cleanup()
"
```

**D. Library Issues**
```bash
# Reinstall rpi_ws281x
pip uninstall rpi-ws281x
pip install rpi-ws281x
```

### 2. Web Interface Not Accessible

#### Symptoms
- Cannot connect to `http://pi-ip:5000`
- "Connection refused" error
- Interface loads but controls don't work

#### Solutions

**A. Check if Application is Running**
```bash
# Check if Python process is running
ps aux | grep python

# Check if port 5000 is listening
netstat -tlnp | grep 5000
```

**B. Start Application Manually**
```bash
cd /path/to/led-controller
source venv/bin/activate
python app.py
```

**C. Check Firewall Settings**
```bash
# Check if port 5000 is blocked
sudo ufw status
sudo ufw allow 5000
```

**D. Check Network Configuration**
```bash
# Get Pi's IP address
hostname -I

# Test local connection
curl http://localhost:5000/api/status
```

### 3. Audio/Music Visualization Not Working

#### Symptoms
- Music pattern selected but no audio response
- "Audio capture failed" error
- No audio input detected

#### Solutions

**A. Check Audio Device**
```bash
# List audio devices
arecord -l

# Test audio input
arecord -f cd -d 5 test.wav
aplay test.wav
```

**B. Set Audio Permissions**
```bash
# Add user to audio group
sudo usermod -a -G audio pi

# Check audio group membership
groups pi
```

**C. Configure Audio Input**
```bash
# Set default audio input
sudo raspi-config
# Navigate to: Advanced Options → Audio → Force 3.5mm jack
```

**D. Test Audio Processing**
```bash
# Run audio test
python3 audio_processor.py
```

### 4. Performance Issues

#### Symptoms
- Slow or choppy animations
- High CPU usage
- System becomes unresponsive

#### Solutions

**A. Reduce LED Count**
```bash
# Edit .env file
LED_COUNT=30  # Reduce from 60
```

**B. Lower Brightness**
```bash
# In web interface or .env
DEFAULT_BRIGHTNESS=64  # Reduce from 128
```

**C. Optimize Patterns**
- Use simpler patterns (Solid, Fade)
- Avoid complex patterns (Music, Fire)
- Reduce animation speed

**D. System Optimization**
```bash
# Close unnecessary applications
sudo systemctl stop bluetooth
sudo systemctl stop wifi-powersave

# Increase GPU memory split
sudo raspi-config
# Navigate to: Advanced Options → Memory Split → 128
```

### 5. Permission Errors

#### Symptoms
- "Permission denied" errors
- Cannot access GPIO
- Audio access denied

#### Solutions

**A. GPIO Permissions**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Check GPIO access
ls -la /dev/gpiomem
```

**B. Audio Permissions**
```bash
# Add user to audio group
sudo usermod -a -G audio pi

# Check audio device permissions
ls -la /dev/snd/
```

**C. File Permissions**
```bash
# Set proper ownership
sudo chown -R pi:pi /path/to/led-controller
chmod +x start.sh
```

### 6. Pattern Not Working Correctly

#### Symptoms
- Pattern selected but wrong behavior
- Colors not displaying correctly
- Animation speed issues

#### Solutions

**A. Check Pattern Implementation**
```python
# Test individual patterns
python3 -c "
from led_controller import LEDController, PatternType
controller = LEDController(60)
controller.set_pattern(PatternType.SOLID)
controller.start_animation()
"
```

**B. Verify Color Values**
```python
# Test color setting
from led_controller import ColorRGB
color = ColorRGB(255, 0, 0)  # Red
print(f"Color: {color.to_hex()}")
```

**C. Check Animation Speed**
```python
# Test speed control
controller.set_animation_speed(0.5)  # Half speed
```

## Advanced Troubleshooting

### Debug Mode

Enable detailed logging:

```bash
# Set debug mode
export DEBUG=True
python app.py
```

### System Logs

Check system logs for errors:

```bash
# Application logs
journalctl -u led-controller -f

# System logs
dmesg | grep -i error

# Audio logs
dmesg | grep -i audio
```

### Hardware Testing

**A. Test GPIO Output**
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# Blink GPIO 18
for i in range(10):
    GPIO.output(18, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(18, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()
```

**B. Test LED Strip**
```python
from led_controller import LEDController
controller = LEDController(10)  # Test with 10 LEDs
controller.set_all_pixels(ColorRGB(255, 0, 0))  # Red
```

**C. Test Power Supply**
```bash
# Measure voltage under load
# Should maintain 5V with LEDs on
```

### Network Troubleshooting

**A. Check Network Connectivity**
```bash
# Test local connection
ping localhost

# Test external connection
ping google.com

# Check IP address
ip addr show
```

**B. Port Accessibility**
```bash
# Test port from another machine
telnet pi-ip 5000

# Check if port is open
nmap -p 5000 pi-ip
```

## Performance Optimization

### For Large LED Strips (100+ LEDs)

1. **Reduce Update Frequency**
   ```python
   # In led_controller.py
   time.sleep(0.1 / self.animation_speed)  # Increase from 0.05
   ```

2. **Use Simpler Patterns**
   - Avoid complex calculations
   - Use pre-computed values
   - Limit simultaneous operations

3. **Optimize Power Usage**
   ```python
   # Lower brightness for power savings
   controller.set_brightness(64)  # Instead of 255
   ```

### System Optimization

1. **Disable Unnecessary Services**
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable wifi-powersave
   ```

2. **Increase GPU Memory**
   ```bash
   sudo raspi-config
   # Advanced Options → Memory Split → 128
   ```

3. **Use Fast SD Card**
   - Class 10 or better
   - A1 or A2 rating preferred

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review the README.md file**
3. **Search existing issues on GitHub**
4. **Test with minimal configuration**

### When Reporting Issues

Include the following information:

1. **System Information**
   ```bash
   uname -a
   cat /etc/os-release
   ```

2. **LED Configuration**
   ```bash
   cat .env
   ```

3. **Error Messages**
   ```bash
   # Full error output
   python app.py 2>&1 | tee error.log
   ```

4. **Hardware Details**
   - LED strip type and length
   - Power supply specifications
   - Wiring configuration

5. **Steps to Reproduce**
   - Exact steps that cause the issue
   - Expected vs actual behavior

### Useful Commands

```bash
# System information
uname -a
cat /proc/cpuinfo
free -h
df -h

# Network information
ip addr show
netstat -tlnp

# Process information
ps aux | grep python
top

# Log information
journalctl -u led-controller
dmesg | tail -20
```

---

**Remember**: Most issues are caused by wiring problems or incorrect configuration. Double-check your connections and settings before reporting issues!
