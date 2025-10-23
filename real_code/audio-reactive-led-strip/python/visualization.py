from __future__ import print_function
from __future__ import division
import time
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import config
import microphone
import dsp
import led

_time_prev = time.time() * 1000.0
"""The previous time that the frames_per_second() function was called"""

_fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
"""The low-pass filter used to estimate frames-per-second"""


def frames_per_second():
    """Return the estimated frames per second

    Returns the current estimate for frames-per-second (FPS).
    FPS is estimated by measured the amount of time that has elapsed since
    this function was previously called. The FPS estimate is low-pass filtered
    to reduce noise.

    This function is intended to be called one time for every iteration of
    the program's main loop.

    Returns
    -------
    fps : float
        Estimated frames-per-second. This value is low-pass filtered
        to reduce noise.
    """
    global _time_prev, _fps
    time_now = time.time() * 1000.0
    dt = time_now - _time_prev
    _time_prev = time_now
    if dt == 0.0:
        return _fps.value
    return _fps.update(1000.0 / dt)


def memoize(function):
    """Provides a decorator for memoizing functions"""
    from functools import wraps
    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


@memoize
def _normalized_linspace(size):
    return np.linspace(0, 1, size)


def interpolate(y, new_length):
    """Intelligently resizes the array by linearly interpolating the values

    Parameters
    ----------
    y : np.array
        Array that should be resized

    new_length : int
        The length of the new interpolated array

    Returns
    -------
    z : np.array
        New array with length of new_length that contains the interpolated
        values of y.
    """
    if len(y) == new_length:
        return y
    x_old = _normalized_linspace(len(y))
    x_new = _normalized_linspace(new_length)
    z = np.interp(x_new, x_old, y)
    return z

