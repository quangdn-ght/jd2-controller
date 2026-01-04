# JDownloader Controller - Project Structure

## Overview
This project has been reorganized into a maintainable structure with feature-based modules.

## Project Structure

```
jd2-controller/
├── src/                          # Source code directory
│   ├── __init__.py
│   ├── main.py                   # Main entry point
│   │
│   ├── api/                      # API modules
│   │   ├── __init__.py
│   │   ├── api.py               # REST API
│   │   └── websocket_api.py     # WebSocket API
│   │
│   ├── jdownloader/             # JDownloader integration
│   │   ├── __init__.py
│   │   ├── jd_auth_config.py    # Authentication config
│   │   ├── jd_cloud_connector.py # Cloud connector
│   │   └── jd_websocket_controller.py # WebSocket controller
│   │
│   ├── verification/            # Connection verification
│   │   ├── __init__.py
│   │   ├── connect_and_verify.py
│   │   ├── verify_connection.py
│   │   └── verify_connection_v2.py
│   │
│   ├── client/                  # Client examples and tests
│   │   ├── __init__.py
│   │   ├── test_websocket.py
│   │   ├── websocket_client_example.py
│   │   └── websocket_client.html
│   │
│   └── utils/                   # Utility functions
│       └── __init__.py
│
├── scripts/                     # Shell scripts
│   ├── aliases.sh
│   ├── run.sh
│   ├── setup_venv.sh
│   ├── start_headless.sh
│   ├── start_jd2.sh
│   └── start_websocket_api.sh
│
├── docs/                        # Documentation
│   └── *.md
│
├── main.py                      # Root entry point (wrapper)
├── verify_connection_v2.py      # Verification wrapper
├── jdctl                        # CLI tool
├── requirements.txt
├── .env
├── jd-controller-api.service    # Systemd service file
└── jdownloader.service          # Systemd service file
```

## Module Organization

### API Module (`src/api/`)
- **api.py**: FastAPI REST API for JDownloader management
- **websocket_api.py**: WebSocket API for real-time control

### JDownloader Module (`src/jdownloader/`)
- **jd_auth_config.py**: Configuration management for MyJDownloader
- **jd_cloud_connector.py**: Cloud API connection handler
- **jd_websocket_controller.py**: WebSocket-based JDownloader controller

### Verification Module (`src/verification/`)
- Scripts for testing and verifying JDownloader cloud connections

### Client Module (`src/client/`)
- Example clients and test scripts
- HTML demo client

### Scripts Directory (`scripts/`)
- Shell scripts for starting services, setup, and management

## Usage

### Running the API Server

```bash
# Development mode with auto-reload
python3 main.py --dev

# Production mode
python3 main.py api --prod
```

### Running Verification

```bash
python3 verify_connection_v2.py
```

### Using Scripts

```bash
# Start WebSocket API
./scripts/start_websocket_api.sh

# Start JDownloader headless
./scripts/start_headless.sh

# Setup virtual environment
./scripts/setup_venv.sh
```

### Importing Modules

With the new structure, imports should use the `src` package:

```python
from src.jdownloader import JDownloaderConfig, MyJDownloaderAPI
from src.api import rest_app, websocket_app
```

## Benefits of This Structure

1. **Clear Separation of Concerns**: Each feature has its own directory
2. **Easy Navigation**: Related files are grouped together
3. **Scalability**: Easy to add new features without cluttering root
4. **Maintainability**: Clear module boundaries and dependencies
5. **Professional Structure**: Follows Python packaging best practices

## Migration Notes

- All Python modules moved to `src/` with feature-based subdirectories
- Shell scripts moved to `scripts/`
- Entry points remain at root for backward compatibility
- Service files remain unchanged and work with wrapper scripts
- All imports updated to use new package structure
