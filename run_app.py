#!/usr/bin/env python3
"""
PLB VIDEO SEO REVERSE ENGINE - Desktop Launcher
================================================
Launches the local Flask server and automatically opens the user's default
web browser to http://127.0.0.1:5000.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
import socket
import webbrowser
import threading
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app

def find_available_port(start_port=5000, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def open_browser(port):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[LAUNCHER] Opening browser at: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[LAUNCHER] Note: Could not auto-open browser: {e}")
        print(f"[LAUNCHER] Please open {url} manually in your web browser.")

def main():
    port = find_available_port(5000)
    print("=" * 65)
    print(" ⚡ PLB VIDEO SEO REVERSE ENGINE - Desktop Application")
    print(f" Web Interface: http://127.0.0.1:{port}")
    print(" Non-Destructive Forensic Video Analysis & SEO Reconstruction")
    print("=" * 65)
    
    # Launch browser in background thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    
    # Run server
    app.run(host="127.0.0.1", port=port, debug=False)

if __name__ == "__main__":
    main()
