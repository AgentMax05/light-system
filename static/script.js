// LED Strip Controller JavaScript
class LEDController {
    constructor() {
        this.apiBase = '/api';
        this.statusInterval = null;
        this.currentStatus = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startStatusUpdates();
        this.loadScheduledPatterns();
    }

    setupEventListeners() {
        // Pattern buttons
        document.querySelectorAll('.pattern-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const pattern = e.currentTarget.dataset.pattern;
                this.setPattern(pattern);
            });
        });

        // Color controls
        const primaryColor = document.getElementById('primaryColor');
        const primaryColorHex = document.getElementById('primaryColorHex');
        const secondaryColor = document.getElementById('secondaryColor');
        const secondaryColorHex = document.getElementById('secondaryColorHex');

        primaryColor.addEventListener('change', (e) => {
            primaryColorHex.value = e.target.value;
            this.setColor('primary', e.target.value);
        });

        primaryColorHex.addEventListener('change', (e) => {
            if (this.isValidHex(e.target.value)) {
                primaryColor.value = e.target.value;
                this.setColor('primary', e.target.value);
            }
        });

        secondaryColor.addEventListener('change', (e) => {
            secondaryColorHex.value = e.target.value;
            this.setColor('secondary', e.target.value);
        });

        secondaryColorHex.addEventListener('change', (e) => {
            if (this.isValidHex(e.target.value)) {
                secondaryColor.value = e.target.value;
                this.setColor('secondary', e.target.value);
            }
        });

        // Brightness control
        const brightnessSlider = document.getElementById('brightnessSlider');
        const brightnessValue = document.getElementById('brightnessValue');

        brightnessSlider.addEventListener('input', (e) => {
            brightnessValue.textContent = e.target.value;
            this.setBrightness(parseInt(e.target.value));
        });

        // Speed control
        const speedSlider = document.getElementById('speedSlider');
        const speedValue = document.getElementById('speedValue');

        speedSlider.addEventListener('input', (e) => {
            speedValue.textContent = e.target.value + 'x';
            this.setSpeed(parseFloat(e.target.value));
        });

        // Control buttons
        document.getElementById('startBtn').addEventListener('click', () => this.startAnimation());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopAnimation());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearLEDs());

        // Audio controls
        document.getElementById('startAudioBtn').addEventListener('click', () => this.startAudio());
        document.getElementById('stopAudioBtn').addEventListener('click', () => this.stopAudio());

        // Schedule controls
        document.getElementById('addScheduleBtn').addEventListener('click', () => this.addSchedule());

        // Settings controls
        document.getElementById('exportBtn').addEventListener('click', () => this.exportSettings());
        document.getElementById('importBtn').addEventListener('click', () => document.getElementById('importFile').click());
        document.getElementById('importFile').addEventListener('change', (e) => this.importSettings(e.target.files[0]));
    }

    async makeRequest(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.apiBase}${endpoint}`, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Request failed');
            }

            return result;
        } catch (error) {
            console.error('API request failed:', error);
            this.showToast('Error: ' + error.message, 'error');
            throw error;
        }
    }

    async setPattern(pattern) {
        try {
            await this.makeRequest('/pattern', 'POST', { pattern });
            this.updatePatternButtons(pattern);
            this.showToast(`Pattern set to ${pattern}`, 'success');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async setColor(type, color) {
        try {
            const data = {};
            data[type] = { hex: color };
            await this.makeRequest('/color', 'POST', data);
            this.showToast(`${type} color updated`, 'success');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async setBrightness(brightness) {
        try {
            await this.makeRequest('/brightness', 'POST', { brightness });
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async setSpeed(speed) {
        try {
            await this.makeRequest('/speed', 'POST', { speed });
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async startAnimation() {
        try {
            await this.makeRequest('/start', 'POST');
            this.showToast('Animation started', 'success');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async stopAnimation() {
        try {
            await this.makeRequest('/stop', 'POST');
            this.showToast('Animation stopped', 'info');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async clearLEDs() {
        try {
            await this.makeRequest('/clear', 'POST');
            this.showToast('LEDs cleared', 'info');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async startAudio() {
        try {
            await this.makeRequest('/audio/start', 'POST');
            this.showToast('Audio capture started', 'success');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async stopAudio() {
        try {
            await this.makeRequest('/audio/stop', 'POST');
            this.showToast('Audio capture stopped', 'info');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async addSchedule() {
        const pattern = document.getElementById('schedulePattern').value;
        const time = document.getElementById('scheduleTime').value;
        const duration = document.getElementById('scheduleDuration').value;

        if (!time) {
            this.showToast('Please select a time', 'warning');
            return;
        }

        try {
            await this.makeRequest('/schedule', 'POST', {
                pattern,
                time,
                duration: parseInt(duration)
            });
            this.showToast('Schedule added', 'success');
            this.loadScheduledPatterns();
            document.getElementById('scheduleTime').value = '';
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async loadScheduledPatterns() {
        try {
            const result = await this.makeRequest('/schedule');
            this.displayScheduledPatterns(result.scheduled_patterns);
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    displayScheduledPatterns(patterns) {
        const container = document.getElementById('scheduledList');
        container.innerHTML = '';

        patterns.forEach((pattern, index) => {
            const item = document.createElement('div');
            item.className = 'scheduled-item';
            item.innerHTML = `
                <div class="scheduled-item-info">
                    <div class="pattern">${pattern.pattern}</div>
                    <div class="time">${pattern.time} (${pattern.duration} min)</div>
                </div>
                <div class="scheduled-item-actions">
                    <button class="btn btn-danger" onclick="ledController.deleteSchedule(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(item);
        });
    }

    async deleteSchedule(index) {
        try {
            await this.makeRequest(`/schedule/${index}`, 'DELETE');
            this.showToast('Schedule deleted', 'info');
            this.loadScheduledPatterns();
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async exportSettings() {
        try {
            const result = await this.makeRequest('/export');
            const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `led-settings-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            this.showToast('Settings exported', 'success');
        } catch (error) {
            // Error already shown in makeRequest
        }
    }

    async importSettings(file) {
        if (!file) return;

        try {
            const text = await file.text();
            const settings = JSON.parse(text);
            await this.makeRequest('/import', 'POST', settings);
            this.showToast('Settings imported', 'success');
            this.updateUI();
        } catch (error) {
            this.showToast('Failed to import settings', 'error');
        }
    }

    async updateStatus() {
        try {
            const status = await this.makeRequest('/status');
            this.currentStatus = status;
            this.updateUI(status);
            this.updateConnectionStatus(true);
        } catch (error) {
            this.updateConnectionStatus(false);
        }
    }

    updateUI(status = this.currentStatus) {
        if (!status) return;

        // Update pattern buttons
        this.updatePatternButtons(status.current_pattern);

        // Update colors
        if (status.primary_color) {
            document.getElementById('primaryColor').value = status.primary_color.hex;
            document.getElementById('primaryColorHex').value = status.primary_color.hex;
        }

        if (status.secondary_color) {
            document.getElementById('secondaryColor').value = status.secondary_color.hex;
            document.getElementById('secondaryColorHex').value = status.secondary_color.hex;
        }

        // Update brightness
        document.getElementById('brightnessSlider').value = status.brightness;
        document.getElementById('brightnessValue').textContent = status.brightness;

        // Update speed
        document.getElementById('speedSlider').value = status.animation_speed;
        document.getElementById('speedValue').textContent = status.animation_speed + 'x';
    }

    updatePatternButtons(activePattern) {
        document.querySelectorAll('.pattern-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.pattern === activePattern) {
                btn.classList.add('active');
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('statusText');

        if (connected) {
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'Disconnected';
        }
    }

    startStatusUpdates() {
        this.updateStatus();
        this.statusInterval = setInterval(() => this.updateStatus(), 2000);
    }

    stopStatusUpdates() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }

    isValidHex(hex) {
        return /^#[0-9A-F]{6}$/i.test(hex);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize the LED controller when the page loads
let ledController;
document.addEventListener('DOMContentLoaded', () => {
    ledController = new LEDController();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (ledController) {
        ledController.stopStatusUpdates();
    }
});
