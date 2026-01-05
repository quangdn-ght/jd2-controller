# Build Script Documentation

## Overview
The `build.sh` script packages the JDownloader Controller project for deployment, including only essential files needed to run the application on another host.

## Usage

### Build Package
```bash
./build.sh
```

This will create a timestamped distribution package in `build/dist/`.

## What Gets Packaged

### Essential Files (Included):
- ✅ `main.py` - Main entry point
- ✅ `requirements.txt` - Python dependencies
- ✅ `src/` - Application source code (excluding `__pycache__`)
- ✅ `jdctl` - CLI tool
- ✅ `*.service` - Systemd service files
- ✅ `scripts/setup_venv.sh` - Virtual environment setup
- ✅ `scripts/run.sh` - Application runner
- ✅ Auto-generated deployment documentation

### Excluded Files:
- ❌ `__pycache__/` - Python cache
- ❌ `docs/` - Documentation (not needed for runtime)
- ❌ `build/` - Build artifacts
- ❌ `*.pyc, *.pyo` - Compiled Python files
- ❌ `check_structure.sh` - Development tools
- ❌ `verify_connection_v2.py` - Verification scripts
- ❌ `.env` - Environment files (security)
- ❌ `venv/` - Virtual environment

## Output Structure

After running `build.sh`, you'll get:
```
build/dist/
├── jd2-controller_YYYYMMDD_HHMMSS.tar.gz       # Distribution package
└── jd2-controller_YYYYMMDD_HHMMSS.tar.gz.sha256 # Checksum file
```

## Package Contents

The extracted package contains:
```
jd2-controller_*/
├── main.py
├── requirements.txt
├── jdctl
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── jdownloader/
│   ├── utils/
│   └── verification/
├── scripts/
│   ├── setup_venv.sh
│   └── run.sh
├── jd-controller-api.service
├── jdownloader.service
├── install.sh              # Auto-generated installer
├── .env.example           # Environment template
├── README.md              # Quick start guide
└── DEPLOYMENT.md          # Detailed deployment guide
```

## Deployment Workflow

1. **On build machine:**
   ```bash
   ./build.sh
   ```

2. **Transfer to target host:**
   ```bash
   scp build/dist/jd2-controller_*.tar.gz user@target-host:/tmp/
   ```

3. **On target host:**
   ```bash
   cd /opt  # or your preferred installation directory
   tar -xzf /tmp/jd2-controller_*.tar.gz
   cd jd2-controller_*
   ./install.sh
   ```

4. **Configure:**
   ```bash
   cp .env.example .env
   nano .env  # Add your credentials
   ```

5. **Test:**
   ```bash
   ./scripts/run.sh --help
   ```

6. **Install services (optional):**
   ```bash
   sudo cp *.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now jd-controller-api
   ```

## Features

- ✅ **Clean Build**: Removes all development artifacts
- ✅ **Timestamped**: Each build has unique version timestamp
- ✅ **Checksum**: SHA256 hash for integrity verification
- ✅ **Auto-installer**: Includes ready-to-run install script
- ✅ **Documentation**: Generates deployment guides automatically
- ✅ **Size Optimized**: Only essential files, no bloat

## Build Output Example

```
🔨 Building jd2-controller v20260105_143025
==================================
🧹 Cleaning previous build...
📦 Copying application files...
📦 Copying source code...
📦 Copying CLI tool...
📦 Copying service files...
📦 Copying deployment scripts...
📝 Creating deployment documentation...
📝 Creating installation script...
📝 Creating environment template...
📝 Creating README...
📦 Creating distribution package...
🔒 Generating checksum...

✅ Build complete!
==================================
📦 Package: /home/user/project/jd2-controller/build/dist/jd2-controller_20260105_143025.tar.gz
📊 Size: 42K
🔒 Checksum: /home/user/project/jd2-controller/build/dist/jd2-controller_20260105_143025.tar.gz.sha256

To deploy:
1. Copy jd2-controller_20260105_143025.tar.gz to target host
2. Extract: tar -xzf jd2-controller_20260105_143025.tar.gz
3. Run: cd jd2-controller_20260105_143025 && ./install.sh
```

## Customization

To include additional files, edit `build.sh` and add copy commands in the appropriate section:

```bash
# Copy additional files
cp "$SCRIPT_DIR/your-file.txt" "$PACKAGE_DIR/"
```

## Troubleshooting

### Build fails with "Permission denied"
```bash
chmod +x build.sh
```

### rsync not found
```bash
# Install rsync
sudo apt-get install rsync  # Debian/Ubuntu
sudo yum install rsync      # CentOS/RHEL
```

### Package too large
Check what's being included:
```bash
tar -tzf build/dist/jd2-controller_*.tar.gz | head -50
```

## Security Notes

- ❌ `.env` files are **never** included in the package
- ❌ Virtual environments are **not** packaged (created on target)
- ✅ `.env.example` is included as a template
- ✅ Checksums verify package integrity

## CI/CD Integration

The build script can be integrated into CI/CD pipelines:

```yaml
# Example GitLab CI
build:
  script:
    - ./build.sh
  artifacts:
    paths:
      - build/dist/*.tar.gz
      - build/dist/*.sha256
```
