# JDownloader Cloud Connection Guide

## ✅ Connection Successfully Verified!

Your JDownloader is now connected to MyJDownloader cloud.

## 📋 Quick Reference

### Start JDownloader
```bash
cd /home/ght/project/jd2-controller
./start_jd2.sh
```

### Verify Cloud Connection
```bash
cd /home/ght/project/jd2-controller
source venv/bin/activate
python verify_connection_v2.py
```

### Check if Running
```bash
ps aux | grep JDownloader.jar
```

### View Logs
```bash
tail -f /tmp/jd2.log
```

### Stop JDownloader
```bash
sudo pkill -9 -f JDownloader.jar
```

## 🔄 Auto-Start on Boot (Optional)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/jdownloader.service
```

Add:
```ini
[Unit]
Description=JDownloader Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/jd2
ExecStart=/usr/bin/java -jar /opt/jd2/JDownloader.jar -norestart
Restart=always
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

## 🌐 Access Your Downloads

- Web Interface: https://my.jdownloader.org
- Device: **JDownloader@root**
- Status: **Connected** ✅

## 🔧 Troubleshooting

If connection fails:
1. Check credentials in `/opt/jd2/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json`
2. Restart JDownloader: `sudo pkill -9 -f JDownloader.jar && ./start_jd2.sh`
3. Wait 1-2 minutes for cloud connection to establish
4. Verify with: `python verify_connection_v2.py`
