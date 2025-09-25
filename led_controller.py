#!/usr/bin/env python3
"""
LED Strip Controller for Raspberry Pi
Controls WS2812B individually addressable LED strips
"""

import time
import math
import threading
import json
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np

try:
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    print("Warning: rpi_ws281x not installed. Install with: pip install rpi-ws281x")
    # Mock classes for development
    class Color:
        @staticmethod
        def RGB(red, green, blue):
            return (red << 16) | (green << 8) | blue
    
    class PixelStrip:
        def __init__(self, *args, **kwargs):
            self.numPixels = kwargs.get('num', 0)
            self.pixels = [0] * self.numPixels
        
        def setPixelColor(self, index, color):
            if 0 <= index < self.numPixels:
                self.pixels[index] = color
        
        def show(self):
            pass
        
        def begin(self):
            pass


class PatternType(Enum):
    SOLID = "solid"
    RAINBOW = "rainbow"
    CHASE = "chase"
    FADE = "fade"
    BREATHING = "breathing"
    TWINKLE = "twinkle"
    WAVE = "wave"
    FIRE = "fire"
    MUSIC = "music"


@dataclass
class ColorRGB:
    red: int
    green: int
    blue: int
    
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.red, self.green, self.blue)
    
    def to_hex(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'ColorRGB':
        hex_color = hex_color.lstrip('#')
        return cls(
            red=int(hex_color[0:2], 16),
            green=int(hex_color[2:4], 16),
            blue=int(hex_color[4:6], 16)
        )
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> 'ColorRGB':
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
        
        return cls(
            red=int((r + m) * 255),
            green=int((g + m) * 255),
            blue=int((b + m) * 255)
        )


class LEDController:
    def __init__(self, led_count: int = 60, pin: int = 18, freq_hz: int = 800000, 
                 dma: int = 10, invert: bool = False, brightness: int = 255, 
                 channel: int = 0):
        """
        Initialize LED controller
        
        Args:
            led_count: Number of LEDs in the strip
            pin: GPIO pin connected to the LED strip data line
            freq_hz: LED signal frequency in Hz
            dma: DMA channel to use for generating signal
            invert: Invert the signal (when using a level shifter)
            brightness: LED brightness (0-255)
            channel: PWM channel
        """
        self.led_count = led_count
        self.pin = pin
        self.brightness = brightness
        self.current_pattern = PatternType.SOLID
        self.is_running = False
        self.animation_thread = None
        self.animation_speed = 1.0
        self.primary_color = ColorRGB(255, 0, 0)  # Red
        self.secondary_color = ColorRGB(0, 0, 255)  # Blue
        self.audio_data = None
        self.audio_callback = None
        
        # Initialize the LED strip
        try:
            self.strip = PixelStrip(
                num=led_count,
                pin=pin,
                freq_hz=freq_hz,
                dma=dma,
                invert=invert,
                brightness=brightness,
                channel=channel
            )
            self.strip.begin()
            print(f"LED strip initialized with {led_count} LEDs")
        except Exception as e:
            print(f"Error initializing LED strip: {e}")
            self.strip = None
    
    def set_brightness(self, brightness: int):
        """Set LED strip brightness (0-255)"""
        self.brightness = max(0, min(255, brightness))
        if self.strip:
            self.strip.setBrightness(self.brightness)
    
    def set_color(self, color: ColorRGB):
        """Set primary color"""
        self.primary_color = color
    
    def set_secondary_color(self, color: ColorRGB):
        """Set secondary color"""
        self.secondary_color = color
    
    def set_animation_speed(self, speed: float):
        """Set animation speed multiplier"""
        self.animation_speed = max(0.1, min(10.0, speed))
    
    def set_pattern(self, pattern: PatternType):
        """Set current pattern"""
        self.current_pattern = pattern
        if self.is_running:
            self.stop_animation()
            self.start_animation()
    
    def set_audio_callback(self, callback: Callable):
        """Set callback function for audio data"""
        self.audio_callback = callback
    
    def set_audio_data(self, data: Optional[np.ndarray]):
        """Set current audio data for music visualization"""
        self.audio_data = data
    
    def start_animation(self):
        """Start the animation loop"""
        if self.is_running:
            return
        
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stop the animation loop"""
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
    
    def clear(self):
        """Turn off all LEDs"""
        if self.strip:
            for i in range(self.led_count):
                self.strip.setPixelColor(i, Color.RGB(0, 0, 0))
            self.strip.show()
    
    def set_pixel(self, index: int, color: ColorRGB):
        """Set individual pixel color"""
        if self.strip and 0 <= index < self.led_count:
            self.strip.setPixelColor(index, Color.RGB(color.red, color.green, color.blue))
    
    def set_all_pixels(self, color: ColorRGB):
        """Set all pixels to the same color"""
        if self.strip:
            for i in range(self.led_count):
                self.strip.setPixelColor(i, Color.RGB(color.red, color.green, color.blue))
            self.strip.show()
    
    def _animation_loop(self):
        """Main animation loop"""
        frame = 0
        while self.is_running:
            try:
                if self.current_pattern == PatternType.SOLID:
                    self._solid_pattern()
                elif self.current_pattern == PatternType.RAINBOW:
                    self._rainbow_pattern(frame)
                elif self.current_pattern == PatternType.CHASE:
                    self._chase_pattern(frame)
                elif self.current_pattern == PatternType.FADE:
                    self._fade_pattern(frame)
                elif self.current_pattern == PatternType.BREATHING:
                    self._breathing_pattern(frame)
                elif self.current_pattern == PatternType.TWINKLE:
                    self._twinkle_pattern(frame)
                elif self.current_pattern == PatternType.WAVE:
                    self._wave_pattern(frame)
                elif self.current_pattern == PatternType.FIRE:
                    self._fire_pattern(frame)
                elif self.current_pattern == PatternType.MUSIC:
                    self._music_pattern(frame)
                
                if self.strip:
                    self.strip.show()
                
                frame += 1
                time.sleep(0.05 / self.animation_speed)  # ~20 FPS base
                
            except Exception as e:
                print(f"Animation error: {e}")
                time.sleep(0.1)
    
    def _solid_pattern(self):
        """Solid color pattern"""
        self.set_all_pixels(self.primary_color)
    
    def _rainbow_pattern(self, frame: int):
        """Rainbow pattern"""
        for i in range(self.led_count):
            hue = (i * 360 / self.led_count + frame * 2) % 360
            color = ColorRGB.from_hsv(hue, 1.0, 1.0)
            self.set_pixel(i, color)
    
    def _chase_pattern(self, frame: int):
        """Chase pattern"""
        for i in range(self.led_count):
            if (i + frame) % 3 == 0:
                self.set_pixel(i, self.primary_color)
            else:
                self.set_pixel(i, ColorRGB(0, 0, 0))
    
    def _fade_pattern(self, frame: int):
        """Fade pattern"""
        intensity = (math.sin(frame * 0.1) + 1) / 2
        color = ColorRGB(
            int(self.primary_color.red * intensity),
            int(self.primary_color.green * intensity),
            int(self.primary_color.blue * intensity)
        )
        self.set_all_pixels(color)
    
    def _breathing_pattern(self, frame: int):
        """Breathing pattern"""
        intensity = (math.sin(frame * 0.05) + 1) / 2
        color = ColorRGB(
            int(self.primary_color.red * intensity),
            int(self.primary_color.green * intensity),
            int(self.primary_color.blue * intensity)
        )
        self.set_all_pixels(color)
    
    def _twinkle_pattern(self, frame: int):
        """Twinkle pattern"""
        for i in range(self.led_count):
            if (i + frame) % 10 == 0:
                intensity = (math.sin(frame * 0.2 + i) + 1) / 2
                color = ColorRGB(
                    int(self.primary_color.red * intensity),
                    int(self.primary_color.green * intensity),
                    int(self.primary_color.blue * intensity)
                )
                self.set_pixel(i, color)
            else:
                self.set_pixel(i, ColorRGB(0, 0, 0))
    
    def _wave_pattern(self, frame: int):
        """Wave pattern"""
        for i in range(self.led_count):
            wave = math.sin((i + frame * 0.5) * 0.3) * 0.5 + 0.5
            color = ColorRGB(
                int(self.primary_color.red * wave),
                int(self.primary_color.green * wave),
                int(self.primary_color.blue * wave)
            )
            self.set_pixel(i, color)
    
    def _fire_pattern(self, frame: int):
        """Fire pattern"""
        for i in range(self.led_count):
            # Simulate fire with random flickering
            flicker = np.random.random()
            if flicker > 0.3:
                intensity = flicker
                color = ColorRGB(
                    int(255 * intensity),
                    int(100 * intensity),
                    int(20 * intensity)
                )
                self.set_pixel(i, color)
            else:
                self.set_pixel(i, ColorRGB(0, 0, 0))
    
    def _music_pattern(self, frame: int):
        """Music visualization pattern"""
        if self.audio_data is not None and len(self.audio_data) > 0:
            # Use audio data to create visualization
            audio_intensity = np.mean(np.abs(self.audio_data))
            color_intensity = min(1.0, audio_intensity * 10)
            
            for i in range(self.led_count):
                # Create frequency-based visualization
                freq_bin = int((i / self.led_count) * len(self.audio_data))
                if freq_bin < len(self.audio_data):
                    freq_intensity = abs(self.audio_data[freq_bin])
                    color = ColorRGB(
                        int(self.primary_color.red * freq_intensity * color_intensity),
                        int(self.primary_color.green * freq_intensity * color_intensity),
                        int(self.primary_color.blue * freq_intensity * color_intensity)
                    )
                    self.set_pixel(i, color)
                else:
                    self.set_pixel(i, ColorRGB(0, 0, 0))
        else:
            # Fallback to rainbow if no audio data
            self._rainbow_pattern(frame)
    
    def get_status(self) -> dict:
        """Get current controller status"""
        return {
            "led_count": self.led_count,
            "brightness": self.brightness,
            "current_pattern": self.current_pattern.value,
            "is_running": self.is_running,
            "animation_speed": self.animation_speed,
            "primary_color": {
                "red": self.primary_color.red,
                "green": self.primary_color.green,
                "blue": self.primary_color.blue,
                "hex": self.primary_color.to_hex()
            },
            "secondary_color": {
                "red": self.secondary_color.red,
                "green": self.secondary_color.green,
                "blue": self.secondary_color.blue,
                "hex": self.secondary_color.to_hex()
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_animation()
        self.clear()
        if self.strip:
            self.strip = None


if __name__ == "__main__":
    # Test the LED controller
    controller = LEDController(led_count=60)
    
    try:
        # Test different patterns
        patterns = [PatternType.SOLID, PatternType.RAINBOW, PatternType.CHASE, PatternType.FADE]
        
        for pattern in patterns:
            print(f"Testing {pattern.value} pattern...")
            controller.set_pattern(pattern)
            controller.start_animation()
            time.sleep(5)
            controller.stop_animation()
        
        print("LED controller test completed")
        
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        controller.cleanup()
