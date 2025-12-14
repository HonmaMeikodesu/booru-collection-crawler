#!/usr/bin/env python3
"""
Tsundora Scraper Entry Point
Convenience wrapper for tsundora_scraper.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tsundora_scraper import main

if __name__ == '__main__':
    main()
