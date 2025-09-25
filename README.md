# Raspberry Pi LED Strip Controller

A comprehensive Python-based system for controlling individually addressable LED strips (WS2812B/NeoPixel) with a Raspberry Pi. Features include web-based control, music visualization, pattern scheduling, and a modern responsive interface.

## Features

- **Individual LED Control**: Set color and brightness for each LED
- **Pattern Generation**: 9 built-in patterns (Solid, Rainbow, Chase, Fade, Breathing, Twinkle, Wave, Fire, Music)
- **Web Interface**: Modern, responsive web interface with real-time controls
- **REST API**: Complete API for external control and integration
- **Music Visualization**: Real-time audio processing and visualization
- **Pattern Scheduling**: Schedule patterns to run at specific times
- **Color Management**: Primary and secondary color controls with hex input
- **Brightness & Speed Control**: Adjustable brightness and animation speed
- **Settings Export/Import**: Backup and restore configurations
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## Hardware Requirements

### Required Components
- Raspberry Pi (any model with GPIO pins)
- WS2812B individually addressable LED strip (BTF-Lighting compatible)
- 5V power supply (external, NOT from Raspberry Pi)
- Jumper wires
- Optional: Level shifter (3.3V to 5V) for longer strips

### Wiring Diagram

```
LED Strip          Raspberry Pi
+5V (Red)    →     External 5V Power Supply
GND (Black)  →     GND (Pin 6)
DI (Data)    →     GPIO 18 (Pin 12)
CI (Clock)   →     Not connected (unused for WS2812B)
```

**⚠️ Important Safety Notes:**
- **NEVER** connect the LED strip's +5V to the Raspberry Pi's 5V pin
- Use an external 5V power supply rated for your LED strip
- For strips longer than 30 LEDs, use a level shifter between GPIO 18 and the LED strip
- Ensure proper heat dissipation for long strips

## Software Installation

### 1. System Requirements
- Raspberry Pi OS (latest recommended)
- Python 3.7+
- Internet connection for package installation

### 2. Install Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-dev python3-venv

# Install system audio libraries
sudo apt install portaudio19-dev python3-pyaudio

# Install additional dependencies for audio processing
sudo apt install libasound2-dev
```

### 3. Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd led-strip-controller

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# LED Configuration
LED_COUNT=60
LED_PIN=18
DEFAULT_BRIGHTNESS=128

# Web Server Configuration
PORT=5000
DEBUG=False

# Audio Configuration (optional)
AUDIO_ENABLED=True
```

### 5. Enable GPIO and Audio (if needed)

```bash
# Enable GPIO (usually enabled by default)
sudo raspi-config
# Navigate to: Interfacing Options → GPIO → Enable

# Enable audio input (for music visualization)
sudo raspi-config
# Navigate to: Advanced Options → Audio → Force 3.5mm jack
```

## Usage

### 1. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py
```

The web interface will be available at `http://your-pi-ip:5000`

### 2. Web Interface

Open your browser and navigate to the Raspberry Pi's IP address on port 5000. The interface provides:

- **Pattern Selection**: Choose from 9 different LED patterns
- **Color Controls**: Set primary and secondary colors
- **Brightness Control**: Adjust overall brightness (0-255)
- **Speed Control**: Control animation speed (0.1x - 10x)
- **Audio Controls**: Start/stop music visualization
- **Scheduling**: Schedule patterns to run at specific times
- **Settings**: Export/import configurations

### 3. API Usage

The system provides a REST API for external control:

```bash
# Get current status
curl http://your-pi-ip:5000/api/status

# Set pattern
curl -X POST http://your-pi-ip:5000/api/pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "rainbow"}'

# Set color
curl -X POST http://your-pi-ip:5000/api/color \
  -H "Content-Type: application/json" \
  -d '{"primary": {"hex": "#FF0000"}}'

# Set brightness
curl -X POST http://your-pi-ip:5000/api/brightness \
  -H "Content-Type: application/json" \
  -d '{"brightness": 200}'

# Start/stop animation
curl -X POST http://your-pi-ip:5000/api/start
curl -X POST http://your-pi-ip:5000/api/stop
```

## Pattern Types

1. **Solid**: Single color across all LEDs
2. **Rainbow**: Moving rainbow pattern
3. **Chase**: Moving light that chases around the strip
4. **Fade**: Smooth fade in/out effect
5. **Breathing**: Gentle breathing effect
6. **Twinkle**: Random twinkling stars
7. **Wave**: Wave-like motion across the strip
8. **Fire**: Flickering fire effect
9. **Music**: Real-time audio visualization

