"""
SK9822/APA102 LED strip controller for Raspberry Pi using SPI
Adapted from custom_test.py for use with audio-reactive-led-strip
"""
from __future__ import print_function
from __future__ import division

import numpy as np

try:
    import spidev
    SPI_AVAILABLE = True
except ImportError:
    print("Warning: spidev not available. SK9822 control will not work.")
    SPI_AVAILABLE = False


class SK9822Controller:
    """Controller for SK9822/APA102 LED strips using SPI interface"""
    
    def __init__(self, num_leds, spi_bus=0, spi_device=0, max_speed_hz=1000000, 
                 brightness=31, software_gamma=True):
        """
        Initialize SK9822 LED controller
        
        Parameters
        ----------
        num_leds : int
            Number of LEDs in the strip
        spi_bus : int
            SPI bus number (usually 0)
        spi_device : int
            SPI device number (usually 0)
        max_speed_hz : int
            SPI clock speed in Hz (1MHz default, can go up to 4MHz)
        brightness : int
            Global brightness (0-31), default is maximum (31)
        software_gamma : bool
            Whether to apply software gamma correction
        """
        if not SPI_AVAILABLE:
            raise RuntimeError("spidev is not installed. Cannot use SK9822 LEDs.")
        
        self.num_leds = num_leds
        self.brightness = brightness
        self.software_gamma = software_gamma
        
        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 0
        self.spi.lsbfirst = False
        
        # Previous pixel values for change detection
        self._prev_pixels = np.tile(253, (3, num_leds))
        
        print(f"SK9822 controller initialized: {num_leds} LEDs on SPI {spi_bus}.{spi_device} @ {max_speed_hz}Hz")
    
    def set_led(self, index, color, brightness, dataframe):
        """
        Set a single LED in the data frame
        
        Parameters
        ----------
        index : int
            LED index (0-based)
        color : tuple
            (R, G, B) color tuple (0-255)
        brightness : int
            LED brightness (0-31)
        dataframe : list
            LED data frame to modify
        """
        # SK9822 format: [brightness byte, B, G, R]
        # Brightness byte: 0xE0 | brightness (0-31)
        dataframe[index*4:index*4+4] = [0xE0 | brightness, color[2], color[1], color[0]]
    
    def send_data(self, led_data):
        """
        Send LED data to the strip via SPI
        
        Parameters
        ----------
        led_data : list
            Raw LED data (without start/end frames)
        """
        data = []
        # Start frame: 4 bytes of 0x00
        data += [0x00, 0x00, 0x00, 0x00]
        # LED data - ensure all values are Python ints, not numpy types
        data += [int(x) for x in led_data]
        # End frame: depends on number of LEDs
        # Formula: max(4, (NUM_LEDS + 15) // 16) ones + 4 zeros
        data += [0xFF] * max(4, (self.num_leds + 15) // 16) + [0x00, 0x00, 0x00, 0x00]
        
        self.spi.xfer2(data)
    
    def update(self, pixels, gamma_table=None):
        """
        Update the LED strip with new pixel values
        
        Parameters
        ----------
        pixels : np.array
            3D array of shape (3, N_PIXELS) with RGB values (0-255)
            pixels[0] = red channel
            pixels[1] = green channel
            pixels[2] = blue channel
        gamma_table : np.array, optional
            Gamma correction lookup table
        """
        # Clip values to valid range and convert to int
        pixels = np.clip(pixels, 0, 255).astype(int)
        
        # Apply gamma correction if enabled and table provided
        if self.software_gamma and gamma_table is not None:
            p = gamma_table[pixels]
        else:
            p = np.copy(pixels)
        
        # Build LED data frame
        # Initialize with all LEDs off at specified brightness
        led_data = [int(0xE0 | self.brightness), 0x00, 0x00, 0x00] * self.num_leds
        
        # Set each LED
        for i in range(self.num_leds):
            # Only update if pixel changed (optimization)
            if not np.array_equal(p[:, i], self._prev_pixels[:, i]):
                r, g, b = int(p[0, i]), int(p[1, i]), int(p[2, i])
                self.set_led(i, (r, g, b), self.brightness, led_data)
        
        # Send to strip
        self.send_data(led_data)
        
        # Update previous values
        self._prev_pixels = np.copy(p)
    
    def clear(self):
        """Turn off all LEDs"""
        led_data = [0xE0 | 1, 0x00, 0x00, 0x00] * self.num_leds
        self.send_data(led_data)
    
    def set_brightness(self, brightness):
        """
        Set global brightness
        
        Parameters
        ----------
        brightness : int
            Brightness value (0-31)
        """
        self.brightness = np.clip(brightness, 0, 31)
    
    def close(self):
        """Close SPI connection and turn off LEDs"""
        self.clear()
        self.spi.close()
        print("SK9822 controller closed")


# Test code
if __name__ == '__main__':
    import time
    
    NUM_LEDS = 300
    controller = SK9822Controller(num_leds=NUM_LEDS, brightness=5)
    
    try:
        print("Testing SK9822 controller...")
        
        # Test 1: Crawling red LED
        print("Test 1: Crawling red LED")
        for i in range(NUM_LEDS):
            pixels = np.zeros((3, NUM_LEDS), dtype=int)
            pixels[0, i] = 255  # Red
            controller.update(pixels)
            time.sleep(0.01)
        
        # Test 2: Rainbow cycle
        print("Test 2: Rainbow cycle")
        import math
        for j in range(0, 256, 10):
            pixels = np.zeros((3, NUM_LEDS), dtype=int)
            for i in range(NUM_LEDS):
                idx = ((i + j) * 256 // NUM_LEDS)
                pixels[0, i] = int((math.sin(idx * 6.28318 / 256) + 1) * 127.5)
                pixels[1, i] = int((math.sin(idx * 6.28318 / 256 + 2) + 1) * 127.5)
                pixels[2, i] = int((math.sin(idx * 6.28318 / 256 + 4) + 1) * 127.5)
            controller.update(pixels)
            time.sleep(0.05)
        
        # Clear all
        print("Clearing all LEDs")
        controller.clear()
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        controller.close()
