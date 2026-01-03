# JDownloader Controller - main.py Usage Guide

## 🎯 Overview

`main.py` is the unified entry point for the JDownloader Controller that supports:
- ✅ API server with auto-reload in dev mode
- ✅ JDownloader headless startup
- ✅ CLI command integration
- ✅ Comprehensive status checking

## 🚀 Quick Start

### Using the wrapper script (recommended)
```bash
./run.sh --dev          # Start API in dev mode
./run.sh status         # Show status
./run.sh cli verify     # Verify cloud connection
```

### Direct usage
```bash
python3 main.py --dev   # Start API in dev mode
python3 main.py status  # Show status
```

## 📋 Commands

### 1. API Server

#### Development Mode (Auto-reload) ⭐
```bash
# Default settings
python3 main.py --dev
python3 main.py api --dev

# Custom host/port
python3 main.py --dev --host 127.0.0.1 --port 8080

# Using wrapper
./run.sh --dev
```

**Features:**
- ✅ Automatic reload when .py files change
- ✅ Watches all Python files in directory
- ✅ Detailed logging
- ✅ Perfect for development

**Output:**
```
======================================================================
              JDownloader Controller API Server
======================================================================

🚀 Starting API server...
📍 URL: http://0.0.0.0:8001
📖 Docs: http://0.0.0.0:8001/docs
🔄 Mode: DEVELOPMENT (auto-reload)
👀 Watching files for changes...
💡 Press Ctrl+C to stop
```

#### Production Mode
```bash
# Default settings
python3 main.py --prod
python3 main.py api --prod

# Using wrapper
./run.sh --prod
```

**Features:**
- ✅ No auto-reload (better performance)
- ✅ Minimal logging
- ✅ Optimized for production

### 2. Start JDownloader Headless

```bash
# Using main.py
python3 main.py start
python3 main.py headless

# Using wrapper
./run.sh start
./run.sh headless
```

This runs the headless startup script with automatic cloud verification.

### 3. CLI Integration

Execute any jdctl command through main.py:

```bash
# Status
python3 main.py cli status
./run.sh cli status

# Verify cloud
python3 main.py cli verify
./run.sh cli verify

# View logs
python3 main.py cli logs
./run.sh cli logs

# Control
python3 main.py cli start
python3 main.py cli stop
python3 main.py cli restart
```

### 4. Comprehensive Status

```bash
python3 main.py status
./run.sh status
```

**Shows:**
- ✅ JDownloader service status (running/stopped with PIDs)
- ✅ API server status (running/stopped with PIDs)
- ✅ Cloud connection status (connected/disconnected with device name)

**Example output:**
```
======================================================================
                JDownloader Controller Status
======================================================================

📦 JDownloader Service:
   ✅ Running (PIDs: 1221747, 1221751, 1221752)

🌐 API Server:
   ✅ Running (PIDs: 1256789)
   �� URL: http://localhost:8001/docs

☁️  Cloud Connection:
   ✅ Connected to MyJDownloader cloud
   📱 Device: JDownloader@root

======================================================================
```

## 🔧 Auto-Reload in Dev Mode

When running with `--dev`, the server will automatically reload when you edit:

**Watched files:**
- `api.py`
- `jd_auth_config.py`
- `jd_cloud_connector.py`
- `verify_connection_v2.py`
- `connect_and_verify.py`
- Any other `.py` file in the directory

**Example workflow:**
```bash
# 1. Start dev server
./run.sh --dev

# 2. Edit api.py in another terminal
nano api.py

# 3. Save the file
# Server automatically reloads!

# 4. Test changes
curl http://localhost:8001/cli/status
```

## 📡 Available API Endpoints

Once the API is running, you can access:

### Interactive Documentation
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### CLI Commands (via API)
- `POST /cli/start` - Start JDownloader headless
- `POST /cli/stop` - Stop JDownloader
- `POST /cli/restart` - Restart JDownloader
- `GET /cli/status` - Get status
- `POST /cli/verify` - Verify cloud
- `GET /cli/logs?lines=50` - Get logs

