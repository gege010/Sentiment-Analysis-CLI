import os
import sys
from pathlib import Path

def auto_fetch_cookies(quiet=False):
    """Attempt to fetch X.com cookies from multiple browsers."""
    try:
        import browser_cookie3
    except ImportError:
        if not quiet:
            print("Installing browser-cookie3...")
        os.system(f"{sys.executable} -m pip install browser-cookie3{' >nul 2>&1' if quiet else ''}")
        try:
            import browser_cookie3
        except ImportError:
            return None

    if not quiet:
        print("Mencoba mengambil cookies terbaru dari Browser (Chrome/Edge/Firefox/Brave)...")

    cookies = []
    
    # Try multiple browsers and domains
    browsers = [
        ("Chrome", browser_cookie3.chrome),
        ("Edge", browser_cookie3.edge),
        ("Firefox", browser_cookie3.firefox),
        ("Brave", browser_cookie3.brave),
        ("Opera", browser_cookie3.opera)
    ]
    
    domains = ['.x.com', '.twitter.com', 'x.com', 'twitter.com']

    for browser_name, browser_func in browsers:
        for domain in domains:
            try:
                cj = browser_func(domain_name=domain)
                cookies.extend(list(cj))
            except Exception as e:
                # Silently catch all exceptions (locked DBs, Admin required, not installed, etc.)
                pass

    if not cookies:
        if not quiet:
            print()
            print("=========================================================================")
            print("[INFO] Autentikasi Otomatis Gagal. Harap gunakan cara MANUAL.")
            print("=========================================================================")
            print("Alasan ini terjadi:")
            print("1. Anda menggunakan profil Chrome selain 'Default' (misal: Profile 1).")
            print("2. Browser sedang aktif/terkunci di background (Edge WebView dll).")
            print("3. Windows memblokir Python membaca database karena izin Administrator.")
            print()
            print("👉 CARA MANUAL (100% Berhasil):")
            print("1. Buka X.com di browser tempat Anda login.")
            print("2. Tekan tombol F12 (Developer Tools) -> Pilih tab 'Application'.")
            print("3. Di sebelah kiri, buka 'Storage' -> 'Cookies' -> 'https://x.com'.")
            print("4. Copy nilai dari 'auth_token', 'ct0', dan 'guest_id'.")
            print("5. Paste nilai-nilai tersebut ke file '.env' di folder proyek ini.")
            print("=========================================================================\n")
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
        if c.name in important_cookies or c.domain in domains:
            cookie_dict[c.name] = c.value
            if c.name not in found_cookies:
                found_cookies.append(c.name)

    if not cookie_dict:
        if not quiet:
            print("\n[INFO] Cookie X.com tidak ditemukan di profil Default browser Anda.")
            print("Jika Anda menggunakan profil Chrome lain, gunakan CARA MANUAL (F12) untuk copy cookie ke .env\n")
        return None

    if not quiet:
        print(f"✓ Berhasil mendapatkan {len(found_cookies)} cookies fresh dari Browser!")
    
    return cookie_dict

def save_cookies_to_env(cookies: dict):
    """Save cookies dict to .env file."""
    env_path = Path(__file__).parent.parent.parent / '.env'

    existing = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, _, value = line.partition('=')
                    existing[key.strip()] = value.strip()

    # Update with cookies
    for name, value in cookies.items():
        existing[f'X_COOKIE_{name.upper()}'] = value

    with open(env_path, 'w') as f:
        for key, value in existing.items():
            f.write(f"{key}={value}\n")
