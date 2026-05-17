#!/usr/bin/env python3
"""
Helper script to export X.com cookies from Chrome browser.
Run this script AFTER logging into X.com in Chrome.
"""
import sys
import os
from pathlib import Path

# Add project root to python path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.cookie_manager import auto_fetch_cookies, save_cookies_to_env

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Export X.com cookies from Chrome")
    parser.add_argument('--save', action='store_true', help='Save cookies to .env file')
    args = parser.parse_args()

    print("==================================================")
    print("X.com Cookie Exporter")
    print("==================================================")
    print("Pastikan Anda sudah login ke X.com di Chrome.")
    print("Jika di Windows, Anda mungkin harus MENUTUP (Close) semua jendela Chrome terlebih dahulu.\n")

    cookies = auto_fetch_cookies(quiet=False)

    if cookies:
        if args.save:
            save_cookies_to_env(cookies)
            print("\nSetup complete! Run 'python -m src.main analyze' to test.")
        else:
            print("\nTo save cookies to .env, run:")
            print("  python scripts/export_cookies.py --save")
    else:
        print("\n[ERROR] Silakan tutup Chrome, login ke X.com, dan jalankan script ini lagi.")
        sys.exit(1)

if __name__ == '__main__':
    main()
