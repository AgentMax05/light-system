#!/usr/bin/env python3
"""
SK9822 SPI LED Strip Test Script
Compatible with SK9822 individually addressable LED strips
Requires both data and clock signals
"""

import time
import math
import spidev

try:
    print("✅ Using SPI interface for SK9822 LEDs")
except ImportError:
    print("❌ SPI interface not available")
    exit(1)


class SK9822LEDTest:
    def __init__(self, led_count=300, spi_bus=0, spi_device=0, brightness=30):
        """
        Initialize SK9822 LED test
        
        Args:
            led_count: Number of LEDs (default: 60)
            spi_bus: SPI bus number (default: 0)
            spi_device: SPI device number (default: 0)
            brightness: LED brightness 0-255 (default: 128)
        """
        self.led_count = led_count
        self.brightness = brightness
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        
        print(f"🔧 Initializing SK9822 LED strip with {led_count} LEDs")
        print(f"   SPI Bus: {spi_bus}, Device: {spi_device}")
        
        try:
            # Initialize SPI interface
            self.spi = spidev.SpiDev()
            self.spi.open(spi_bus, spi_device)
            self.spi.max_speed_hz = 2000000  # 2MHz SPI speed for better performance
            self.spi.mode = 0b00  # SPI mode 0
            print("✅ SPI interface initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize SPI: {e}")
            print("Check your SPI settings and permissions")
            exit(1)

    def _start_frame(self):
        """Return the SK9822/APA102 start frame (32 zero bits)."""
        return [0x00] * 4

    def _end_frame(self):
        """Return an appropriate end frame to latch data across the strip.

        Per APA102/SK9822 timing, require at least N/2 clock cycles of 1s
        (N = number of LEDs). That's ceil(N/16) bytes of 0xFF. Keep a
        minimum of 4 bytes for compatibility with short strips.
        """
        bytes_needed = max(4, (self.led_count + 15) // 16)
        return [0xFF] * bytes_needed
    
    def clear_all(self):
        """Turn off all LEDs"""
        # SK9822 requires start frame and a sufficiently long end frame
        start_frame = self._start_frame()
        end_frame = self._end_frame()
        
        # Create data for all LEDs (off)
        led_data = []
        for i in range(self.led_count):
            led_data.extend([0xE1, 0x00, 0x00, 0x00])  # Brightness=0, R=0, G=0, B=0
        
        # Send start frame + LED data + end frame
        data = start_frame + led_data + end_frame
        
        # Send data in chunks for large LED counts to ensure all data is transmitted
        # chunk_size = 1024  # Send in 1KB chunks
        # for i in range(0, len(data), chunk_size):
        #     chunk = data[i:i + chunk_size]
        #     self.spi.xfer2(chunk)
        #     time.sleep(0.001)  # Small delay between chunks
        
        self.spi.xfer2(data)

        print(f"🔴 All {self.led_count} LEDs cleared")
    
    def solid_color(self, red, green, blue):
        """Set all LEDs to the same color"""
        start_frame = self._start_frame()
        end_frame = self._end_frame()
        
        # Create data for all LEDs
        led_data = []
        for i in range(self.led_count):
            # SK9822 format: [Brightness(5 bits) + 3 bits, Blue, Green, Red]
            brightness_byte = 0xE0 | (self.brightness >> 3)  # Top 5 bits for brightness
            led_data.extend([brightness_byte, blue, green, red])
        
        # Send start frame + LED data + end frame
        data = start_frame + led_data + end_frame
        
        # Debug: Print data size
        print(f"📊 Sending {len(data)} bytes for {self.led_count} LEDs")
        
        # Send data in chunks for large LED counts to ensure all data is transmitted
        chunk_size = 1024  # Send in 1KB chunks
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.spi.xfer2(chunk)
            time.sleep(0.001)  # Small delay between chunks
        
        print(f"🎨 Set all {self.led_count} LEDs to RGB({red}, {green}, {blue})")
    
    def rainbow_test(self, duration=5):
        """Simple rainbow pattern"""
        print(f"🌈 Starting rainbow test for {self.led_count} LEDs...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            start_frame = self._start_frame()
            end_frame = self._end_frame()
            
            led_data = []
            for i in range(self.led_count):
                # Create rainbow effect
                hue = (i * 360 / self.led_count + time.time() * 50) % 360
                rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
                
                brightness_byte = 0xE0 | (self.brightness >> 3)
                led_data.extend([brightness_byte, rgb[2], rgb[1], rgb[0]])  # BGR format
            
            data = start_frame + led_data + end_frame
            
            # Send data in chunks for large LED counts
            chunk_size = 1024  # Send in 1KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                self.spi.xfer2(chunk)
                time.sleep(0.001)  # Small delay between chunks
            
            time.sleep(0.1)  # Slower for 300 LEDs
        
        print("✅ Rainbow test completed")
    
    def chase_test(self, duration=5):
        """Simple chase pattern"""
        print(f"🏃 Starting chase test for {self.led_count} LEDs...")
        start_time = time.time()
        position = 0
        
        while time.time() - start_time < duration:
            start_frame = self._start_frame()
            end_frame = self._end_frame()
            
            led_data = []
            for i in range(self.led_count):
                if i == position:
                    # Bright red at current position
                    brightness_byte = 0xE0 | (self.brightness >> 3)
                    led_data.extend([brightness_byte, 0x00, 0x00, 0xFF])  # Red
                elif i == (position + 1) % self.led_count or i == (position - 1) % self.led_count:
                    # Dim red at adjacent positions
                    brightness_byte = 0xE0 | ((self.brightness // 2) >> 3)
                    led_data.extend([brightness_byte, 0x00, 0x00, 0x80])  # Dim red
                else:
                    # Off
                    led_data.extend([0xE0, 0x00, 0x00, 0x00])  # Off
            
            data = start_frame + led_data + end_frame
            
            # Send data in chunks for large LED counts
            chunk_size = 1024  # Send in 1KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                self.spi.xfer2(chunk)
                time.sleep(0.001)  # Small delay between chunks
            
            position = (position + 1) % self.led_count
            time.sleep(0.2)  # Slower for 300 LEDs
        
        print("✅ Chase test completed")
    
    def breathing_test(self, duration=5):
        """Breathing effect"""
        print(f"🫁 Starting breathing test for {self.led_count} LEDs...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Breathing effect with sine wave
            intensity = (math.sin(time.time() * 2) + 1) / 2  # 0 to 1
            current_brightness = int(self.brightness * intensity)
            
            start_frame = self._start_frame()
            end_frame = self._end_frame()
            
            led_data = []
            for i in range(self.led_count):
                brightness_byte = 0xE0 | (current_brightness >> 3)
                led_data.extend([brightness_byte, 0xFF, 0x00, 0xFF])  # Purple
            
            data = start_frame + led_data + end_frame
            
            # Send data in chunks for large LED counts
            chunk_size = 1024  # Send in 1KB chunks
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                self.spi.xfer2(chunk)
                time.sleep(0.001)  # Small delay between chunks
            
            time.sleep(0.1)  # Slower for 300 LEDs
        
        print("✅ Breathing test completed")

    def crawl_once(self, red=255, green=0, blue=0, delay_s=0.02):
        """Move a single lit pixel from start (index 0) to end and stop."""
        print(f"➡️  Crawling single pixel across {self.led_count} LEDs...")
        start_frame = self._start_frame()
        end_frame = self._end_frame()
        brightness_byte = 0xE0 | (self.brightness >> 3)

        for position in range(self.led_count):
            led_data = []
            for i in range(self.led_count):
                if i == position:
                    # Lit pixel at current position (BGR order)
                    led_data.extend([brightness_byte, blue, green, red])
                else:
                    # Off
                    led_data.extend([0xE0, 0x00, 0x00, 0x00])

            data = start_frame + led_data + end_frame

            # Send in chunks
            chunk_size = 1024
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                self.spi.xfer2(chunk)
                # Small delay helps ensure reliable clocking at lower speeds
                # and avoids hammering the SPI bus too hard.
                time.sleep(0.0005)

            time.sleep(delay_s)

        print("✅ Crawl complete")
    
    def brightness_sweep(self, red=255, green=255, blue=255, *, cycles=1,
                         min_level=1, max_level=31, step=1, delay_s=0.02):
        """Light all LEDs and sweep SK9822 global brightness up and down.

        Args:
            red, green, blue: Color to display while sweeping (0-255)
            cycles: Number of up+down sweeps
            min_level, max_level: 5-bit SK9822 brightness header levels (1..31)
            step: Increment step for brightness level
            delay_s: Delay between frames in seconds
        Notes:
            - SK9822 brightness header is 5-bit (0..31). We program it directly via 0xE0 | level.
            - Color bytes are still sent at full intensity; only header level changes perceived brightness.
        """
        print(f"🔆 Brightness sweep on {self.led_count} LEDs (levels {min_level}..{max_level})")
        start_frame = self._start_frame()
        end_frame = self._end_frame()

        def send_frame(level: int):
            level = max(0, min(31, level))
            brightness_byte = 0xE0 | level
            led_data = []
            for _ in range(self.led_count):
                # BGR order for SK9822
                led_data.extend([brightness_byte, blue, green, red])
            data = start_frame + led_data + end_frame
            chunk_size = 1024
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                self.spi.xfer2(chunk)
            time.sleep(delay_s)

        for _ in range(max(1, cycles)):
            # Up
            for lvl in range(min_level, max_level + 1, max(1, step)):
                send_frame(lvl)
            # Down
            for lvl in range(max_level, min_level - 1, -max(1, step)):
                send_frame(lvl)
        print("✅ Brightness sweep complete")
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def run_all_tests(self):
        """Run all basic tests"""
        print("🚀 Starting SK9822 LED strip tests...")
        print("=" * 50)
        
        try:
            # Test 1: Solid colors
            print("\n1️⃣ Testing solid colors...")
            self.solid_color(255, 0, 0)    # Red
            time.sleep(1)
            self.solid_color(0, 255, 0)    # Green
            time.sleep(1)
            self.solid_color(0, 0, 255)    # Blue
            time.sleep(1)
            self.solid_color(255, 255, 255) # White
            time.sleep(1)
            
            # Test 2: Rainbow
            print("\n2️⃣ Testing rainbow pattern...")
            self.rainbow_test(3)
            
            # Test 3: Chase
            print("\n3️⃣ Testing chase pattern...")
            self.chase_test(3)
            
            # Test 4: Breathing
            print("\n4️⃣ Testing breathing pattern...")
            self.breathing_test(3)
            
            # Clear at the end
            print("\n🧹 Clearing all LEDs...")
            self.clear_all()
            
            print("\n✅ All tests completed successfully!")
            print("🎉 Your SK9822 LED strip is working correctly!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
            self.clear_all()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            self.clear_all()
            raise
    
    def cleanup(self):
        """Clean up SPI resources"""
        if hasattr(self, 'spi'):
            self.spi.close()
            print("🧹 SPI interface closed")


def main():
    """Main program: set all LEDs to constant red at ~30% brightness"""
    print("🔌 SK9822 SPI LED Strip – Constant Red @ ~30%")
    print("=" * 50)
    
    # Configuration - adjust these for your setup
    LED_COUNT = 300     # Number of LEDs in your strip (change this to match your strip)
    SPI_BUS = 0         # SPI bus number (usually 0)
    SPI_DEVICE = 0      # SPI device number (usually 0)
    # ~30% brightness on SK9822 header ≈ 0.3 * 255 ≈ 77
    BRIGHTNESS = 77     # Brightness (0-255) mapped to 5-bit header via >> 3
    COLOR = (255, 0, 0) # Solid red
    
    print("Configuration:")
    print(f"  LED Count: {LED_COUNT}")
    print(f"  SPI Bus: {SPI_BUS}")
    print(f"  SPI Device: {SPI_DEVICE}")
    print(f"  Brightness: {BRIGHTNESS}")
    print(f"  Color: RGB{COLOR}")
    print()
    
    # Initialize and set solid color
    try:
        led = SK9822LEDTest(LED_COUNT, SPI_BUS, SPI_DEVICE, BRIGHTNESS)
        led.solid_color(*COLOR)
        print("✅ Set to constant red at ~30% brightness. Press Ctrl+C to exit.")
        # Keep process alive so LEDs remain steady until user exits
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping on user request")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nTroubleshooting:")
        print("1. Check your wiring (MOSI to DI, SCLK to CI, GND, external 5V power)")
        print("2. Verify LED count matches your strip (change LED_COUNT in script)")
        print("3. Ensure SPI is enabled: sudo raspi-config")
        print("4. Check SPI permissions: sudo usermod -a -G spi pi")
        print("5. Verify SPI interface: ls /dev/spi*")
        print("6. Try lowering SPI speed or LED_COUNT for testing")
    finally:
        if 'led' in locals():
            # Do not clear on exit; keep LEDs showing last latched frame
            led.cleanup()


if __name__ == "__main__":
    main()
