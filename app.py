#!/usr/bin/env python3
"""
Flask web application for LED strip control
Provides REST API and web interface
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
import pyaudio
import schedule

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from led_controller import LEDController, PatternType, ColorRGB

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global LED controller instance
led_controller = None
audio_stream = None
audio_thread = None
scheduler_thread = None

# Configuration
LED_COUNT = int(os.getenv('LED_COUNT', 60))
LED_PIN = int(os.getenv('LED_PIN', 18))
DEFAULT_BRIGHTNESS = int(os.getenv('DEFAULT_BRIGHTNESS', 128))

# Audio configuration
AUDIO_CHUNK_SIZE = 1024
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100

# Scheduled patterns storage
scheduled_patterns = []


def init_led_controller():
    """Initialize the LED controller"""
    global led_controller
    try:
        led_controller = LEDController(
            led_count=LED_COUNT,
            pin=LED_PIN,
            brightness=DEFAULT_BRIGHTNESS
        )
        print(f"LED controller initialized with {LED_COUNT} LEDs")
        return True
    except Exception as e:
        print(f"Failed to initialize LED controller: {e}")
        return False


def start_audio_capture():
    """Start audio capture for music visualization"""
    global audio_stream, audio_thread
    
    if audio_thread and audio_thread.is_alive():
        return
    
    def audio_worker():
        global audio_stream
        try:
            p = pyaudio.PyAudio()
            audio_stream = p.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK_SIZE
            )
            
            while True:
                try:
                    data = audio_stream.read(AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Process audio data for visualization
                    if led_controller:
                        led_controller.set_audio_data(audio_data)
                        
                except Exception as e:
                    print(f"Audio capture error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
        finally:
            if audio_stream:
                audio_stream.stop_stream()
                audio_stream.close()
    
    audio_thread = threading.Thread(target=audio_worker, daemon=True)
    audio_thread.start()


def start_scheduler():
    """Start the pattern scheduler"""
    global scheduler_thread
    
    if scheduler_thread and scheduler_thread.is_alive():
        return
    
    def scheduler_worker():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
    scheduler_thread.start()


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current LED controller status"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    return jsonify(led_controller.get_status())


@app.route('/api/pattern', methods=['POST'])
def set_pattern():
    """Set LED pattern"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        data = request.get_json()
        pattern_name = data.get('pattern')
        
        if pattern_name not in [p.value for p in PatternType]:
            return jsonify({"error": "Invalid pattern"}), 400
        
        pattern = PatternType(pattern_name)
        led_controller.set_pattern(pattern)
        
        return jsonify({"success": True, "pattern": pattern_name})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/color', methods=['POST'])
def set_color():
    """Set LED colors"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        data = request.get_json()
        
        if 'primary' in data:
            color_data = data['primary']
            if 'hex' in color_data:
                color = ColorRGB.from_hex(color_data['hex'])
            else:
                color = ColorRGB(
                    color_data.get('red', 255),
                    color_data.get('green', 0),
                    color_data.get('blue', 0)
                )
            led_controller.set_color(color)
        
        if 'secondary' in data:
            color_data = data['secondary']
            if 'hex' in color_data:
                color = ColorRGB.from_hex(color_data['hex'])
            else:
                color = ColorRGB(
                    color_data.get('red', 0),
                    color_data.get('green', 0),
                    color_data.get('blue', 255)
                )
            led_controller.set_secondary_color(color)
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/brightness', methods=['POST'])
def set_brightness():
    """Set LED brightness"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        data = request.get_json()
        brightness = data.get('brightness', 128)
        
        if not isinstance(brightness, int) or brightness < 0 or brightness > 255:
            return jsonify({"error": "Brightness must be between 0 and 255"}), 400
        
        led_controller.set_brightness(brightness)
        return jsonify({"success": True, "brightness": brightness})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/speed', methods=['POST'])
