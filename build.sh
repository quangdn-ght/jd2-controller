#!/bin/bash
# Build script to package JDownloader Controller for deployment
# Creates a clean distribution package with only essential files

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="jd2-controller"
VERSION=$(date +%Y%m%d_%H%M%S)
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$BUILD_DIR/dist"
PACKAGE_NAME="${PROJECT_NAME}_${VERSION}"
PACKAGE_DIR="$DIST_DIR/$PACKAGE_NAME"

echo "🔨 Building $PROJECT_NAME v$VERSION"
echo "=================================="

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf "$DIST_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy essential Python files
echo "📦 Copying application files..."
cp "$SCRIPT_DIR/main.py" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$PACKAGE_DIR/"

# Copy src directory (excluding __pycache__)
echo "📦 Copying source code..."
rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='*.pyo' \
    "$SCRIPT_DIR/src/" "$PACKAGE_DIR/src/"

# Copy CLI tool
if [ -f "$SCRIPT_DIR/jdctl" ]; then
    echo "📦 Copying CLI tool..."
    cp "$SCRIPT_DIR/jdctl" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/jdctl"
fi

# Copy service files
echo "📦 Copying service files..."
if [ -f "$SCRIPT_DIR/jd-controller-api.service" ]; then
    cp "$SCRIPT_DIR/jd-controller-api.service" "$PACKAGE_DIR/"
fi
if [ -f "$SCRIPT_DIR/jdownloader.service" ]; then
    cp "$SCRIPT_DIR/jdownloader.service" "$PACKAGE_DIR/"
fi

# Copy essential scripts
echo "📦 Copying deployment scripts..."
mkdir -p "$PACKAGE_DIR/scripts"
cp "$SCRIPT_DIR/scripts/setup_venv.sh" "$PACKAGE_DIR/scripts/" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/run.sh" "$PACKAGE_DIR/scripts/" 2>/dev/null || true

# Create deployment documentation
echo "📝 Creating deployment documentation..."
cat > "$PACKAGE_DIR/DEPLOYMENT.md" << 'EOF'
# JDownloader Controller - Deployment Guide

## Prerequisites
- Python 3.8 or higher
- systemd (for service installation)
- JDownloader2 installed

## Quick Deployment

### 1. Extract Package
```bash
tar -xzf jd2-controller_*.tar.gz
cd jd2-controller_*
```

### 2. Setup Virtual Environment
```bash
chmod +x scripts/setup_venv.sh
./scripts/setup_venv.sh
```

### 3. Configure Environment
Create a `.env` file with your credentials:
```bash
# JDownloader Cloud Credentials
JDOWNLOADER_EMAIL=your_email@example.com
JDOWNLOADER_PASSWORD=your_password
JDOWNLOADER_DEVICE_NAME=your_device_name

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Test Installation
```bash
./scripts/run.sh --help
```

### 5. Install as Systemd Service (Optional)

#### Install API Service
```bash
sudo cp jd-controller-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jd-controller-api
sudo systemctl start jd-controller-api
```

#### Install JDownloader Service
```bash
sudo cp jdownloader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jdownloader
sudo systemctl start jdownloader
```

### 6. Verify Service Status
```bash
sudo systemctl status jd-controller-api
sudo systemctl status jdownloader
```

## Directory Structure
```
.
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── jdctl                        # CLI tool
├── src/                         # Application source code
├── scripts/                     # Deployment scripts
│   ├── setup_venv.sh           # Virtual environment setup
│   └── run.sh                  # Run application
├── jd-controller-api.service   # Systemd service for API
├── jdownloader.service         # Systemd service for JDownloader
└── DEPLOYMENT.md               # This file
```

## Usage

### CLI Mode
```bash
./jdctl status
./jdctl start
./jdctl stop
```

### API Mode
```bash
./scripts/run.sh
# API will be available at http://localhost:8000
```

## Troubleshooting

### Check Logs
```bash
# For API service
sudo journalctl -u jd-controller-api -f

# For JDownloader service
sudo journalctl -u jdownloader -f
```

### Verify Python Environment
```bash
source venv/bin/activate
python --version
pip list
```

### Permission Issues
Ensure scripts are executable:
```bash
chmod +x jdctl
chmod +x scripts/*.sh
```

## Support
For issues and questions, refer to the project documentation.
EOF

# Create installation script
echo "📝 Creating installation script..."
cat > "$PACKAGE_DIR/install.sh" << 'EOF'
#!/bin/bash
# Installation script for JDownloader Controller

set -e

echo "🚀 Installing JDownloader Controller..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Setup virtual environment
echo "📦 Setting up virtual environment..."
chmod +x scripts/setup_venv.sh
./scripts/setup_venv.sh

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x jdctl 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Create .env file with your JDownloader credentials"
echo "2. Run: ./scripts/run.sh --help"
echo "3. See DEPLOYMENT.md for detailed instructions"
echo ""
EOF

chmod +x "$PACKAGE_DIR/install.sh"

# Create .env template
echo "📝 Creating environment template..."
cat > "$PACKAGE_DIR/.env.example" << 'EOF'
# JDownloader Cloud Credentials
JDOWNLOADER_EMAIL=your_email@example.com
JDOWNLOADER_PASSWORD=your_password
JDOWNLOADER_DEVICE_NAME=your_device_name

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Logging Level
LOG_LEVEL=INFO
EOF

# Create README
echo "📝 Creating README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# JDownloader Controller

A Python-based controller for managing JDownloader2 via cloud API.

## Quick Start

1. Run installation script:
   ```bash
   ./install.sh
   ```

2. Configure credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Start the application:
   ```bash
   ./scripts/run.sh
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
EOF

# Create tarball
echo "📦 Creating distribution package..."
cd "$DIST_DIR"
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# Calculate package size
PACKAGE_SIZE=$(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)

# Generate checksum
echo "🔒 Generating checksum..."
sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.tar.gz.sha256"

# Clean up extracted directory (optional)
rm -rf "$PACKAGE_NAME"

echo ""
echo "✅ Build complete!"
echo "=================================="
echo "📦 Package: $DIST_DIR/${PACKAGE_NAME}.tar.gz"
echo "📊 Size: $PACKAGE_SIZE"
echo "🔒 Checksum: $DIST_DIR/${PACKAGE_NAME}.tar.gz.sha256"
echo ""
echo "To deploy:"
echo "1. Copy ${PACKAGE_NAME}.tar.gz to target host"
echo "2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "3. Run: cd ${PACKAGE_NAME} && ./install.sh"
echo ""

# Show checksum
echo "SHA256 Checksum:"
cat "${PACKAGE_NAME}.tar.gz.sha256"
echo ""
