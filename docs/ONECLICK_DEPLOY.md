# One-Click Deploy Script

## Overview
The `oneclick_deploy.sh` script automates the complete deployment workflow: build → transfer → install.

## Prerequisites

### 1. SSH Configuration
Ensure SSH is configured for passwordless authentication to the target host:

```bash
# Test SSH connection
ssh fshare "echo 'Connection OK'"
```

If you need to set up SSH keys:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519

# Copy key to remote host
ssh-copy-id fshare

# Test passwordless login
ssh fshare
```

### 2. SSH Config (Optional but Recommended)
Add to `~/.ssh/config`:
```
Host fshare
    HostName your-server-ip-or-domain
    User your-username
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

### 3. Remote Host Requirements
- Remote path `/opt` must be writable by your user OR
- Modify `REMOTE_PATH` variable in the script to use a different location

## Usage

### Basic Usage
```bash
./oneclick_deploy.sh
```

That's it! The script will:
1. ✅ Build the latest package
2. ✅ Transfer to remote host
3. ✅ Extract and install automatically

### What It Does

#### Step 1: Build Package
- Runs `./build.sh`
- Creates timestamped package in `build/dist/`

#### Step 2: Transfer to Remote
- Finds the latest `.tar.gz` package
- Tests SSH connection
- Transfers package via SCP to `fshare:/opt/`

#### Step 3: Install on Remote
- Connects via SSH
- Extracts the package
- Runs `install.sh` automatically
- Sets up virtual environment
- Configures permissions

## Configuration

Edit these variables at the top of the script if needed:

```bash
REMOTE_HOST="fshare"      # SSH host name or IP
REMOTE_PATH="/opt"        # Installation directory on remote host
```

## Output Example

```
╔════════════════════════════════════════════╗
║  JDownloader Controller - One-Click Deploy ║
╚════════════════════════════════════════════╝

[1/3] Building package...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔨 Building jd2-controller v20260105_180740
...
✅ Build complete!

[2/3] Transferring to fshare...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Package: jd2-controller_20260105_180740.tar.gz
🎯 Target: fshare:/opt

Testing SSH connection...
✓ SSH connection successful

Transferring package...
✓ Package transferred successfully

[3/3] Installing on fshare...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Navigating to /opt...
📦 Extracting package...
🔧 Running installation...
🚀 Installing JDownloader Controller...
...
✅ Installation complete!

╔════════════════════════════════════════════╗
║          ✓ Deployment Successful!          ║
╚════════════════════════════════════════════╝

🎯 Target host: fshare
📍 Install path: /opt/jd2-controller_20260105_180740

To connect and configure:
  ssh fshare
  cd /opt/jd2-controller_20260105_180740
  nano .env
```

## Post-Deployment Steps

After successful deployment, connect to the remote host:

```bash
ssh fshare
cd /opt/jd2-controller_*
```

### 1. Configure Environment
```bash
cp .env.example .env
nano .env
```

Add your credentials:
```env
JDOWNLOADER_EMAIL=your_email@example.com
JDOWNLOADER_PASSWORD=your_password
JDOWNLOADER_DEVICE_NAME=your_device_name
```

### 2. Test the Installation
```bash
./scripts/run.sh --help
./jdctl --help
```

### 3. Install as Systemd Service
```bash
sudo cp jd-controller-api.service /etc/systemd/system/
sudo cp jdownloader.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now jd-controller-api
sudo systemctl status jd-controller-api
```

## Troubleshooting

### SSH Connection Failed
```bash
# Test connection
ssh -v fshare

# Check SSH config
cat ~/.ssh/config

# Verify SSH keys
ls -la ~/.ssh/
```

### Permission Denied on /opt
Change the remote path in the script:
```bash
# Edit oneclick_deploy.sh
REMOTE_PATH="/home/yourusername/apps"
```

Or create the directory on remote host:
```bash
ssh fshare "sudo mkdir -p /opt && sudo chown $USER:$USER /opt"
```

### Build Failed
```bash
# Run build manually to see errors
./build.sh
```

### Transfer Failed
```bash
# Test SCP manually
scp build/dist/jd2-controller_*.tar.gz fshare:/tmp/
```

### Installation Failed on Remote
```bash
# Connect and install manually
ssh fshare
cd /opt
tar -xzf jd2-controller_*.tar.gz
cd jd2-controller_*
./install.sh
```

## Multiple Remote Hosts

To deploy to multiple hosts, you can:

### Option 1: Run Multiple Times
```bash
# Edit script and change REMOTE_HOST
./oneclick_deploy.sh  # deploys to host1

# Edit again
./oneclick_deploy.sh  # deploys to host2
```

### Option 2: Pass Host as Argument
Modify the script to accept host as argument:
```bash
REMOTE_HOST="${1:-fshare}"
```

Then use:
```bash
./oneclick_deploy.sh server1
./oneclick_deploy.sh server2
```

## Advanced Usage

### Deploy to Custom Path
```bash
# Edit oneclick_deploy.sh
REMOTE_PATH="/home/user/applications"
```

### Deploy to Different User
In `~/.ssh/config`:
```
Host fshare
    HostName server.example.com
    User deployuser
```

### Using Non-Standard SSH Port
In `~/.ssh/config`:
```
Host fshare
    HostName server.example.com
    Port 2222
```

## Security Notes

- ✅ Uses SSH key authentication (no passwords)
- ✅ `.env` files are NOT transferred (security)
- ✅ Package integrity verified with SHA256
- ⚠️ Ensure SSH keys are properly secured (chmod 600 ~/.ssh/id_*)

## Integration with CI/CD

Example GitLab CI:
```yaml
deploy:
  stage: deploy
  script:
    - ./oneclick_deploy.sh
  only:
    - main
```

Example GitHub Actions:
```yaml
- name: Deploy
  run: |
    eval $(ssh-agent)
    ssh-add - <<< "${{ secrets.SSH_PRIVATE_KEY }}"
    ./oneclick_deploy.sh
```
