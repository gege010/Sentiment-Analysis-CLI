#!/usr/bin/env python3
"""
Helper script to export X.com cookies from Chrome browser.
Run this script AFTER logging into X.com in Chrome.
"""
import json
import os
import sys

def export_cookies():
    """Export X.com cookies from Chrome."""
    try:
        import browser_cookie3
    except ImportError:
        print("Installing browser-cookie3...")
        os.system(f"{sys.executable} -m pip install browser-cookie3")
        import browser_cookie3

    print("Exporting cookies from Chrome...")
    print("(Make sure you're logged into X.com in Chrome first!)")
    print()

    try:
        cj = browser_cookie3.chrome(domain_name='x.com')
        cookies = list(cj)
    except Exception as e:
        print(f"Error accessing Chrome: {e}")
        print("\nIf Chrome is running, try closing it first or use --brave flag")
        return None

    if not cookies:
        print("No cookies found. Please log into X.com in Chrome first.")
        return None

    # Filter important cookies
    important_cookies = [
        'auth_token',
        'ct0',
        'guest_id',
        '_twitter_sess',
        'kdt',
        'twid',
    ]

    cookie_dict = {}
    found_cookies = []

    for c in cookies:
        if c.name in important_cookies or c.domain in ['x.com', '.x.com']:
            cookie_dict[c.name] = c.value
            found_cookies.append(c.name)

    if not cookie_dict:
        print("No X.com authentication cookies found.")
        print("Please log into X.com in Chrome first.")
        return None

    print(f"Found {len(found_cookies)} cookies:")
    for name in found_cookies:
        value = cookie_dict[name]
        preview = value[:20] + "..." if len(value) > 20 else value
        print(f"  - {name}: {preview}")

    return cookie_dict


def save_to_env(cookies: dict):
    """Save cookies to .env file."""
    env_path = '.env'

    # Read existing .env
    existing = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, _, value = line.partition('=')
                    existing[key.strip()] = value.strip()

    # Update with cookies
    for name, value in cookies.items():
        existing[f'X_COOKIE_{name.upper()}'] = value

    # Write back
    with open(env_path, 'w') as f:
        for key, value in existing.items():
            f.write(f"{key}={value}\n")

    print(f"\nCookies saved to {env_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Export X.com cookies from Chrome")
    parser.add_argument('--save', action='store_true', help='Save cookies to .env file')
    args = parser.parse_args()

    cookies = export_cookies()

    if cookies:
        if args.save:
            save_to_env(cookies)
            print("\nSetup complete! Run 'python -m src.main analyze --topic \"AI\"' to test.")
        else:
            print("\nTo save cookies to .env, run:")
            print("  python scripts/export_cookies.py --save")
    else:
        print("\nPlease log into X.com in Chrome, then run this script again.")
        sys.exit(1)


if __name__ == '__main__':
    main()
