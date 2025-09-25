#!/usr/bin/env python3
"""
Simple LED Strip Test Script
Basic test to turn on LEDs with simple patterns
"""

import time
import math

try:
    from rpi_ws281x import PixelStrip, Color
    print("✅ rpi_ws281x library found")
except ImportError:
    print("❌ rpi_ws281x library not found")
    print("Install with: pip install rpi-ws281x")
    exit(1)


class SimpleLEDTest:
    def __init__(self, led_count=30, pin=18, brightness=128):
        """
        Initialize simple LED test
        
        Args:
            led_count: Number of LEDs (default: 30)
            pin: GPIO pin (default: 18)
            brightness: LED brightness 0-255 (default: 128)
        """
        self.led_count = led_count
        self.pin = pin
        self.brightness = brightness
        
        print(f"🔧 Initializing LED strip with {led_count} LEDs on GPIO {pin}")
        
        try:
            # Initialize the LED strip
            self.strip = PixelStrip(
                num=led_count,
                pin=pin,
                freq_hz=800000,
                dma=10,
                invert=False,
                brightness=brightness,
                channel=0
            )
            self.strip.begin()
            print("✅ LED strip initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize LED strip: {e}")
            print("Check your wiring and GPIO settings")
            exit(1)
    
    def clear_all(self):
        """Turn off all LEDs"""
        for i in range(self.led_count):
            self.strip.setPixelColor(i, Color.RGB(0, 0, 0))
        self.strip.show()
        print("🔴 All LEDs cleared")
    
    def solid_color(self, red, green, blue):
        """Set all LEDs to the same color"""
        color = Color.RGB(red, green, blue)
        for i in range(self.led_count):
            self.strip.setPixelColor(i, color)
        self.strip.show()
        print(f"🎨 Set all LEDs to RGB({red}, {green}, {blue})")
    
    def rainbow_test(self, duration=5):
        """Simple rainbow pattern"""
        print("🌈 Starting rainbow test...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            for i in range(self.led_count):
                # Create rainbow effect
                hue = (i * 360 / self.led_count + time.time() * 50) % 360
                rgb = self.hsv_to_rgb(hue, 1.0, 1.0)
                self.strip.setPixelColor(i, Color.RGB(rgb[0], rgb[1], rgb[2]))
            
            self.strip.show()
            time.sleep(0.05)  # 20 FPS
        
        print("✅ Rainbow test completed")
    
    def chase_test(self, duration=5):
        """Simple chase pattern"""
        print("🏃 Starting chase test...")
        start_time = time.time()
        position = 0
        
        while time.time() - start_time < duration:
            # Clear all LEDs
            for i in range(self.led_count):
                self.strip.setPixelColor(i, Color.RGB(0, 0, 0))
            
            # Light up current position
            self.strip.setPixelColor(position, Color.RGB(255, 0, 0))  # Red
            self.strip.setPixelColor((position + 1) % self.led_count, Color.RGB(128, 0, 0))  # Dim red
            self.strip.setPixelColor((position - 1) % self.led_count, Color.RGB(128, 0, 0))  # Dim red
            
            self.strip.show()
            position = (position + 1) % self.led_count
            time.sleep(0.1)
        
        print("✅ Chase test completed")
    
    def breathing_test(self, duration=5):
        """Breathing effect"""
        print("🫁 Starting breathing test...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Breathing effect with sine wave
            intensity = (math.sin(time.time() * 2) + 1) / 2  # 0 to 1
            brightness = int(255 * intensity)
            
            for i in range(self.led_count):
                self.strip.setPixelColor(i, Color.RGB(brightness, 0, brightness))  # Purple
            
            self.strip.show()
            time.sleep(0.05)
        
        print("✅ Breathing test completed")
    
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
        print("🚀 Starting LED strip tests...")
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
            print("🎉 Your LED strip is working correctly!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Tests interrupted by user")
            self.clear_all()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            self.clear_all()
            raise


def main():
    """Main test function"""
    print("🔌 Simple LED Strip Test")
    print("=" * 30)
    
    # Configuration - adjust these for your setup
    LED_COUNT = 30      # Number of LEDs in your strip
    GPIO_PIN = 18       # GPIO pin connected to LED data line
    BRIGHTNESS = 128    # Brightness (0-255)
    
    print(f"Configuration:")
    print(f"  LED Count: {LED_COUNT}")
    print(f"  GPIO Pin: {GPIO_PIN}")
    print(f"  Brightness: {BRIGHTNESS}")
    print()
    
    # Create and run tests
    try:
        led_test = SimpleLEDTest(LED_COUNT, GPIO_PIN, BRIGHTNESS)
        led_test.run_all_tests()
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\nTroubleshooting:")
        print("1. Check your wiring (GPIO 18, GND, external 5V power)")
        print("2. Verify LED count matches your strip")
        print("3. Ensure rpi_ws281x library is installed")
        print("4. Check if GPIO is enabled: sudo raspi-config")


if __name__ == "__main__":
    main()
