# JDownloader Controller - FastAPI Refactored

RESTful API for managing JDownloader MyJDownloader authentication and configuration.

## 🚀 Quick Setup

### 1. Clone and Navigate
```bash
cd /home/ght/project/jd2-controller
```

### 2. Setup Virtual Environment
```bash
# Make the setup script executable
chmod +x setup_venv.sh

# Run the setup script
./setup_venv.sh

# Activate the virtual environment
source venv/bin/activate
```

### 3. Configure Environment Variables
```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

**Required settings in `.env`:**
```env
JDOWNLOADER_EMAIL=your@email.com
JDOWNLOADER_PASSWORD=yourpassword
JDOWNLOADER_HOME=/opt/jd2
API_PORT=8000
# Optional: Set API_KEY for security
API_KEY=your-secret-api-key
```

### 4. Install Dependencies
```bash
# If not already done by setup_venv.sh
pip install -r requirements.txt
```

## 📡 Using the FastAPI Application

### Start the API Server
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the API server
python api.py
```

The API will be available at:
- **API Endpoint**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### API Endpoints

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

#### 2. Get Current Configuration
```bash
curl http://localhost:8000/config
```

**With API Key:**
```bash
curl -H "X-API-Key: your-secret-api-key" http://localhost:8000/config
```

#### 3. Update Credentials
```bash
curl -X POST http://localhost:8000/config/credentials \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword",
    "device_name": "MyServer"
  }'
```

#### 4. Get Connection Status
```bash
curl -H "X-API-Key: your-secret-api-key" \
  http://localhost:8000/config/status
```

#### 5. Clear Credentials
```bash
curl -X DELETE http://localhost:8000/config/credentials \
  -H "X-API-Key: your-secret-api-key"
```

## 🔧 CLI Usage (Legacy Support)

The original CLI tool still works and now supports environment variables:

```bash
# Using environment variables from .env
python jd_auth_config.py --show-config

# Override with command line arguments
python jd_auth_config.py --email test@email.com --password testpass

# Using only environment variables
python jd_auth_config.py
```

## 🔒 Security

### API Key Authentication
Set `API_KEY` in your `.env` file to enable API key authentication:

```env
API_KEY=your-super-secret-key-here
```

All API requests must include the header:
```
X-API-Key: your-super-secret-key-here
```

### Production Deployment
For production use:
1. Always set a strong `API_KEY`
2. Use HTTPS with a reverse proxy (nginx, traefik, etc.)
3. Consider using environment variables directly instead of .env file
4. Restrict API access with firewall rules

## 🐳 Running as a Service

### Systemd Service Example
Create `/etc/systemd/system/jd-controller-api.service`:

```ini
[Unit]
Description=JDownloader Controller API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/ght/project/jd2-controller
Environment="PATH=/home/ght/project/jd2-controller/venv/bin"
ExecStart=/home/ght/project/jd2-controller/venv/bin/python api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jd-controller-api
sudo systemctl start jd-controller-api
sudo systemctl status jd-controller-api
```

## 📦 Project Structure

```
jd2-controller/
├── api.py                  # FastAPI application
├── jd_auth_config.py      # Core configuration module
├── requirements.txt       # Python dependencies
├── setup_venv.sh         # Virtual environment setup script
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── .gitignore           # Git ignore rules
├── venv/                # Virtual environment (created by setup)
└── README.md            # This file
```

## 🧪 Testing the API

### Using curl
```bash
# Test health
curl http://localhost:8000/health

# Get configuration
curl -H "X-API-Key: your-key" http://localhost:8000/config

# Update credentials
curl -X POST http://localhost:8000/config/credentials \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"email":"test@test.com","password":"password123"}'
```

### Using Python requests
```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key"
headers = {"X-API-Key": API_KEY}

# Get config
response = requests.get(f"{API_URL}/config", headers=headers)
print(response.json())

# Update credentials
data = {
    "email": "your@email.com",
    "password": "yourpassword",
    "device_name": "MyServer"
}
response = requests.post(
    f"{API_URL}/config/credentials",
    json=data,
    headers=headers
)
print(response.json())
```

### Using the Interactive Docs
Navigate to http://localhost:8000/docs to use the built-in Swagger UI for testing all endpoints interactively.

## 🆘 Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
./setup_venv.sh
```

### Port Already in Use
Change the port in `.env`:
```env
API_PORT=8001
```

### Permission Errors
Make sure your user has access to the JDownloader directory:
```bash
sudo chown -R $USER:$USER /opt/jd2
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JDownloader MyJDownloader](https://my.jdownloader.org/)
- [Original Documentation](README_AUTOMATION.md)

## 🔄 Migration from Old Setup

If you were using the old setup:
1. Your existing JDownloader configuration will still work
2. Create the `.env` file with your credentials
3. Run `./setup_venv.sh` to set up the new environment
4. Start using the API or continue with CLI

No data migration needed - the same configuration files are used!
