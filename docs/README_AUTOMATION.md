# JDownloader Cloud Authentication - Python Automation

This package provides Python scripts to automate JDownloader MyJDownloader Cloud authentication and connection management.

## �� Scripts Overview

### `jd_auth_config.py` - Configuration Manager
Manages MyJDownloader credentials and configuration.

**Features:**
- Update email and password
- Enable/disable auto-connect
- Display current configuration
- Validate credentials before saving

**Usage:**
```bash
# Configure credentials
python3 jd_auth_config.py --email your@email.com --password yourpassword

# Show current configuration
python3 jd_auth_config.py --show-config

# Set custom device name
python3 jd_auth_config.py --email your@email.com --password yourpass --device-name "MyServer"
```

## 🚀 Quick Start Guide

### 1. Configure Credentials
```bash
cd /opt/jd2
python3 jd_auth_config.py \
  --email quangdn@giahungtech.com.vn \
  --password Giahung@2024
```

### 2. Verify Configuration
```bash
python3 jd_auth_config.py --show-config
```

### 3. Start JDownloader
```bash
sudo java -jar JDownloader.jar -norestart
```

### 4. Check Connection
- Wait 10-30 seconds for initial connection
- Visit: https://my.jdownloader.org
- Login with your credentials
- Your device should appear in the devices list

## 🔄 Complete Automation Workflow

```bash
#!/bin/bash
# Complete automation script

# 1. Configure credentials
python3 /opt/jd2/jd_auth_config.py \
  --email "quangdn@giahungtech.com.vn" \
  --password "Giahung@2024" \
  --device-name "ProductionServer"

# 2. Verify configuration
python3 /opt/jd2/jd_auth_config.py --show-config

# 3. Start JDownloader
cd /opt/jd2
sudo java -jar JDownloader.jar -norestart &

# 4. Wait for startup
sleep 10

# 5. Check if running
ps aux | grep JDownloader
```

## 📋 Configuration File

**Location:** `/opt/jd2/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json`

**Structure:**
```json
{
  "email": "your@email.com",
  "password": "yourpassword",
  "autoconnectenabledv2": true,
  "devicename": "JDownloader@hostname",
  "serverhost": "api.jdownloader.org",
  "directconnectmode": "LAN",
  "latesterror": "NONE"
}
```

## 🔐 Security Best Practices

### 1. Use Environment Variables
```bash
export MJD_EMAIL="your@email.com"
export MJD_PASSWORD="yourpassword"

python3 jd_auth_config.py --email "$MJD_EMAIL" --password "$MJD_PASSWORD"
```

### 2. Secure Configuration Files
```bash
# Restrict access to config files
sudo chmod 600 /opt/jd2/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json
sudo chown root:root /opt/jd2/cfg/*.json
```

### 3. Use Systemd Service
Create `/etc/systemd/system/jdownloader.service`:
```ini
[Unit]
Description=JDownloader 2
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/opt/jd2
ExecStart=/usr/bin/java -jar /opt/jd2/JDownloader.jar -norestart
ExecStop=/usr/bin/pkill -f JDownloader.jar
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jdownloader
sudo systemctl start jdownloader
sudo systemctl status jdownloader
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# 1. Check configuration
python3 jd_auth_config.py --show-config

# 2. Verify JDownloader is running
ps aux | grep JDownloader

# 3. Check logs
tail -f /opt/jd2/logs/*/Log.L.log

# 4. Restart JDownloader
sudo pkill -f JDownloader.jar
sudo java -jar /opt/jd2/JDownloader.jar -norestart &
```

### Common Errors

**"Configuration file not found"**
- Run: `python3 jd_auth_config.py --email <email> --password <pass>`

**"JDownloader is already running"**
- Stop first: `sudo pkill -f JDownloader.jar`

**"Permission denied"**
- Run with sudo: `sudo python3 jd_auth_config.py ...`

**"Invalid email format"**
- Ensure email contains @ symbol

**"Password too short"**
- Password must be at least 6 characters

## 📊 Monitoring and Logging

### Check JDownloader Logs
```bash
# List log directories
ls -lh /opt/jd2/logs/

# View latest log
tail -f /opt/jd2/logs/$(ls -t /opt/jd2/logs/ | head -1)/Log.L.log
```

