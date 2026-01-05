# Quick Build & Deploy Reference

## 🚀 One-Click Deploy (Fastest) - RECOMMENDED

**Automated build, transfer, install, and start services:**
```bash
./oneclick_deploy.sh --remote=fshare
```

**Or with IP address:**
```bash
./oneclick_deploy.sh remote=10.168.1.104
```

This will automatically:
1. ✅ Build the package
2. ✅ Transfer to remote host
3. ✅ Extract and install to `/opt/jd2-controller/current`
4. ✅ Copy .env configuration (if exists)
5. ✅ Install and start systemd services

**Requirements:** 
- SSH passwordless authentication to remote host
- Sudo access on remote host (for /opt and systemd)

**Result:**
- Services auto-started and enabled
- API accessible at `http://remote-host:8001`
- Install location: `/opt/jd2-controller/current`

📖 See [docs/ONECLICK_DEPLOY.md](docs/ONECLICK_DEPLOY.md) for detailed setup

---

## Manual Build & Deploy

### Build the Package

```bash
./build.sh
```

**Output:** `build/dist/jd2-controller_YYYYMMDD_HHMMSS.tar.gz`

## Deploy to Another Host

### 1. Transfer Package
```bash
# Using SCP
scp build/dist/jd2-controller_*.tar.gz user@remote-host:/opt/

# Or using rsync
rsync -avz build/dist/jd2-controller_*.tar.gz user@remote-host:/opt/
```

### 2. On Remote Host
```bash
cd /opt
tar -xzf jd2-controller_*.tar.gz
cd jd2-controller_*
./install.sh
```

### 3. Configure
```bash
cp .env.example .env
nano .env  # Add credentials
```

### 4. Run
```bash
# Test run
./scripts/run.sh --help

# Or install as service
sudo cp jd-controller-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now jd-controller-api
```

## What's Included in Package

✅ **Included:**
- Python source code (src/)
- Main entry point (main.py)
- Dependencies list (requirements.txt)
- CLI tool (jdctl)
- Service files (*.service)
- Setup scripts (scripts/)
- Auto-generated docs (README.md, DEPLOYMENT.md)
- Environment template (.env.example)
- Installation script (install.sh)

❌ **Excluded:**
- Documentation folder (docs/)
- Python cache (__pycache__/)
- Build artifacts (build/)
- Virtual environment (venv/)
- Environment files (.env)
- Development tools
- Test files

## Package Info

- **Size:** ~20KB (without dependencies)
- **Format:** tar.gz with SHA256 checksum
- **Platform:** Linux (systemd-based)
- **Python:** 3.8+ required

## Verify Package Integrity

```bash
cd build/dist
sha256sum -c jd2-controller_*.tar.gz.sha256
```

## Full Deployment Example

```bash
# On BUILD machine
./build.sh

# Transfer to PRODUCTION machine
scp build/dist/jd2-controller_20260105_180740.tar.gz prod-server:/opt/

# On PRODUCTION machine
ssh prod-server
cd /opt
tar -xzf jd2-controller_20260105_180740.tar.gz
cd jd2-controller_20260105_180740
./install.sh
cp .env.example .env
nano .env  # Configure
./scripts/run.sh  # Test
sudo cp jd-controller-api.service /etc/systemd/system/
sudo systemctl enable --now jd-controller-api
```

---

For detailed documentation, see [BUILD_GUIDE.md](BUILD_GUIDE.md)
