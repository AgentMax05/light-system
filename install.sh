#!/bin/bash
# LED Strip Controller Installation Script
# For Raspberry Pi OS

set -e  # Exit on any error

echo "🎨 LED Strip Controller Installation Script"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-setuptools \
    portaudio19-dev \
    python3-pyaudio \
    libasound2-dev \
    git \
    build-essential \
    cmake

# Install rpi_ws281x system dependencies
echo "💡 Installing LED strip dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    scons \
    swig

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Install rpi_ws281x (if not already installed)
echo "🔌 Installing rpi_ws281x library..."
if ! python -c "import rpi_ws281x" 2>/dev/null; then
    echo "Installing rpi_ws281x from source..."
    git clone https://github.com/jgarff/rpi_ws281x.git
    cd rpi_ws281x
    scons
    cd python
    python setup.py build
    sudo python setup.py install
    cd ../..
    rm -rf rpi_ws281x
fi

# Create configuration file
echo "⚙️  Creating configuration file..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
    echo "   Please edit .env to configure your LED strip"
else
    echo "ℹ️  .env file already exists"
fi

# Set up systemd service (optional)
echo "🚀 Setting up systemd service..."
read -p "Create systemd service for auto-start? (y/N): " create_service
if [[ "$create_service" =~ ^[Yy]$ ]]; then
    sudo tee /etc/systemd/system/led-controller.service > /dev/null <<EOF
[Unit]
Description=LED Strip Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable led-controller.service
    echo "✅ Systemd service created and enabled"
    echo "   Start with: sudo systemctl start led-controller"
    echo "   Stop with: sudo systemctl stop led-controller"
    echo "   Status with: sudo systemctl status led-controller"
fi

# Set up audio permissions
echo "🎵 Setting up audio permissions..."
sudo usermod -a -G audio pi
sudo usermod -a -G gpio pi

# Enable GPIO (if not already enabled)
echo "🔌 Configuring GPIO..."
if ! grep -q "dtparam=gpio=18" /boot/config.txt; then
    echo "dtparam=gpio=18" | sudo tee -a /boot/config.txt
    echo "✅ GPIO 18 enabled in /boot/config.txt"
    echo "   Reboot required for GPIO changes to take effect"
fi

# Test installation
echo "🧪 Testing installation..."
if python -c "import rpi_ws281x, flask, numpy, pyaudio" 2>/dev/null; then
    echo "✅ All Python dependencies installed successfully"
else
    echo "❌ Some dependencies failed to install"
    echo "   Please check the error messages above"
fi

# Create startup script
echo "📝 Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
# LED Controller Startup Script

cd "$(dirname "$0")"
source venv/bin/activate
python app.py
EOF

chmod +x start.sh

# Final instructions
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "Next steps:"
echo "1. Edit .env file to configure your LED strip:"
echo "   nano .env"
echo ""
echo "2. Test the installation:"
echo "   ./start.sh"
echo ""
echo "3. Access the web interface:"
echo "   http://your-pi-ip:5000"
echo ""
echo "4. For production use:"
echo "   sudo systemctl start led-controller"
echo ""
echo "⚠️  Important Safety Notes:"
echo "   - Use external 5V power supply for LED strip"
echo "   - Do NOT connect LED +5V to Raspberry Pi"
echo "   - Use level shifter for strips longer than 30 LEDs"
echo ""
echo "📚 Documentation: README.md"
echo "🐛 Issues: Check troubleshooting section in README"
echo ""
echo "Happy LED controlling! 🎨✨"