### Monitor Service Status
```bash
#!/bin/bash
# monitor.sh - Continuous monitoring

while true; do
    clear
    echo "=== JDownloader Status Monitor ==="
    date
    echo ""
    
    # Check if running
    if pgrep -f "JDownloader.jar" > /dev/null; then
        echo "✓ Status: Running"
        echo "  PID: $(pgrep -f JDownloader.jar)"
    else
        echo "✗ Status: Not running"
    fi
    
    # Show configuration
    python3 /opt/jd2/jd_auth_config.py --show-config
    
    sleep 30
done
```

## 🎯 Advanced Usage

### Automated Restart on Failure
```bash
#!/bin/bash
# auto_restart.sh

while true; do
    if ! pgrep -f "JDownloader.jar" > /dev/null; then
        echo "$(date): JDownloader not running, restarting..."
        cd /opt/jd2
        sudo java -jar JDownloader.jar -norestart &
    fi
    sleep 60
done
```

### Scheduled Configuration Updates
```bash
# Add to crontab: crontab -e
# Update credentials daily at 3 AM
0 3 * * * /usr/bin/python3 /opt/jd2/jd_auth_config.py --email "$MJD_EMAIL" --password "$MJD_PASSWORD"

# Check and restart if needed every hour
0 * * * * pgrep -f "JDownloader.jar" || (cd /opt/jd2 && /usr/bin/java -jar JDownloader.jar -norestart &)
```

## 📚 Script Arguments Reference

### jd_auth_config.py

```
Arguments:
  --email, -e           MyJDownloader email address
  --password, -p        MyJDownloader password
  --device-name, -d     Device name (default: JDownloader@hostname)
  --show-config         Display current configuration
  -h, --help            Show help message
```

**Examples:**
```bash
# Update credentials
python3 jd_auth_config.py -e user@example.com -p mypassword

# Change device name
python3 jd_auth_config.py -e user@example.com -p mypassword -d "MyServer"

# View configuration
python3 jd_auth_config.py --show-config
```

## 🔄 Integration Examples

### Bash Script Integration
```bash
#!/bin/bash
# setup_jdownloader.sh

set -e

echo "Configuring JDownloader..."
python3 /opt/jd2/jd_auth_config.py \
    --email "${JD_EMAIL}" \
    --password "${JD_PASSWORD}" \
    --device-name "${JD_DEVICE_NAME:-JDownloader}"

echo "Starting JDownloader..."
cd /opt/jd2
sudo java -jar JDownloader.jar -norestart &

echo "Waiting for startup..."
sleep 15

if pgrep -f "JDownloader.jar" > /dev/null; then
    echo "✓ JDownloader started successfully!"
else
    echo "✗ Failed to start JDownloader"
    exit 1
fi
```

### Docker Integration
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    python3 \
    wget

# Copy JDownloader
COPY jd2 /opt/jd2

# Configure credentials from environment
RUN python3 /opt/jd2/jd_auth_config.py \
    --email "${MJD_EMAIL}" \
    --password "${MJD_PASSWORD}"

# Start JDownloader
CMD ["java", "-jar", "/opt/jd2/JDownloader.jar", "-norestart"]
```

### Ansible Playbook
```yaml
---
- name: Configure JDownloader
  hosts: jdownloader_servers
  tasks:
    - name: Configure MyJDownloader credentials
      command: >
        python3 /opt/jd2/jd_auth_config.py
        --email "{{ myjd_email }}"
        --password "{{ myjd_password }}"
        --device-name "{{ inventory_hostname }}"
      
    - name: Start JDownloader service
      systemd:
        name: jdownloader
        state: started
        enabled: yes
```

## 📖 API Reference

### JDownloaderConfig Class

```python
from jd_auth_config import JDownloaderConfig

# Initialize
jd = JDownloaderConfig(jd_home="/opt/jd2")

# Read configuration
config = jd.read_config()

# Update credentials
success = jd.update_credentials(
    email="user@example.com",
    password="mypassword",
    device_name="MyServer"
)

# Display configuration
jd.display_config()
```

## 🤝 Support

For issues or questions:
1. Check this README
2. Review script help: `python3 jd_auth_config.py --help`
3. Check JDownloader logs in `/opt/jd2/logs/`
4. Visit: https://my.jdownloader.org
5. JDownloader support: https://support.jdownloader.org

## 📝 Version History

- **v1.0.0** (2026-01-03)
  - Initial release
  - Basic credential configuration
  - Configuration display
  - Input validation

## 📄 License

These scripts are provided as-is for automation purposes.

---

**Last Updated:** 2026-01-03
**Version:** 1.0.0
**Maintainer:** System Administrator
