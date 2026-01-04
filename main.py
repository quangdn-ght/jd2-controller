#!/usr/bin/env python3
"""Main entry point for JDownloader Controller"""
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main
from src.main import main

if __name__ == "__main__":
    main()
