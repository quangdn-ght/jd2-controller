# 🎨 Using the WebSocket Demo Client

## Quick Access

Once the WebSocket API server is running, access the interactive demo at:

**http://localhost:8001/demo**

## What is the Demo?

The demo is a beautiful, interactive web interface that allows you to control JDownloader directly from your browser. No additional files to open - just visit the URL!

## Features

- 🎨 **Modern UI** - Beautiful gradient design with responsive layout
- 📊 **Live Statistics** - Real-time monitoring of active downloads, progress, and status
- 📥 **Easy Link Management** - Add multiple download links with one click
- 🎮 **One-Click Controls** - Start, pause, stop downloads instantly
- 📦 **Download List** - View all downloads with progress bars
- 📜 **Console Log** - Monitor all API communications in real-time
- 🔌 **Auto-Connect** - Automatically connects when page loads

## How to Use

### 1. Start the Server

```bash
./start_websocket_api.sh
```

### 2. Open the Demo

Visit http://localhost:8001/demo in your browser

### 3. Connect to JDownloader

Click the **"Connect to JDownloader"** button

You should see:
- Status indicator turns green
- Connection message in console log
- Statistics update with current downloads

### 4. Add Downloads

1. Enter URLs in the text area (one per line)
2. Optionally enter a package name
3. Click **"➕ Add Links"**

Example:
```
https://example.com/file1.zip
https://example.com/file2.mp4
https://example.com/file3.pdf
```

### 5. Control Downloads

Use the control buttons:
- **▶️ Start** - Begin downloading
- **⏸️ Pause** - Pause active downloads
- **⏹️ Stop** - Stop all downloads
- **📊 Status** - Get current status

### 6. Monitor Progress

Click **"▶️ Start Monitoring"** to receive real-time updates every 2 seconds.

You'll see:
- Active downloads count
- Total downloads
- Overall progress percentage
- Individual download progress bars
- Download speeds and ETA

### 7. View Downloads

Click **"📋 Get Downloads"** to refresh the download list and see:
- File names
- Download status
- Progress bars
- Bytes downloaded/total

## Tips

### Add Downloads Quickly

You can paste multiple URLs at once - the demo will handle them all:

```
https://site.com/video1.mp4
https://site.com/video2.mp4
https://site.com/video3.mp4
```

### Monitor in Real-Time

Start monitoring before adding downloads to see them appear in real-time as they're added and start downloading.

### Check Linkgrabber

Click **"🔗 Get Linkgrabber"** to see links that were added but haven't been moved to downloads yet.

### Use Package Names

Organize your downloads with package names:
- "Movies"
- "Software"
- "Documents"
- "January 2026 Downloads"

## Troubleshooting

### Can't Connect to JDownloader

1. **Check if server is running:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Check if JDownloader is running:**
   ```bash
   ps aux | grep JDownloader
   ```

3. **Verify cloud connection:**
   ```bash
   python3 verify_connection_v2.py
   ```

### Demo Page Won't Load

1. **Check server is running on port 8001:**
   ```bash
   lsof -i :8001
   ```

2. **Try accessing health endpoint:**
   ```bash
   curl http://localhost:8001/health
   ```

3. **Check server logs:**
   Look at the terminal where you started the server

### WebSocket Connection Failed

1. **Check browser console** (F12) for error messages
2. **Verify WebSocket URL** - should be `ws://localhost:8001/ws`
3. **Try refreshing** the page
4. **Check firewall** settings

### No Downloads Showing

1. **Connect first** - Click "Connect to JDownloader" button
2. **Check linkgrabber** - Links might be in linkgrabber, not downloads
3. **Verify credentials** - Make sure your .env file is configured

## Browser Compatibility

The demo works in all modern browsers:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Opera

## Mobile Friendly

The demo is responsive and works on mobile devices! Access it from your phone or tablet by using your server's IP address:

```
http://YOUR_SERVER_IP:8001/demo
```

For example:
```
http://192.168.1.100:8001/demo
```

## Advanced Usage

### Monitoring Interval

The default monitoring interval is 2 seconds. You can adjust this by:
1. Stop monitoring
2. Edit the interval in the JavaScript console:
   ```javascript
   // Change interval to 5 seconds
   ws.send(JSON.stringify({
       action: 'start_monitoring',
       interval: 5
   }));
   ```

### Custom Commands

Open browser console (F12) and send custom commands:

```javascript
// Get specific download status
ws.send(JSON.stringify({
    action: 'get_downloads'
}));

// Remove specific links
ws.send(JSON.stringify({
    action: 'remove',
    link_ids: [1, 2, 3]
}));
```

## Architecture

```
Browser (Demo Client)
       ↓
   WebSocket
       ↓
websocket_api.py (Server)
       ↓
jd_websocket_controller.py
       ↓
   myjdapi
       ↓
MyJDownloader Cloud
       ↓
JDownloader Instance
```

## Next Steps

- Try the [Python client examples](websocket_client_example.py)
- Read the [complete API guide](docs/WEBSOCKET_API_GUIDE.md)
- Check the [quick reference](WEBSOCKET_QUICK_REFERENCE.txt)
- Explore the [API documentation](http://localhost:8001/docs)

---

**Enjoy controlling your JDownloader with a beautiful web interface!** 🎉
