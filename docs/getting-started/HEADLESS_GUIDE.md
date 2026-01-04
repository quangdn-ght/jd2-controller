# JDownloader Headless Control Guide

## 🎯 Overview

JDownloader is now configured to run in **headless mode** (no GUI) with automatic cloud verification on every startup.

## 🚀 Quick Start

### Option 1: Using the Headless Startup Script (Recommended)
```bash
cd /home/ght/project/jd2-controller
./start_headless.sh
```

This script will:
- ✅ Check all requirements
- ✅ Stop any existing instances
- ✅ Start JDownloader in headless mode
- ✅ Automatically verify cloud connection
- ✅ Display status and control commands

### Option 2: Using the CLI Control Tool
```bash
cd /home/ght/project/jd2-controller

# Start JDownloader
./jdctl start

# Check status
./jdctl status

# Verify cloud connection
./jdctl verify

# View logs
./jdctl logs

# Follow logs in real-time
./jdctl logs --follow

# Stop JDownloader
./jdctl stop

# Restart JDownloader
./jdctl restart
```

## 📋 CLI Commands Reference

### `jdctl start`
Starts JDownloader in headless mode with automatic cloud verification.

### `jdctl stop`
Gracefully stops JDownloader.

### `jdctl restart`
Stops and restarts JDownloader.

### `jdctl status`
Shows:
- Running status
- Process IDs
- Resource usage
- Log file location

### `jdctl verify`
Verifies connection to MyJDownloader cloud and shows connected devices.

### `jdctl logs`
Shows the last 50 lines of logs.

### `jdctl logs --follow`
Follows logs in real-time (press Ctrl+C to stop).

## 🔧 Headless Configuration

JDownloader runs with these settings:
- **Mode**: Headless (no GUI)
- **Flag**: `-Djava.awt.headless=true`
- **Arguments**: `-norestart -noerr`
- **Log File**: `/tmp/jd2.log`
- **Working Directory**: `/opt/jd2`

## 🔄 Auto-Start on Boot

### Method 1: Systemd Service (Recommended)

1. **Copy the service file**:
```bash
sudo cp /home/ght/project/jd2-controller/jdownloader.service /etc/systemd/system/
```

2. **Enable and start the service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jdownloader
sudo systemctl start jdownloader
```

3. **Check service status**:
```bash
sudo systemctl status jdownloader
```

4. **Service commands**:
```bash
# Start
sudo systemctl start jdownloader

# Stop
sudo systemctl stop jdownloader

# Restart
sudo systemctl restart jdownloader

# View logs
sudo journalctl -u jdownloader -f
```

### Method 2: Cron Job

Add to root's crontab:
```bash
sudo crontab -e
```

Add this line:
```cron
@reboot sleep 30 && /home/ght/project/jd2-controller/start_headless.sh > /tmp/jd_startup.log 2>&1
```

## 🔍 Cloud Verification

Every startup automatically:
1. Waits for JDownloader to initialize (10 seconds)
2. Attempts cloud verification every 10 seconds
3. Maximum wait time: 90 seconds
4. Shows connected devices and status

**Successful verification shows**:
- ✅ Cloud connection verified
- Device name and ID
- Connection status

## 📊 Monitoring

### Check if Running
```bash
ps aux | grep JDownloader.jar | grep -v grep
```

### View Real-time Logs
```bash
tail -f /tmp/jd2.log
```

### Check Cloud Status
```bash
cd /home/ght/project/jd2-controller
./jdctl verify
```

### Using FastAPI
```bash
# Start API server
cd /home/ght/project/jd2-controller
source venv/bin/activate
python api.py &

# Check service status
curl http://localhost:8001/service/status

# Verify cloud connection
curl http://localhost:8001/cloud/verify

# View API docs
firefox http://localhost:8001/docs
```

## 🎮 Control Options

### 1. Shell Scripts
- `start_headless.sh` - Start with verification
- `jdctl` - Full CLI control

### 2. Python Scripts
- `verify_connection_v2.py` - Verify cloud only
- `connect_and_verify.py` - Complete process

### 3. FastAPI Endpoints
- `POST /service/start` - Start service
- `POST /service/stop` - Stop service
- `GET /service/status` - Get status
- `POST /cloud/verify` - Verify cloud

### 4. Systemd Service
- `systemctl start/stop/restart jdownloader`

## 🐛 Troubleshooting

### JDownloader Won't Start
```bash
# Check if Java is installed
java -version

# Check if port is in use
netstat -tulpn | grep java

# Check logs
tail -100 /tmp/jd2.log

# Try manual start
cd /opt/jd2
sudo java -Djava.awt.headless=true -jar JDownloader.jar -norestart
```

### Cloud Connection Fails
```bash
# Verify credentials
sudo cat /opt/jd2/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json

# Wait longer (initial connection can take 1-2 minutes)
sleep 60
./jdctl verify

# Check network connectivity
ping api.jdownloader.org

# Restart with fresh connection
./jdctl restart
```

### Multiple Instances Running
```bash
# Kill all instances
sudo pkill -9 -f JDownloader.jar

# Wait and start fresh
sleep 3
./start_headless.sh
```

## 📱 Web Access

Access your JDownloader from anywhere:
- **URL**: https://my.jdownloader.org
- **Device**: JDownloader@root
- **Email**: quangdn@giahungtech.com.vn

## 🔐 Security Notes

1. **No GUI** means no local interface - control only via:
   - Web interface (my.jdownloader.org)
   - CLI tools (jdctl)
   - API endpoints

2. **Credentials** are stored in:
   - `/opt/jd2/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json`
   - `/home/ght/project/jd2-controller/.env`

3. **API Security**: Set `API_KEY` in `.env` for protected endpoints

## 📁 File Locations

- **JDownloader Home**: `/opt/jd2`
- **Config Files**: `/opt/jd2/cfg/`
- **Logs**: `/tmp/jd2.log`
- **Scripts**: `/home/ght/project/jd2-controller/`
- **Downloads**: `/opt/jd2/Downloads/` (default)

## ✅ Verification Checklist

After startup, verify:
- [ ] Process is running: `./jdctl status`
- [ ] Cloud connected: `./jdctl verify`
- [ ] Web accessible: https://my.jdownloader.org
- [ ] Logs are clean: `./jdctl logs | tail -20`

## 🎉 Success Indicators

When everything is working:
```
✅ JDownloader running (PID: XXXXX)
✅ Cloud connection verified!
✅ Device 1: JDownloader@root
🎉 SUCCESS! JDownloader is connected to MyJDownloader cloud!
```

---

**Status**: Headless mode configured ✅  
**Auto-verification**: Enabled ✅  
**Control Method**: CLI only ✅
