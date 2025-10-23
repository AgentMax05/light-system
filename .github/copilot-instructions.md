## Purpose

Short, actionable guidance for AI coding agents working in this repo (LED strip controller).

1. Big picture
   - Flask web app (`app.py`) + single global `LEDController` (`led_controller.py`).
   - Audio capture/processing lives in `audio_processor.py` and integrates into the controller via callbacks or by passing audio buffers (`set_audio_data`).
   - Static UI in `templates/index.html` and `static/script.js` drives the REST API under `/api/*` endpoints.

2. Key files to touch
   - `app.py` — HTTP routes, scheduler, audio thread orchestration. Update this file when adding REST endpoints or changing scheduling behavior.
   - `led_controller.py` — pattern implementations are `_solid_pattern`, `_rainbow_pattern`, etc. Add patterns by adding a new `PatternType` enum value and an `_your_pattern(self, frame)` method, then wire it into `_animation_loop`.
   - `audio_processor.py` — FFT, frequency bins, and visualization creators; use `visualization_callback` to emit prepared LED arrays.
   - `static/script.js` — front-end client; when adding endpoints change this file to call them and update `templates/index.html` where needed.

3. Conventions and contracts
   - Patterns are represented by `PatternType` strings (e.g., "rainbow", "music"). Frontend posts `{ "pattern": "rainbow" }` to `/api/pattern`.
   - Color payloads accept either `{ "primary": { "hex": "#RRGGBB" } }` or `{ "primary": { "red":N, "green":N, "blue":N } }` and map to `ColorRGB`.
   - Brightness is an integer 0–255 (POST `/api/brightness` with `{ "brightness": 200 }`).
   - Animation speed is a float 0.1–10.0 (POST `/api/speed` with `{ "speed": 1.5 }`).
   - Scheduler uses 24-hour `HH:MM` strings (POST `/api/schedule` with `{ "pattern":"rainbow", "time":"23:30", "duration":60 }`).

4. Developer workflows (how to run & test)
   - Install deps: `python -m venv venv; venv\Scripts\Activate; pip install -r requirements.txt`.
   - Run app locally: `python app.py`. The web UI is served at `http://localhost:5000`.
   - Hardware libs: `rpi-ws281x` (LEDs) and `pyaudio` (audio). `led_controller.py` provides a soft mock if `rpi_ws281x` is missing; use that for non-RPi development.
   - Quick hardware test: `python test\simple_led_test.py` to verify wiring and basic patterns.

5. Integration and external dependencies
   - rpi-ws281x for WS2812/NeoPixel control; spidev is used in `test/sk9822_led_test.py` for SK9822 strips.
   - pyaudio + scipy/numpy for audio capture/FFT. Audio device must be available and may require system packages on Raspberry Pi.
   - No DB or persistent storage: scheduled patterns and settings are in-memory (process lifetime). Persist explicitly if needed.

6. Common change patterns and pitfalls
   - Adding a new pattern: add enum value to `PatternType`, implement `_new_pattern(self, frame)`, wire into `_animation_loop`, and add UI button + `/api/pattern` usage in `static/script.js`.
   - Keep backend and frontend pattern names in sync — they are matched by exact strings from `PatternType`.
   - Audio visualization: if you modify `AudioProcessor._create_visualization_data`, ensure `led_controller._music_pattern` or the frontend consumer still expects `led_data` normalized 0..1.
   - When running on non-Raspberry Pi machines, expect `rpi_ws281x` ImportError; leverage the mock in `led_controller.py` for unit-level work.

7. Useful examples (copy-paste)
   - Set pattern: POST /api/pattern -> JSON: { "pattern": "rainbow" }
   - Set primary color by hex: POST /api/color -> JSON: { "primary": { "hex": "#FF00AA" } }
   - Start audio capture: POST /api/audio/start

8. Where to look for tests and examples
   - `test/simple_led_test.py` — basic LED behavior and wiring examples.
   - `README.md` — higher-level setup and wiring guidance; use it for hardware notes.

If anything here looks incomplete or you want more detail on a specific area (e.g., adding CI, persisting schedules, or unit test examples), tell me which section to expand.
