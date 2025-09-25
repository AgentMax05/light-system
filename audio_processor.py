#!/usr/bin/env python3
"""
Audio processing module for music visualization
Captures audio input and processes it for LED visualization
"""

import numpy as np
import pyaudio
import threading
import time
from typing import Optional, Callable
from collections import deque
import scipy.fft as fft


class AudioProcessor:
    def __init__(self, sample_rate: int = 44100, chunk_size: int = 1024, 
                 channels: int = 1, led_count: int = 60):
        """
        Initialize audio processor for music visualization
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Number of samples per chunk
            channels: Number of audio channels
            led_count: Number of LEDs to visualize
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.led_count = led_count
        
        self.audio_stream = None
        self.is_running = False
        self.audio_thread = None
        
        # Audio processing buffers
        self.audio_buffer = deque(maxlen=10)  # Keep last 10 chunks
        self.fft_buffer = deque(maxlen=5)     # Keep last 5 FFT results
        
        # Visualization data
        self.frequency_bins = None
        self.amplitude_data = None
        self.beat_detection = False
        self.bass_intensity = 0.0
        self.treble_intensity = 0.0
        
        # Callbacks
        self.visualization_callback = None
        self.beat_callback = None
        
        # Initialize frequency bins for LED mapping
        self._init_frequency_bins()
    
    def _init_frequency_bins(self):
        """Initialize frequency bins for LED mapping"""
        # Create frequency bins for different ranges
        self.frequency_bins = {
            'bass': (0, 250),      # 0-250 Hz
            'low_mid': (250, 500), # 250-500 Hz
            'mid': (500, 2000),    # 500-2000 Hz
            'high_mid': (2000, 4000), # 2000-4000 Hz
            'treble': (4000, 8000) # 4000-8000 Hz
        }
    
    def set_visualization_callback(self, callback: Callable):
        """Set callback for visualization data"""
        self.visualization_callback = callback
    
    def set_beat_callback(self, callback: Callable):
        """Set callback for beat detection"""
        self.beat_callback = callback
    
    def start_capture(self):
        """Start audio capture"""
        if self.is_running:
            return
        
        try:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_running = True
            self.audio_stream.start_stream()
            print("Audio capture started")
            
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
            raise
    
    def stop_capture(self):
        """Stop audio capture"""
        self.is_running = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
        
        if hasattr(self, 'audio'):
            self.audio.terminate()
        
        print("Audio capture stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if not self.is_running:
            return (None, pyaudio.paComplete)
        
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Add to buffer
            self.audio_buffer.append(audio_data)
            
            # Process audio for visualization
            self._process_audio(audio_data)
            
        except Exception as e:
            print(f"Audio callback error: {e}")
        
        return (None, pyaudio.paContinue)
    
    def _process_audio(self, audio_data: np.ndarray):
        """Process audio data for visualization"""
        try:
            # Convert to float and normalize
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Apply window function to reduce spectral leakage
            windowed = audio_float * np.hanning(len(audio_float))
            
            # Compute FFT
            fft_data = fft.fft(windowed)
            fft_magnitude = np.abs(fft_data[:len(fft_data)//2])
            
            # Add to FFT buffer
            self.fft_buffer.append(fft_magnitude)
            
            # Calculate frequency bins
            freqs = fft.fftfreq(len(fft_data), 1/self.sample_rate)[:len(fft_data)//2]
            
            # Extract frequency ranges
            self._extract_frequency_ranges(fft_magnitude, freqs)
            
            # Detect beats
            self._detect_beats(fft_magnitude)
            
            # Create visualization data
            visualization_data = self._create_visualization_data(fft_magnitude, freqs)
            
            # Call visualization callback
            if self.visualization_callback:
                self.visualization_callback(visualization_data)
                
        except Exception as e:
            print(f"Audio processing error: {e}")
    
    def _extract_frequency_ranges(self, fft_magnitude: np.ndarray, freqs: np.ndarray):
        """Extract intensity for different frequency ranges"""
        try:
            # Bass (0-250 Hz)
            bass_mask = (freqs >= 0) & (freqs <= 250)
            self.bass_intensity = np.mean(fft_magnitude[bass_mask]) if np.any(bass_mask) else 0.0
            
            # Treble (4000-8000 Hz)
            treble_mask = (freqs >= 4000) & (freqs <= 8000)
            self.treble_intensity = np.mean(fft_magnitude[treble_mask]) if np.any(treble_mask) else 0.0
            
        except Exception as e:
            print(f"Frequency extraction error: {e}")
    
    def _detect_beats(self, fft_magnitude: np.ndarray):
        """Simple beat detection using energy analysis"""
        try:
            if len(self.fft_buffer) < 3:
                return
            
            # Calculate energy
            current_energy = np.sum(fft_magnitude)
            
            # Get previous energies
            prev_energies = [np.sum(fft) for fft in list(self.fft_buffer)[-3:-1]]
            
            if len(prev_energies) >= 2:
                avg_prev_energy = np.mean(prev_energies)
                
                # Beat detected if current energy is significantly higher
                if current_energy > avg_prev_energy * 1.3:
                    self.beat_detection = True
                    if self.beat_callback:
                        self.beat_callback()
                else:
                    self.beat_detection = False
                    
        except Exception as e:
            print(f"Beat detection error: {e}")
    
    def _create_visualization_data(self, fft_magnitude: np.ndarray, freqs: np.ndarray) -> dict:
        """Create visualization data for LEDs"""
        try:
            # Map frequency bins to LED positions
            led_data = np.zeros(self.led_count)
            
            # Create frequency bands for LED mapping
            freq_bands = np.logspace(np.log10(20), np.log10(8000), self.led_count + 1)
            
            for i in range(self.led_count):
                # Find frequencies in this band
                band_mask = (freqs >= freq_bands[i]) & (freqs < freq_bands[i + 1])
                
                if np.any(band_mask):
                    # Average magnitude in this frequency band
                    led_data[i] = np.mean(fft_magnitude[band_mask])
                else:
                    led_data[i] = 0.0
            
            # Normalize data
            if np.max(led_data) > 0:
                led_data = led_data / np.max(led_data)
            
            return {
                'led_data': led_data,
                'bass_intensity': self.bass_intensity,
                'treble_intensity': self.treble_intensity,
                'beat_detected': self.beat_detection,
                'overall_amplitude': np.mean(fft_magnitude)
            }
            
        except Exception as e:
            print(f"Visualization data creation error: {e}")
            return {
                'led_data': np.zeros(self.led_count),
                'bass_intensity': 0.0,
                'treble_intensity': 0.0,
                'beat_detected': False,
                'overall_amplitude': 0.0
            }
    
    def get_audio_levels(self) -> dict:
        """Get current audio levels for display"""
        if not self.fft_buffer:
            return {
                'bass': 0.0,
                'treble': 0.0,
                'overall': 0.0,
                'beat': False
            }
        
        latest_fft = list(self.fft_buffer)[-1]
        
        return {
            'bass': float(self.bass_intensity),
            'treble': float(self.treble_intensity),
            'overall': float(np.mean(latest_fft)),
            'beat': self.beat_detection
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_capture()


class MusicVisualizer:
    """Music visualization patterns for LED strips"""
    
    def __init__(self, led_count: int = 60):
        self.led_count = led_count
        self.beat_history = deque(maxlen=20)
        self.energy_history = deque(maxlen=50)
    
    def spectrum_visualization(self, audio_data: dict) -> np.ndarray:
        """Create spectrum visualization from audio data"""
        led_data = audio_data['led_data']
        
        # Apply smoothing
        smoothed = self._smooth_data(led_data)
        
        # Convert to RGB values
        colors = np.zeros((self.led_count, 3))
        
        for i, intensity in enumerate(smoothed):
            # Map intensity to color (blue to red)
            if intensity > 0.5:
                # High intensity - red
                colors[i] = [intensity * 255, (1 - intensity) * 255, 0]
            else:
                # Low intensity - blue
                colors[i] = [0, 0, intensity * 255]
        
        return colors
    
    def beat_visualization(self, audio_data: dict) -> np.ndarray:
        """Create beat-based visualization"""
        colors = np.zeros((self.led_count, 3))
        
        if audio_data['beat_detected']:
            # Flash white on beat
            colors.fill(255)
        else:
            # Fade based on bass intensity
            bass_intensity = audio_data['bass_intensity']
            colors[:, 0] = bass_intensity * 255  # Red channel
            colors[:, 1] = bass_intensity * 128   # Green channel
            colors[:, 2] = 0                      # Blue channel
        
        return colors
    
    def frequency_bars(self, audio_data: dict) -> np.ndarray:
        """Create frequency bar visualization"""
        colors = np.zeros((self.led_count, 3))
        led_data = audio_data['led_data']
        
        # Group LEDs into frequency bars
        bars = 8  # Number of frequency bars
        leds_per_bar = self.led_count // bars
        
        for bar in range(bars):
            start_led = bar * leds_per_bar
            end_led = min((bar + 1) * leds_per_bar, self.led_count)
            
            # Calculate bar intensity
            bar_intensity = np.mean(led_data[start_led:end_led])
            
            # Color based on frequency range
            if bar < 2:  # Bass
                color = [bar_intensity * 255, 0, 0]  # Red
            elif bar < 4:  # Mid
                color = [0, bar_intensity * 255, 0]  # Green
            else:  # Treble
                color = [0, 0, bar_intensity * 255]  # Blue
            
            colors[start_led:end_led] = color
        
        return colors
    
    def _smooth_data(self, data: np.ndarray, window_size: int = 3) -> np.ndarray:
        """Apply smoothing to data"""
        if len(data) < window_size:
            return data
        
        smoothed = np.zeros_like(data)
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            smoothed[i] = np.mean(data[start:end])
        
        return smoothed


if __name__ == "__main__":
    # Test audio processor
    processor = AudioProcessor(led_count=60)
    
    def visualization_callback(data):
        print(f"Bass: {data['bass_intensity']:.3f}, "
              f"Treble: {data['treble_intensity']:.3f}, "
              f"Beat: {data['beat_detected']}")
    
    def beat_callback():
        print("BEAT DETECTED!")
    
    processor.set_visualization_callback(visualization_callback)
    processor.set_beat_callback(beat_callback)
    
    try:
        processor.start_capture()
        print("Audio processor started. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping audio processor...")
    finally:
        processor.cleanup()
