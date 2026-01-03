# JDownloader Controller - Quick Start Guide

## 🚀 Quick Start

### Development Mode (Auto-reload)
```bash
# Using run.sh wrapper
./run.sh --dev

# Or directly with venv python
source venv/bin/activate
python main.py --dev
```

### Production Mode
```bash
# Using run.sh wrapper  
./run.sh --prod

# Or directly
source venv/bin/activate
python main.py --prod
```

### Start JDownloader Headless
```bash
./run.sh start
# Or
./run.sh headless
```

### Show Status
```bash
./run.sh status
```

### Run CLI Commands
```bash
./run.sh cli status
./run.sh cli verify
./run.sh cli logs
./run.sh cli start
./run.sh cli stop
```

## 🔧 Main Commands

### API Server
```bash
# Dev mode with auto-reload
python3 main.py --dev

# Production mode
python3 main.py --prod

# Custom host/port
python3 main.py --dev --host 127.0.0.1 --port 8080
```

### JDownloader Control
```bash
# Start JDownloader headless
python3 main.py start

# Show comprehensive status
python3 main.py status
```

### CLI Integration
```bash
# Run any jdctl command
python3 main.py cli <command>

# Examples:
python3 main.py cli status
python3 main.py cli verify
python3 main.py cli logs
python3 main.py cli start
python3 main.py cli stop
python3 main.py cli restart
```

## 📦 Installation

### Make scripts executable
```bash
chmod +x run.sh main.py
```

### Setup systemd service (optional)
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

## 🔄 Development Workflow

### 1. Start API in dev mode
```bash
./run.sh --dev
```

### 2. Edit files
The server will automatically reload when you edit:
- `api.py`
- `jd_auth_config.py`
- `jd_cloud_connector.py`
- Any `.py` file in the directory

### 3. Test endpoints
Visit: http://localhost:8001/docs

### 4. Stop server
Press `Ctrl+C`

## 📊 API Endpoints

### CLI Commands via API
- `POST /cli/start` - Start JDownloader headless
- `POST /cli/stop` - Stop JDownloader
- `POST /cli/restart` - Restart JDownloader
- `GET /cli/status` - Get status with PIDs
- `POST /cli/verify` - Verify cloud connection
- `GET /cli/logs?lines=50` - Get logs

### Configuration
- `GET /config` - Get current config
- `POST /config/credentials` - Update credentials
- `DELETE /config/credentials` - Clear credentials

### Cloud Connection
- `POST /cloud/connect` - Connect to cloud
- `GET /cloud/devices` - List devices
- `POST /cloud/verify` - Verify connection

### Service Management
- `GET /service/status` - Service status
- `POST /service/start` - Start service
- `POST /service/stop` - Stop service
- `POST /service/restart` - Restart service

## 🌐 Access

- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Web**: https://my.jdownloader.org

## 🐛 Troubleshooting

### Port already in use
```bash
# Change port
./run.sh --dev --port 8002
```

### API won't start
```bash
# Check logs
tail -f /tmp/api.log

# Check if venv is set up
ls -la venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Auto-reload not working
Make sure you're using `--dev` flag:
```bash
./run.sh --dev  # ✅ Correct
./run.sh        # ❌ Won't reload
```

## 📝 Environment Variables

Edit `.env` file:
```env
# JDownloader
JDOWNLOADER_EMAIL=your@email.com
JDOWNLOADER_PASSWORD=yourpassword
JDOWNLOADER_HOME=/opt/jd2

# API
API_HOST=0.0.0.0
API_PORT=8001
API_RELOAD=false  # Set to true for auto-reload by default

# Security
API_KEY=your-secret-key  # Optional
```

## ✅ Features

- ✅ Auto-reload in development mode
- ✅ Production mode for deployment
- ✅ Comprehensive status checking
- ✅ CLI command integration
- ✅ Systemd service support
- ✅ Environment variable configuration
- ✅ Interactive API documentation
- ✅ Full REST API for all operations