def set_speed():
    """Set animation speed"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        data = request.get_json()
        speed = data.get('speed', 1.0)
        
        if not isinstance(speed, (int, float)) or speed < 0.1 or speed > 10.0:
            return jsonify({"error": "Speed must be between 0.1 and 10.0"}), 400
        
        led_controller.set_animation_speed(speed)
        return jsonify({"success": True, "speed": speed})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/start', methods=['POST'])
def start_animation():
    """Start LED animation"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        led_controller.start_animation()
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_animation():
    """Stop LED animation"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        led_controller.stop_animation()
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_leds():
    """Clear all LEDs"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    try:
        led_controller.clear()
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/audio/start', methods=['POST'])
def start_audio():
    """Start audio capture for music visualization"""
    try:
        start_audio_capture()
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/audio/stop', methods=['POST'])
def stop_audio():
    """Stop audio capture"""
    global audio_stream
    
    try:
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
            audio_stream = None
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedule', methods=['POST'])
def schedule_pattern():
    """Schedule a pattern to run at a specific time"""
    try:
        data = request.get_json()
        
        pattern_name = data.get('pattern')
        time_str = data.get('time')  # Format: "HH:MM"
        duration = data.get('duration', 60)  # Duration in minutes
        
        if pattern_name not in [p.value for p in PatternType]:
            return jsonify({"error": "Invalid pattern"}), 400
        
        # Parse time
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM"}), 400
        
        # Schedule the pattern
        def run_scheduled_pattern():
            if led_controller:
                led_controller.set_pattern(PatternType(pattern_name))
                led_controller.start_animation()
                time.sleep(duration * 60)  # Convert to seconds
                led_controller.stop_animation()
        
        schedule.every().day.at(time_str).do(run_scheduled_pattern)
        
        scheduled_patterns.append({
            "pattern": pattern_name,
            "time": time_str,
            "duration": duration,
            "created": datetime.now().isoformat()
        })
        
        return jsonify({"success": True, "scheduled": len(scheduled_patterns)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/schedule', methods=['GET'])
def get_scheduled_patterns():
    """Get all scheduled patterns"""
    return jsonify({"scheduled_patterns": scheduled_patterns})


@app.route('/api/schedule/<int:index>', methods=['DELETE'])
def delete_scheduled_pattern(index):
    """Delete a scheduled pattern"""
    try:
        if 0 <= index < len(scheduled_patterns):
            del scheduled_patterns[index]
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Invalid pattern index"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get available pattern presets"""
    presets = {
        "patterns": [p.value for p in PatternType],
        "colors": {
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF",
            "yellow": "#FFFF00",
            "purple": "#800080",
            "orange": "#FFA500",
            "pink": "#FFC0CB",
            "cyan": "#00FFFF"
        }
    }
    return jsonify(presets)


@app.route('/api/export', methods=['GET'])
def export_settings():
    """Export current settings"""
    if not led_controller:
        return jsonify({"error": "LED controller not initialized"}), 500
    
    settings = {
        "led_count": LED_COUNT,
        "led_pin": LED_PIN,
        "status": led_controller.get_status(),
        "scheduled_patterns": scheduled_patterns,
        "exported_at": datetime.now().isoformat()
    }
    
    return jsonify(settings)


@app.route('/api/import', methods=['POST'])
def import_settings():
    """Import settings from JSON"""
    try:
        data = request.get_json()
        
        # Apply settings
        if 'status' in data:
            status = data['status']
            
            if 'brightness' in status:
                led_controller.set_brightness(status['brightness'])
            
            if 'animation_speed' in status:
                led_controller.set_animation_speed(status['animation_speed'])
            
            if 'current_pattern' in status:
                led_controller.set_pattern(PatternType(status['current_pattern']))
        
        if 'scheduled_patterns' in data:
            global scheduled_patterns
            scheduled_patterns = data['scheduled_patterns']
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


def cleanup():
    """Cleanup resources on shutdown"""
    global led_controller, audio_stream
    
    if led_controller:
        led_controller.cleanup()
    
    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()


if __name__ == '__main__':
    # Initialize LED controller
    if not init_led_controller():
        print("Warning: LED controller initialization failed. Running in demo mode.")
    
    # Start scheduler
    start_scheduler()
    
    try:
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cleanup()
