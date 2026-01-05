# Deployment Scripts Summary

This project includes automated build and deployment scripts for easy production deployment.

## 📜 Available Scripts

### 1. `build.sh` - Build Package
Creates a production-ready deployment package with only essential files.

```bash
./build.sh
```

**Output:** `build/dist/jd2-controller_YYYYMMDD_HHMMSS.tar.gz` (~20KB)

📖 Documentation: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)

---

### 2. `oneclick_deploy.sh` - Automated Deployment ⭐
**One command to build, transfer, and install on remote host!**

```bash
./oneclick_deploy.sh
```

**What it does:**
1. ✅ Builds the latest package
2. ✅ Transfers to `fshare` host via SCP
3. ✅ Extracts and runs install on remote host

**Prerequisites:**
- SSH passwordless authentication configured
- Remote host accessible as `fshare` (or modify `REMOTE_HOST` in script)

📖 Documentation: [docs/ONECLICK_DEPLOY.md](docs/ONECLICK_DEPLOY.md)

---

## 🚀 Quick Start

### First Time Setup

1. **Configure SSH (one-time setup):**
   ```bash
   ssh-copy-id fshare
   ssh fshare "echo 'SSH OK'"
   ```

2. **Deploy with one command:**
   ```bash
   ./oneclick_deploy.sh
   ```

3. **Configure on remote host:**
   ```bash
   ssh fshare
   cd /opt/jd2-controller_*
   cp .env.example .env
   nano .env  # Add credentials
   ./scripts/run.sh
   ```

### Regular Updates

Just run:
```bash
./oneclick_deploy.sh
```

---

## 📊 Comparison

| Feature | build.sh | oneclick_deploy.sh |
|---------|----------|-------------------|
| Build package | ✅ | ✅ (automatic) |
| Transfer to remote | ❌ (manual) | ✅ |
| Install on remote | ❌ (manual) | ✅ |
| Best for | Manual deployment | Automated deployment |
| SSH required | ❌ | ✅ |

---

## 📁 Package Contents

Both scripts create packages containing:

✅ **Included:**
- Python source code (`src/`)
- Main entry point (`main.py`)
- Dependencies (`requirements.txt`)
- CLI tool (`jdctl`)
- Service files (`*.service`)
- Setup scripts (`scripts/`)
- Documentation (auto-generated)

❌ **Excluded:**
- Documentation folder (`docs/`)
- Python cache (`__pycache__/`)
- Build artifacts (`build/`)
- Virtual environment (`venv/`)
- Environment files (`.env`)
- Development tools

---

## 🔧 Configuration

### Change Remote Host
Edit `oneclick_deploy.sh`:
```bash
REMOTE_HOST="your-host-name"
```

### Change Remote Path
Edit `oneclick_deploy.sh`:
```bash
REMOTE_PATH="/your/custom/path"
```

---

## 📚 Documentation

- [BUILD_DEPLOY.md](BUILD_DEPLOY.md) - Quick reference for build and deploy
- [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) - Detailed build documentation
- [docs/ONECLICK_DEPLOY.md](docs/ONECLICK_DEPLOY.md) - One-click deploy setup guide

---

## 🎯 Workflow Examples

### Development to Production
```bash
# Develop locally
git commit -m "New features"
git push

# Deploy to production
./oneclick_deploy.sh
```

### Multiple Environments
```bash
# Deploy to staging
REMOTE_HOST=staging ./oneclick_deploy.sh

# Deploy to production
REMOTE_HOST=production ./oneclick_deploy.sh
```

### Manual Control
```bash
# Build only
./build.sh

# Transfer manually
scp build/dist/jd2-controller_*.tar.gz custom-host:/custom/path/

# Install manually
ssh custom-host
cd /custom/path
tar -xzf jd2-controller_*.tar.gz
cd jd2-controller_*
./install.sh
```

---

## ✅ Complete Deployment Example

```bash
# 1. One-click deploy
./oneclick_deploy.sh

# 2. Configure on remote (one-time)
ssh fshare
cd /opt/jd2-controller_*
cp .env.example .env
nano .env  # Add: JDOWNLOADER_EMAIL, JDOWNLOADER_PASSWORD, etc.

# 3. Install as service
sudo cp jd-controller-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now jd-controller-api

# 4. Verify
sudo systemctl status jd-controller-api
curl http://localhost:8000/health
```

---

## 🆘 Troubleshooting

### SSH Connection Issues
```bash
# Test SSH
ssh fshare "echo OK"

# Setup SSH keys
ssh-copy-id fshare
```

### Build Fails
```bash
# Check build script
./build.sh
# Check for errors in output
```

### Remote Installation Fails
```bash
# Connect and debug
ssh fshare
cd /opt/jd2-controller_*
./install.sh  # Run manually to see errors
```

See individual documentation files for more detailed troubleshooting.