## Music Visualization

The system includes advanced audio processing capabilities:

- **Real-time Audio Capture**: Captures audio from the Pi's microphone or USB audio device
- **Frequency Analysis**: Analyzes different frequency ranges (bass, mid, treble)
- **Beat Detection**: Detects beats and musical events
- **Multiple Visualization Modes**: Spectrum, beat-based, and frequency bar visualizations

### Audio Setup

1. Connect a microphone or USB audio device
2. Test audio input: `arecord -l` (should show your audio device)
3. Start audio capture in the web interface
4. Select "Music" pattern for visualization

## Scheduling

Schedule patterns to run automatically:

1. Select a pattern from the dropdown
2. Set the time (24-hour format)
3. Set duration in minutes
4. Click "Add Schedule"

Scheduled patterns will run automatically at the specified time.

## Configuration

### LED Strip Configuration

Edit the `.env` file to configure your LED strip:

```bash
LED_COUNT=60        # Number of LEDs in your strip
LED_PIN=18          # GPIO pin connected to data line
DEFAULT_BRIGHTNESS=128  # Default brightness (0-255)
```

### Power Requirements

Calculate power requirements for your LED strip:

- **Power per LED**: ~60mA at full brightness (white)
- **Total Power**: LED_COUNT × 60mA × 5V
- **Example**: 60 LEDs = 3.6A at 5V = 18W

Choose a power supply with at least 20% headroom.

## Troubleshooting

### Common Issues

1. **LEDs not lighting up**
   - Check wiring connections
   - Verify power supply is connected and working
   - Ensure GPIO pin is correct (default: GPIO 18)
   - Check if rpi_ws281x library is installed

2. **Audio not working**
   - Check microphone/audio device connection
   - Verify audio permissions: `sudo usermod -a -G audio pi`
   - Test audio input: `arecord -f cd -d 5 test.wav`

3. **Web interface not accessible**
   - Check if the application is running: `ps aux | grep python`
   - Verify port is not blocked: `netstat -tlnp | grep 5000`
   - Check firewall settings

4. **Performance issues**
   - Reduce LED count for better performance
   - Lower brightness to reduce power consumption
   - Close unnecessary applications

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set DEBUG=True in .env file
DEBUG=True

# Run with debug output
python app.py
```

### Log Files

Check system logs for errors:

```bash
# View application logs
journalctl -u led-controller

# Check system audio logs
dmesg | grep audio
```

## Safety Considerations

1. **Power Safety**
   - Use appropriate power supply for your LED strip
   - Never exceed the power supply's rated capacity
   - Use proper fusing for protection

2. **Heat Management**
   - Ensure adequate ventilation for long strips
   - Monitor temperature during extended use
   - Consider heat sinks for high-power applications

3. **Electrical Safety**
   - Use proper connectors and wiring
   - Avoid exposed connections
   - Follow local electrical codes

4. **Software Safety**
   - Regular backups of configurations
   - Monitor system resources
   - Implement proper shutdown procedures

## Advanced Configuration

### Custom Patterns

Create custom patterns by extending the `LEDController` class:

```python
def custom_pattern(self, frame: int):
    """Custom pattern implementation"""
    for i in range(self.led_count):
        # Your custom logic here
        color = ColorRGB(255, 0, 0)  # Red
        self.set_pixel(i, color)
```

### API Integration

Integrate with external systems using the REST API:

```python
import requests

# Control LEDs from external script
response = requests.post('http://pi-ip:5000/api/pattern', 
                        json={'pattern': 'rainbow'})
```

### Home Automation

Integrate with home automation systems:

- **Home Assistant**: Use REST API commands
- **OpenHAB**: Create items for LED control
- **Node-RED**: Use HTTP request nodes

## Performance Optimization

### For Large LED Strips (100+ LEDs)

1. **Reduce Update Frequency**
   ```python
   # In led_controller.py, increase sleep time
   time.sleep(0.1 / self.animation_speed)  # Reduce from 0.05
   ```

2. **Optimize Patterns**
   - Use simpler patterns for better performance
   - Reduce color calculations
   - Limit simultaneous operations

3. **Power Management**
   - Use lower brightness settings
   - Implement sleep modes
   - Monitor power consumption

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the troubleshooting section
2. Review the GitHub issues
3. Create a new issue with detailed information
4. Include system logs and configuration details

## Changelog

### Version 1.0.0
- Initial release
- Basic LED control
- Web interface
- Pattern generation
- Music visualization
- Scheduling system
- REST API
- Mobile responsive design

---

**Happy LED Controlling!** 🎨✨