# ORIGINAL FILTERS:
# r_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
#                        alpha_decay=0.2, alpha_rise=0.99)
# g_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
#                        alpha_decay=0.05, alpha_rise=0.3)
# b_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
#                        alpha_decay=0.1, alpha_rise=0.5)
# common_mode = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
#                        alpha_decay=0.99, alpha_rise=0.01)
p_filt = dsp.ExpFilter(np.tile(1, (3, config.N_PIXELS // 2)),
                       alpha_decay=0.1, alpha_rise=0.99)
p = np.tile(1.0, (3, config.N_PIXELS // 2))
# gain = dsp.ExpFilter(np.tile(0.01, config.N_FFT_BINS),
#                      alpha_decay=0.001, alpha_rise=0.99)

# Make normalization fall faster so levels recover after loud parts
gain = dsp.ExpFilter(np.tile(0.01, config.N_FFT_BINS),
                     alpha_decay=0.05,  # was 0.001
                     alpha_rise=0.95)   # was 0.99

# Common-mode (baseline) that adapts reasonably in both directions
common_mode = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                            alpha_decay=0.9,   # slower fall than 0.99
                            alpha_rise=0.2)    # faster rise than 0.01

# Red: emphasize energy above baseline, but let it decay faster so it’s visible
r_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                       alpha_decay=0.1,  # was 0.2
                       alpha_rise=0.8)   # was 0.99

# Green: actually filter it (you computed g_filt but didn’t use it); also boost it
g_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                       alpha_decay=0.2,  # more stable than 0.05
                       alpha_rise=0.6)   # more responsive than 0.3

# Blue: reduce persistence so it doesn’t wash out others
b_filt = dsp.ExpFilter(np.tile(0.01, config.N_PIXELS // 2),
                       alpha_decay=0.08,  # was 0.1
                       alpha_rise=0.35)   # was 0.5


def visualize_scroll(y):
    """Effect that originates in the center and scrolls outwards"""
    global p
    y = y**2.0
    gain.update(y)
    y /= gain.value
    y *= 255.0
    r = int(np.max(y[:len(y) // 3]))
    g = int(np.max(y[len(y) // 3: 2 * len(y) // 3]))
    b = int(np.max(y[2 * len(y) // 3:]))
    # Scrolling effect window
    p[:, 1:] = p[:, :-1]
    p *= 0.98
    p = gaussian_filter1d(p, sigma=0.2)
    # Create new color originating at the center
    p[0, 0] = r
    p[1, 0] = g
    p[2, 0] = b
    # Update the LED strip
    return np.concatenate((p[:, ::-1], p), axis=1)


def visualize_energy(y):
    """Effect that expands from the center with increasing sound energy"""
    global p
    y = np.copy(y)
    gain.update(y)
    y /= gain.value
    # Scale by the width of the LED strip
    y *= float((config.N_PIXELS // 2) - 1)
    # Map color channels according to energy in the different freq bands
    scale = 0.9
    r = int(np.mean(y[:len(y) // 3]**scale))
    g = int(np.mean(y[len(y) // 3: 2 * len(y) // 3]**scale))
    b = int(np.mean(y[2 * len(y) // 3:]**scale))
    # Assign color to different frequency regions
    p[0, :r] = 255.0
    p[0, r:] = 0.0
    p[1, :g] = 255.0
    p[1, g:] = 0.0
    p[2, :b] = 255.0
    p[2, b:] = 0.0
    p_filt.update(p)
    p = np.round(p_filt.value)
    # Apply substantial blur to smooth the edges
    p[0, :] = gaussian_filter1d(p[0, :], sigma=4.0)
    p[1, :] = gaussian_filter1d(p[1, :], sigma=4.0)
    p[2, :] = gaussian_filter1d(p[2, :], sigma=4.0)
    # Set the new pixel value
    return np.concatenate((p[:, ::-1], p), axis=1)


_prev_spectrum = np.tile(0.01, config.N_PIXELS // 2)

prev_scroll = 0
def visualize_spectrum(y):
    """Effect that maps the Mel filterbank frequencies onto the LED strip"""
    global _prev_spectrum, prev_scroll
    y = np.copy(interpolate(y, config.N_PIXELS // 2))
    common_mode.update(y)
    diff = y - _prev_spectrum
    _prev_spectrum = np.copy(y)
    # Color channel mappings
    r = r_filt.update(y - common_mode.value)
    g = g_filt.update(np.abs(diff))
    # b = b_filt.update(np.copy(y) - common_mode.value)
    
    
    # Reduce blue by scaling it down and applying the common mode subtraction
    b = b_filt.update(np.copy(y) - common_mode.value * 0.5)
    
    # Boost red and green to balance with blue
    r = r * 1.5
    g = g * 1.3


    # Mirror the color channels for symmetric output
    r = np.concatenate((r[::-1], r))
    g = np.concatenate((g[::-1], g))
    b = np.concatenate((b[::-1], b))
    output = np.array([r, g,b]) * 255
    prev_scroll = (prev_scroll + 1) % config.N_PIXELS

    return np.roll(output, axis=1, shift=prev_scroll)


fft_plot_filter = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                         alpha_decay=0.5, alpha_rise=0.99)
# mel_gain = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
#                          alpha_decay=0.01, alpha_rise=0.99)
mel_gain = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                         alpha_decay=0.2, alpha_rise=0.99)
mel_smoothing = dsp.ExpFilter(np.tile(1e-1, config.N_FFT_BINS),
                         alpha_decay=0.5, alpha_rise=0.99)
volume = dsp.ExpFilter(config.MIN_VOLUME_THRESHOLD,
                       alpha_decay=0.02, alpha_rise=0.02)
fft_window = np.hamming(int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY)
prev_fps_update = time.time()


def microphone_update(audio_samples):
    global y_roll, prev_rms, prev_exp, prev_fps_update
    # Normalize samples between 0 and 1
    y = audio_samples / 2.0**15
    # Construct a rolling window of audio samples
    y_roll[:-1] = y_roll[1:]
    y_roll[-1, :] = np.copy(y)
    y_data = np.concatenate(y_roll, axis=0).astype(np.float32)
    
    vol = np.max(np.abs(y_data))
    if vol < config.MIN_VOLUME_THRESHOLD:
        print('No audio input. Volume below threshold. Volume:', vol)
        led.pixels = np.tile(0, (3, config.N_PIXELS))
        led.update()
    else:
        # Transform audio input into the frequency domain
        N = len(y_data)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N
        # Pad with zeros until the next power of two
        y_data *= fft_window
        y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        YS = np.abs(np.fft.rfft(y_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * dsp.mel_y.T
        # Scale data to values more suitable for visualization
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= mel_gain.value
        mel = mel_smoothing.update(mel)
        # Map filterbank output onto LED strip
        output = visualization_effect(mel)
        led.pixels = output
        led.update()
        if config.USE_GUI:
            # Plot filterbank output
            x = np.linspace(config.MIN_FREQUENCY, config.MAX_FREQUENCY, len(mel))
            mel_curve.setData(x=x, y=fft_plot_filter.update(mel))
            # Plot the color channels
            r_curve.setData(y=led.pixels[0])
            g_curve.setData(y=led.pixels[1])
            b_curve.setData(y=led.pixels[2])
    if config.USE_GUI:
        app.processEvents()
    
    if config.DISPLAY_FPS:
        fps = frames_per_second()
        if time.time() - 0.5 > prev_fps_update:
            prev_fps_update = time.time()
            print('FPS {:.0f} / {:.0f}'.format(fps, config.FPS))


# Number of audio samples to read every time frame
samples_per_frame = int(config.MIC_RATE / config.FPS)

# Array containing the rolling audio sample window
y_roll = np.random.rand(config.N_ROLLING_HISTORY, samples_per_frame) / 1e16

"""Visualization effect to display on the LED strip"""

# --- New Wave Pulse Visualizer ---
def visualize_wavepulse(y):
    """
    Creates a symmetric, colorful wave pulse effect that radiates from the center
    and fades out, with color gradients based on frequency content.
    """
    global p
    # Normalize and scale input
    y = np.copy(y)
    gain.update(y)
    y /= gain.value
    y = np.clip(y, 0, 1)
    # Interpolate y to match half the LED count
    half_leds = config.N_PIXELS // 2
    y_interp = interpolate(y, half_leds)
    gradient = np.linspace(0, 1, half_leds)
    r = (y_interp * (1 - gradient)) * 255
    g = (y_interp * gradient) * 255
    b = (np.abs(np.sin(gradient * np.pi + np.sum(y_interp))) * y_interp) * 255
    # Pulse effect: fade previous frame, add new pulse to left half
    p *= 0.85  # Fade tails
    half_leds = config.N_PIXELS // 2
    p[0, :half_leds] += r
    p[1, :half_leds] += g
    p[2, :half_leds] += b
    # Smooth with Gaussian blur
    p[0, :] = gaussian_filter1d(p[0, :], sigma=2.0)
    p[1, :] = gaussian_filter1d(p[1, :], sigma=2.0)
    p[2, :] = gaussian_filter1d(p[2, :], sigma=2.0)
    # Mirror for symmetry
    output = np.concatenate((p[:, ::-1], p), axis=1)
    output = np.clip(output, 0, 255)
    return output

from collections import deque
_bass_env_filt = dsp.ExpFilter(np.array([0.1]), alpha_decay=0.2, alpha_rise=0.9)
_level_filt   = dsp.ExpFilter(np.array([0.5]), alpha_decay=0.2, alpha_rise=0.8)
_peak_hist    = deque(maxlen=30)  # ~0.5s at 60 FPS; for robust gain

def visualize_party(y):
    """
    LED visualizer tuned for party/rap:
      - Strong bass/kick-driven red
      - Snappy transients in green
      - Stable body/air in blue
      - Robust gain (percentile) to avoid post-loudness dimming
      - Mirror + slight scroll for motion
    """
    global _prev_spectrum, prev_scroll, _peak_hist

    # --- Resize y to half-strip (we'll mirror later) ---
    half = config.N_PIXELS // 2
    y = np.copy(interpolate(y, half))
    y = np.maximum(y, 0)  # no negatives

    # --- Robust level estimate (prevents "dim after loud" hangover) ---
    # Use rolling 95th percentile as a divisor, smoothed.
    _peak_hist.append(float(np.max(y)))
    level_est = np.percentile(_peak_hist, 95) if _peak_hist else np.max(y)
    lvl = float(_level_filt.update(np.array([level_est]))[0])
    denom = np.clip(lvl, 0.15, 3.0)
    y = y / denom

    # --- Common-mode subtraction (above-baseline emphasis) ---
    common_mode.update(y)
    y_above = np.clip(y - 0.7 * common_mode.value, 0, None)  # 0.7 keeps it lively

    # --- Frame-to-frame change for transients ---
    if _prev_spectrum is None or len(_prev_spectrum) != len(y):
        _prev_spectrum = np.copy(y)
    diff = y - _prev_spectrum
    _prev_spectrum = np.copy(y)
    transients = np.abs(diff) * 0

    # --- Band selections (indices over half-strip) ---
    n = len(y)
    bass_hi = max(2, int(0.18 * n))        # ~lowest 18% → kick/bass
    hat_lo  = int(0.65 * n)                # ~top 35% → hats/air

    bass_band = y_above[:bass_hi]
    hats_band = y[hat_lo:]

    # Beat pulse from bass envelope (kick accent)
    bass_level = float(bass_band.mean()) if bass_band.size else 0.0
    env = float(_bass_env_filt.update(np.array([bass_level]))[0])
    beat_pulse = np.clip((bass_level - env) * 4.0, 0.0, 1.0)  # scale = sensitivity
    pulse_gain = 1.0 + 1.2 * beat_pulse                        # global brightness pop

    # --- Color channels ---
    # Red: above-baseline energy (bass forward) + tiny transient mix
    r_raw = 1.6 * y_above + 0.2 * transients
    r = r_filt.update(r_raw)

    # Green: transients (hats/ticks/claps) with a little extra boost
    g_raw = 2.2 * transients
    g = g_filt.update(g_raw)

    # Blue: stable body/air; lightly smooth and downweight mids to favor top
    smooth_y = 0.7 * y + 0.3 * np.roll(y, 1)
    # add a small emphasis to hats region
    if hats_band.size:
        smooth_y[hat_lo:] *= 1.2
    b = b_filt.update(smooth_y)

    # --- Channel balancing & gamma ---
    r *= 1.25
    g *= 1.40
    b *= 0.85

    # global pulse from kick
    rgb = np.vstack([r, g, b]) * pulse_gain

    # clip and optional gamma for pleasing roll-off
    rgb = np.clip(rgb, 0, 1)
    gamma = 2.0
    rgb = rgb ** (1.0 / gamma)

    # --- Mirror for symmetry and gentle scroll ---
    r_m = np.concatenate((rgb[0, ::-1], rgb[0]))
    g_m = np.concatenate((rgb[1, ::-1], rgb[1]))
    b_m = np.concatenate((rgb[2, ::-1], rgb[2]))

    prev_scroll = (prev_scroll + 1) % config.N_PIXELS  # 1 px/frame; tune for speed
    output = np.array([r_m, g_m, b_m]) * 255.0
    return np.roll(output, shift=prev_scroll, axis=1)


# To use, set:
# visualization_effect = visualize_wavepulse
"""Visualization effect to display on the LED strip"""

visualization_effect = visualize_party
# visualization_effect = visualize_wavepulse
# visualization_effect = visualize_spectrum
# visualization_effect = visualize_scroll
# visualization_effect = visualize_energy


if __name__ == '__main__':
    if config.USE_GUI:
        import pyqtgraph as pg
        from pyqtgraph.Qt import QtGui, QtCore
        # Create GUI window
        app = QtGui.QApplication([])
        view = pg.GraphicsView()
        layout = pg.GraphicsLayout(border=(100,100,100))
        view.setCentralItem(layout)
        view.show()
        view.setWindowTitle('Visualization')
        view.resize(800,600)
        # Mel filterbank plot
        fft_plot = layout.addPlot(title='Filterbank Output', colspan=3)
        fft_plot.setRange(yRange=[-0.1, 1.2])
        fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        x_data = np.array(range(1, config.N_FFT_BINS + 1))
        mel_curve = pg.PlotCurveItem()
        mel_curve.setData(x=x_data, y=x_data*0)
        fft_plot.addItem(mel_curve)
        # Visualization plot
        layout.nextRow()
        led_plot = layout.addPlot(title='Visualization Output', colspan=3)
        led_plot.setRange(yRange=[-5, 260])
        led_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        # Pen for each of the color channel curves
        r_pen = pg.mkPen((255, 30, 30, 200), width=4)
        g_pen = pg.mkPen((30, 255, 30, 200), width=4)
        b_pen = pg.mkPen((30, 30, 255, 200), width=4)
        # Color channel curves
        r_curve = pg.PlotCurveItem(pen=r_pen)
        g_curve = pg.PlotCurveItem(pen=g_pen)
        b_curve = pg.PlotCurveItem(pen=b_pen)
        # Define x data
        x_data = np.array(range(1, config.N_PIXELS + 1))
        r_curve.setData(x=x_data, y=x_data*0)
        g_curve.setData(x=x_data, y=x_data*0)
        b_curve.setData(x=x_data, y=x_data*0)
        # Add curves to plot
        led_plot.addItem(r_curve)
        led_plot.addItem(g_curve)
        led_plot.addItem(b_curve)
        # Frequency range label
        freq_label = pg.LabelItem('')
        # Frequency slider
        def freq_slider_change(tick):
            minf = freq_slider.tickValue(0)**2.0 * (config.MIC_RATE / 2.0)
            maxf = freq_slider.tickValue(1)**2.0 * (config.MIC_RATE / 2.0)
            t = 'Frequency range: {:.0f} - {:.0f} Hz'.format(minf, maxf)
            freq_label.setText(t)
            config.MIN_FREQUENCY = minf
            config.MAX_FREQUENCY = maxf
            dsp.create_mel_bank()
        freq_slider = pg.TickSliderItem(orientation='bottom', allowAdd=False)
        freq_slider.tickMoveFinished = freq_slider_change
        freq_slider.addTick((config.MIN_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        freq_slider.addTick((config.MAX_FREQUENCY / (config.MIC_RATE / 2.0))**0.5)
        freq_label.setText('Frequency range: {} - {} Hz'.format(
            config.MIN_FREQUENCY,
            config.MAX_FREQUENCY))
        # Effect selection
        active_color = '#16dbeb'
        inactive_color = '#FFFFFF'
        def energy_click(x):
            global visualization_effect
            visualization_effect = visualize_energy
            energy_label.setText('Energy', color=active_color)
            scroll_label.setText('Scroll', color=inactive_color)
            spectrum_label.setText('Spectrum', color=inactive_color)
        def scroll_click(x):
            global visualization_effect
            visualization_effect = visualize_scroll
            energy_label.setText('Energy', color=inactive_color)
            scroll_label.setText('Scroll', color=active_color)
            spectrum_label.setText('Spectrum', color=inactive_color)
        def spectrum_click(x):
            global visualization_effect
            visualization_effect = visualize_spectrum
            energy_label.setText('Energy', color=inactive_color)
            scroll_label.setText('Scroll', color=inactive_color)
            spectrum_label.setText('Spectrum', color=active_color)
        # Create effect "buttons" (labels with click event)
        energy_label = pg.LabelItem('Energy')
        scroll_label = pg.LabelItem('Scroll')
        spectrum_label = pg.LabelItem('Spectrum')
        energy_label.mousePressEvent = energy_click
        scroll_label.mousePressEvent = scroll_click
        spectrum_label.mousePressEvent = spectrum_click
        energy_click(0)
        # Layout
        layout.nextRow()
        layout.addItem(freq_label, colspan=3)
        layout.nextRow()
        layout.addItem(freq_slider, colspan=3)
        layout.nextRow()
        layout.addItem(energy_label)
        layout.addItem(scroll_label)
        layout.addItem(spectrum_label)
    # Initialize LEDs
    led.update()
    # Start listening to live audio stream
    microphone.start_stream(microphone_update)
