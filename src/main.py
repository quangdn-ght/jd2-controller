#!/usr/bin/env python3
"""
JDownloader Controller - Main Entry Point
Supports development mode with auto-reload and production mode
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def start_api(dev_mode=False, host="0.0.0.0", port=8001):
    """Start FastAPI server"""
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get settings from environment
    api_host = os.getenv("API_HOST", host)
    api_port = int(os.getenv("API_PORT", port))
    
    print("=" * 70)
    print("JDownloader Controller API Server".center(70))
    print("=" * 70)
    print(f"\n🚀 Starting API server...")
    print(f"📍 URL: http://{api_host}:{api_port}")
    print(f"📖 Docs: http://{api_host}:{api_port}/docs")
    print(f"🔄 Mode: {'DEVELOPMENT (auto-reload)' if dev_mode else 'PRODUCTION'}")
    
    if dev_mode:
        print(f"👀 Watching files for changes...")
        print(f"💡 Press Ctrl+C to stop\n")
    
    # Start uvicorn
    uvicorn.run(
        "src.api.api:app",
        host=api_host,
        port=api_port,
        reload=dev_mode,
        reload_dirs=[str(project_root)] if dev_mode else None,
        reload_includes=["*.py"] if dev_mode else None,
        log_level="info" if dev_mode else "warning"
    )


def run_cli_command(command, *args):
    """Run jdctl command"""
    jdctl_path = project_root / "jdctl"
    
    if not jdctl_path.exists():
        print(f"❌ Error: jdctl not found at {jdctl_path}")
        sys.exit(1)
    
    cmd = [str(jdctl_path), command] + list(args)
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def start_headless():
    """Start JDownloader in headless mode with verification"""
    script_path = project_root / "scripts" / "start_headless.sh"
    
    if not script_path.exists():
        print(f"❌ Error: start_headless.sh not found at {script_path}")
        sys.exit(1)
    
    result = subprocess.run(["bash", str(script_path)])
    sys.exit(result.returncode)


def show_status():
    """Show comprehensive status"""
    print("\n" + "=" * 70)
    print("JDownloader Controller Status".center(70))
    print("=" * 70 + "\n")
    
    # Check JDownloader status
    print("📦 JDownloader Service:")
    result = subprocess.run(
        ["pgrep", "-f", "JDownloader.jar"],
        capture_output=True
    )
    
    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"   ✅ Running (PIDs: {', '.join(pids)})")
    else:
        print(f"   ❌ Not running")
    
    # Check API status
    print("\n🌐 API Server:")
    result = subprocess.run(
        ["pgrep", "-f", "python.*api.py"],
        capture_output=True
    )
    
    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"   ✅ Running (PIDs: {', '.join(pids)})")
        
        # Try to get API port
        from dotenv import load_dotenv
        load_dotenv()
        api_port = os.getenv("API_PORT", "8001")
        print(f"   📍 URL: http://localhost:{api_port}/docs")
    else:
        print(f"   ❌ Not running")
    
    # Check cloud connection
    print("\n☁️  Cloud Connection:")
    verify_script = project_root / "src" / "verification" / "verify_connection_v2.py"
    venv_python = project_root / "venv" / "bin" / "python"
    
    if verify_script.exists() and venv_python.exists():
        result = subprocess.run(
            [str(venv_python), str(verify_script)],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract device name from output
            output = result.stdout.decode()
            if "SUCCESS" in output:
                print(f"   ✅ Connected to MyJDownloader cloud")
                if "JDownloader@" in output:
                    import re
                    match = re.search(r'Name:\s+(\S+)', output)
                    if match:
                        print(f"   📱 Device: {match.group(1)}")
            else:
                print(f"   ⚠️  Cloud status uncertain")
        else:
            print(f"   ❌ Not connected")
    else:
        print(f"   ⚠️  Cannot verify (missing scripts)")
    
    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="JDownloader Controller - Main Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start API in development mode (auto-reload)
  python main.py --dev
  python main.py api --dev
  
  # Start API in production mode
  python main.py --prod
  python main.py api --prod
  
  # Start JDownloader headless with verification
  python main.py start
  python main.py headless
  
  # Run CLI commands
  python main.py cli status
  python main.py cli verify
  python main.py cli logs
  
  # Show comprehensive status
  python main.py status
  
  # Custom API host/port
  python main.py api --dev --host 127.0.0.1 --port 8080
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='api',
        choices=['api', 'start', 'headless', 'cli', 'status'],
        help='Command to execute (default: api)'
    )
    
    parser.add_argument(
        'subcommand',
        nargs='?',
        help='Subcommand for cli (e.g., status, verify, start, stop)'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run API in development mode with auto-reload'
    )
    
    parser.add_argument(
        '--prod',
        action='store_true',
        help='Run API in production mode (no auto-reload)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API server host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8001,
        help='API server port (default: 8001)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'api':
            # Determine dev mode
            dev_mode = args.dev or (not args.prod and os.getenv("API_RELOAD", "").lower() == "true")
            start_api(dev_mode=dev_mode, host=args.host, port=args.port)
        
        elif args.command in ['start', 'headless']:
            start_headless()
        
        elif args.command == 'cli':
            if not args.subcommand:
                print("❌ Error: CLI command requires a subcommand")
                print("   Available: start, stop, restart, status, verify, logs")
                sys.exit(1)
            run_cli_command(args.subcommand)
        
        elif args.command == 'status':
            show_status()
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
