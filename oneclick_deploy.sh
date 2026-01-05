#!/bin/bash
# One-Click Deploy Script for JDownloader Controller
# Builds, transfers, and installs the application on remote host

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build/dist"
REMOTE_HOST=""
REMOTE_PATH="/opt/jd2-controller"
DEPLOY_NAME="jd2-controller"

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --remote=*|remote=*)
            REMOTE_HOST="${arg#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --remote=<host>"
            echo ""
            echo "Arguments:"
            echo "  --remote=<host>  Remote host to deploy to (hostname or IP)"
            echo "  remote=<host>    Alternative format for remote host"
            echo ""
            echo "Examples:"
            echo "  $0 --remote=fshare"
            echo "  $0 remote=10.168.1.104"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if remote host is provided
if [ -z "$REMOTE_HOST" ]; then
    echo -e "\033[0;31m✗ Error: Remote host is required\033[0m"
    echo ""
    echo "Usage: $0 --remote=<host>"
    echo ""
    echo "Examples:"
    echo "  $0 --remote=fshare"
    echo "  $0 remote=10.168.1.104"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  JDownloader Controller - One-Click Deploy ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Build the package
echo -e "${GREEN}[1/3]${NC} Building package..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$SCRIPT_DIR"
./build.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi

# Find the latest tar.gz file
echo ""
echo -e "${GREEN}[2/3]${NC} Transferring to ${YELLOW}${REMOTE_HOST}${NC}..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LATEST_PACKAGE=$(ls -t "$BUILD_DIR"/*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_PACKAGE" ]; then
    echo -e "${RED}✗ No package found in $BUILD_DIR${NC}"
    exit 1
fi

PACKAGE_NAME=$(basename "$LATEST_PACKAGE")
PACKAGE_DIR="${PACKAGE_NAME%.tar.gz}"

echo -e "📦 Package: ${BLUE}$PACKAGE_NAME${NC}"
echo -e "🎯 Target: ${YELLOW}${REMOTE_HOST}:${REMOTE_PATH}${NC}"
echo ""

# Test SSH connection
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "$REMOTE_HOST" "echo 'SSH OK'" &>/dev/null; then
    echo -e "${RED}✗ Cannot connect to $REMOTE_HOST${NC}"
    echo "  Please ensure:"
    echo "  - SSH is configured"
    echo "  - Host '$REMOTE_HOST' is defined in ~/.ssh/config"
    echo "  - Passwordless authentication is set up"
    exit 1
fi
echo -e "${GREEN}✓${NC} SSH connection successful"
echo ""

# Transfer package
echo "Transferring package..."
scp "$LATEST_PACKAGE" "${REMOTE_HOST}:~/"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Transfer failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Package transferred successfully"

# Step 3: Extract and install on remote host
echo ""
echo -e "${GREEN}[3/4]${NC} Installing on ${YELLOW}${REMOTE_HOST}${NC}..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ssh "$REMOTE_HOST" bash << EOF
    set -e
    
    echo "📂 Creating installation directory..."
    sudo mkdir -p $REMOTE_PATH
    sudo chown \$USER:\$USER $REMOTE_PATH
    
    echo "📦 Extracting package..."
    cd ~
    tar -xzf $PACKAGE_NAME
    
    # Move extracted content to installation directory
    echo "📁 Moving to installation directory..."
    if [ -d "$REMOTE_PATH/$PACKAGE_DIR" ]; then
        echo "🔄 Removing old version..."
        rm -rf $REMOTE_PATH/$PACKAGE_DIR
    fi
    mv $PACKAGE_DIR $REMOTE_PATH/
    
    # Remove old current symlink and create new one
    if [ -L "$REMOTE_PATH/current" ] || [ -d "$REMOTE_PATH/current" ]; then
        rm -rf $REMOTE_PATH/current
    fi
    ln -sf $REMOTE_PATH/$PACKAGE_DIR $REMOTE_PATH/current
    
    # Clean up tar file
    rm -f $PACKAGE_NAME
    
    echo "🔧 Running installation..."
    cd $REMOTE_PATH/current
    chmod +x install.sh
    ./install.sh
    
    echo ""
    echo "═══════════════════════════════════════════"
    echo "📋 Installation complete!"
    echo "═══════════════════════════════════════════"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Installation failed!${NC}"
    exit 1
fi

# Step 4: Copy .env if exists and install services
echo ""
echo -e "${GREEN}[4/4]${NC} Configuring and starting services..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Copy .env file if exists locally
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "📝 Copying .env configuration..."
    scp "$SCRIPT_DIR/.env" "${REMOTE_HOST}:${REMOTE_PATH}/current/.env"
    echo -e "${GREEN}✓${NC} Configuration copied"
else
    echo -e "${YELLOW}⚠${NC}  No .env file found locally, skipping..."
fi

# Install and start services
echo ""
echo "🔧 Installing systemd services..."
ssh "$REMOTE_HOST" bash << 'EOF'
    set -e
    cd /opt/jd2-controller/current
    
    # Update service file paths to use /opt/jd2-controller/current
    if [ -f "jd-controller-api.service" ]; then
        sudo cp jd-controller-api.service /etc/systemd/system/
        echo "✓ Installed jd-controller-api.service"
    fi
    
    if [ -f "jdownloader.service" ]; then
        sudo cp jdownloader.service /etc/systemd/system/
        echo "✓ Installed jdownloader.service"
    fi
    
    # Reload systemd
    echo "🔄 Reloading systemd..."
    sudo systemctl daemon-reload
    
    # Enable and start services
    echo "🚀 Starting services..."
    
    if systemctl list-unit-files | grep -q jdownloader.service; then
        sudo systemctl enable jdownloader.service
        sudo systemctl restart jdownloader.service
        echo "✓ JDownloader service started"
    fi
    
    if systemctl list-unit-files | grep -q jd-controller-api.service; then
        sudo systemctl enable jd-controller-api.service
        sudo systemctl restart jd-controller-api.service
        echo "✓ JD Controller API service started"
    fi
    
    echo ""
    echo "📊 Service Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    systemctl status jdownloader.service --no-pager -l || true
    echo ""
    systemctl status jd-controller-api.service --no-pager -l || true
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Installation failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✓ Deployment Successful!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "🎯 Target host: ${YELLOW}${REMOTE_HOST}${NC}"
echo -e "📍 Install path: ${BLUE}${REMOTE_PATH}/current${NC}"
echo -e "📦 Version: ${BLUE}${PACKAGE_DIR}${NC}"
echo ""
echo "Services installed and started:"
echo "  ✓ jdownloader.service"
echo "  ✓ jd-controller-api.service"
echo ""
echo "Check service status:"
echo -e "  ${BLUE}ssh ${REMOTE_HOST} 'sudo systemctl status jd-controller-api'${NC}"
echo ""
echo "View logs:"
echo -e "  ${BLUE}ssh ${REMOTE_HOST} 'sudo journalctl -u jd-controller-api -f'${NC}"
echo ""
echo "Access API:"
echo -e "  ${BLUE}http://${REMOTE_HOST}:8001${NC}"
echo ""
