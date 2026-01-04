#!/bin/bash
# JDownloader Headless Startup with Cloud Verification
# This script starts JDownloader in headless mode and verifies cloud connection

set -e

# Configuration
JD_HOME="/opt/jd2"
JD_JAR="$JD_HOME/JDownloader.jar"
LOG_FILE="/tmp/jd2.log"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERIFY_SCRIPT="$SCRIPT_DIR/src/verification/verify_connection_v2.py"
PYTHON_VENV="$SCRIPT_DIR/venv/bin/python"
MAX_WAIT=30  # Maximum wait time for cloud connection in seconds

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_requirements() {
    print_status "Checking requirements..."
    
    if [ ! -f "$JD_JAR" ]; then
        print_error "JDownloader.jar not found at $JD_JAR"
        exit 1
    fi
    
    if ! command -v java &> /dev/null; then
        print_error "Java is not installed"
        exit 1
    fi
    
    if [ ! -f "$PYTHON_VENV" ]; then
        print_error "Python virtual environment not found at $PYTHON_VENV"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

stop_existing_instances() {
    print_status "Stopping any existing JDownloader instances..."
    
    if pgrep -f "JDownloader.jar" > /dev/null; then
        pkill -9 -f "JDownloader.jar" 2>/dev/null || true
        sleep 2
        print_success "Existing instances stopped"
    else
        print_status "No existing instances found"
    fi
}

start_jdownloader_headless() {
    print_status "Starting JDownloader in headless mode..."
    
    cd "$JD_HOME"
    
    # Start JDownloader with headless flags
    nohup java -Djava.awt.headless=true \
                    -jar "$JD_JAR" \
                    -norestart \
                    -noerr \
                    > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    print_status "JDownloader started with PID: $pid"
    
    # Wait for process to stabilize
    print_status "Waiting for JDownloader to initialize..."
    sleep 5
    
    # Verify process is still running
    if ! pgrep -f "JDownloader.jar" > /dev/null; then
        print_error "JDownloader failed to start. Check logs at $LOG_FILE"
        tail -20 "$LOG_FILE"
        exit 1
    fi
    
    local actual_pid=$(pgrep -f "JDownloader.jar" | head -1)
    print_success "JDownloader running (PID: $actual_pid)"
}

verify_cloud_connection() {
    print_status "Waiting for cloud connection to establish..."
    
    local elapsed=0
    local wait_interval=5
    local attempt=1
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        print_status "Verification attempt $attempt (${elapsed}s elapsed)..."
        
        if $PYTHON_VENV "$VERIFY_SCRIPT" > /tmp/jd_verify.log 2>&1; then
            print_success "Cloud connection verified!"
            cat /tmp/jd_verify.log | grep -E "SUCCESS|Device|Email|Name" || true
            return 0
        fi
        
        sleep $wait_interval
        elapsed=$((elapsed + wait_interval))
        attempt=$((attempt + 1))
    done
    
    print_warning "Cloud connection not verified within ${MAX_WAIT}s"
    print_warning "JDownloader is running but cloud status is uncertain"
    print_status "You can manually verify with: $PYTHON_VENV $VERIFY_SCRIPT"
    
    # Show last verification attempt output
    echo ""
    echo "Last verification output:"
    cat /tmp/jd_verify.log | tail -10
    
    return 1
}

show_status() {
    echo ""
    echo "======================================================================"
    echo "                    JDownloader Status"
    echo "======================================================================"
    
    if pgrep -f "JDownloader.jar" > /dev/null; then
        local pid=$(pgrep -f "JDownloader.jar" | head -1)
        print_success "Status: RUNNING (PID: $pid)"
    else
        print_error "Status: NOT RUNNING"
    fi
    
    echo ""
    echo "Control Commands:"
    echo "  Status:  ps aux | grep JDownloader.jar | grep -v grep"
    echo "  Logs:    tail -f $LOG_FILE"
    echo "  Stop:    pkill -9 -f JDownloader.jar"
    echo "  Verify:  $PYTHON_VENV $VERIFY_SCRIPT"
    echo ""
    echo "Web Access: https://my.jdownloader.org"
    echo "======================================================================"
}

# Main execution
main() {
    echo "======================================================================"
    echo "           JDownloader Headless Startup & Cloud Verification"
    echo "======================================================================"
    echo ""
    
    check_requirements
    stop_existing_instances
    start_jdownloader_headless
    
    # Verify cloud connection
    if verify_cloud_connection; then
        show_status
        exit 0
    else
        show_status
        exit 1
    fi
}

# Run main function
main