### Examples
```bash
# Get status
curl http://localhost:8001/cli/status

# Verify cloud connection
curl -X POST http://localhost:8001/cli/verify

# Get last 100 lines of logs
curl http://localhost:8001/cli/logs?lines=100

# Stop JDownloader
curl -X POST http://localhost:8001/cli/stop
```

## 🔄 Systemd Service

For production deployment:

```bash
# Copy service file
sudo cp jd-controller-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable jd-controller-api

# Start service
sudo systemctl start jd-controller-api

# Check status
sudo systemctl status jd-controller-api

# View logs
sudo journalctl -u jd-controller-api -f
```

The systemd service runs in production mode automatically.

## ⚙️ Configuration

### Environment Variables

Edit `.env` file:
```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8001
API_RELOAD=false  # Set to true for auto-reload by default
API_KEY=           # Optional API key for authentication

# JDownloader
JDOWNLOADER_EMAIL=your@email.com
JDOWNLOADER_PASSWORD=yourpassword
JDOWNLOADER_HOME=/opt/jd2
JDOWNLOADER_DEVICE_NAME=
```

### Command Line Override

```bash
# Override host and port
python3 main.py --dev --host 127.0.0.1 --port 9000

# This ignores .env settings for host/port
```

## 🐛 Troubleshooting

### API won't start

**Check if port is in use:**
```bash
lsof -i :8001
```

**Kill existing process:**
```bash
pkill -f "python.*api.py"
```

**Try different port:**
```bash
./run.sh --dev --port 8002
```

### Auto-reload not working

**Make sure you're using --dev flag:**
```bash
./run.sh --dev  # ✅ Will reload
./run.sh        # ❌ Won't reload (defaults to api mode without --dev)
```

**Check if file is being watched:**
Look for "Watching" in startup output.

### Virtual environment issues

**Recreate venv:**
```bash
rm -rf venv
./setup_venv.sh
```

**Check venv python:**
```bash
ls -la venv/bin/python
```

## 📊 Command Comparison

| Task | Old Way | New Way (main.py) |
|------|---------|-------------------|
| Start API dev | `python api.py` (manual reload) | `./run.sh --dev` (auto-reload) |
| Start API prod | `python api.py &` | `./run.sh --prod` |
| Start JDownloader | `./start_headless.sh` | `./run.sh start` |
| Check status | `./jdctl status` | `./run.sh status` OR `./run.sh cli status` |
| Verify cloud | `./jdctl verify` | `./run.sh cli verify` |
| View logs | `./jdctl logs` | `./run.sh cli logs` |

## ✨ Benefits

### Unified Entry Point
- Single command for all operations
- Consistent interface
- Easy to remember

### Auto-Reload in Dev
- No manual server restarts
- Faster development cycle
- See changes immediately

### Comprehensive Status
- See everything at a glance
- JDownloader, API, and Cloud status
- Quick diagnostics

### Production Ready
- Systemd service support
- Proper process management
- Clean shutdown

## 🎯 Typical Workflows

### Development Workflow
```bash
# 1. Start API in dev mode
./run.sh --dev

# 2. Open another terminal and edit code
nano api.py

# 3. Save - server auto-reloads

# 4. Test in browser
firefox http://localhost:8001/docs

# 5. Make more changes - repeat
```

### Production Deployment
```bash
# 1. Setup systemd service
sudo cp jd-controller-api.service /etc/systemd/system/
sudo systemctl enable jd-controller-api
sudo systemctl start jd-controller-api

# 2. Check status
./run.sh status

# 3. Monitor logs
sudo journalctl -u jd-controller-api -f
```

### Daily Operations
```bash
# Morning check
./run.sh status

# Verify everything is connected
./run.sh cli verify

# Check logs if needed
./run.sh cli logs

# Restart if necessary
./run.sh cli restart
```

## 📚 Related Documentation

- **QUICKSTART.md** - Quick start guide
- **HEADLESS_GUIDE.md** - Headless operation guide
- **QUICK_REFERENCE.txt** - Command reference
- **API Docs** - http://localhost:8001/docs (when running)

---

**Status**: ✅ Fully functional with auto-reload support  
**Version**: 2.0.0  
**Date**: January 3, 2026
