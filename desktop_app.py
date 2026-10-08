#!/usr/bin/env python3
"""
PLB CREATOR STUDIO — Standalone Native Desktop Application
===========================================================
Unified Desktop Launcher combining:
- PLB Story Universe Factory (Port 5050)
- PLB Video SEO Reverse Engine (Port 5000)
- PLB Studio Desktop Hub (Port 5500)

Launches in native Chromium App Mode (frameless desktop window)
with automatic health checking and graceful multi-server shutdown.
"""

import os
import sys
import time
import argparse
import threading
import subprocess
import webbrowser
import urllib.request
from pathlib import Path
from werkzeug.serving import make_server

# Set up project root in sys.path
if getattr(sys, "frozen", False):
    project_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
else:
    project_root = Path(__file__).resolve().parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Import the 3 Flask applications
from app import app as app_seo
from story_forge.app import app as app_universe
from studio.app import studio_app

def find_chromium_browser():
    """Locates an installed Chromium-based browser to run in native App Mode."""
    candidates = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def wait_for_service(url: str, name: str, timeout: float = 10.0) -> bool:
    """Waits until a local HTTP service responds."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status < 500:
                    return True
        except Exception:
            time.sleep(0.15)
    return False

def main():
    parser = argparse.ArgumentParser(description="PLB Creator Studio — Desktop Application")
    parser.add_argument("--port", type=int, default=5500, help="Studio gateway port (default: 5500)")
    parser.add_argument("--seo-port", type=int, default=5000, help="Video SEO engine port (default: 5000)")
    parser.add_argument("--universe-port", type=int, default=5050, help="Story Universe port (default: 5050)")
    parser.add_argument("--browser", action="store_true", help="Open in standard browser instead of native app window")
    parser.add_argument("--no-gui", action="store_true", help="Start servers only without launching GUI window")
    args = parser.parse_args()

    print("=" * 72)
    print(" ⚡ PLB CREATOR STUDIO — STANDALONE DESKTOP APPLICATION")
    print("=" * 72)
    print(" [1] PLB Story Universe Factory   -> http://127.0.0.1:%d" % args.universe_port)
    print(" [2] PLB Video SEO Reverse Engine -> http://127.0.0.1:%d" % args.seo_port)
    print(" [3] PLB Unified Desktop Studio   -> http://127.0.0.1:%d" % args.port)
    print("=" * 72)

    # 1. Initialize and start backend servers in daemon threads
    try:
        server_seo = make_server("127.0.0.1", args.seo_port, app_seo, threaded=True)
        t_seo = threading.Thread(target=server_seo.serve_forever, daemon=True)
        t_seo.start()
        print("  ✓ Started Video SEO Reverse Engine on port %d" % args.seo_port)
    except Exception as e:
        print("  ! Notice on port %d: %s (service may already be running)" % (args.seo_port, e))
        server_seo = None

    try:
        server_universe = make_server("127.0.0.1", args.universe_port, app_universe, threaded=True)
        t_universe = threading.Thread(target=server_universe.serve_forever, daemon=True)
        t_universe.start()
        print("  ✓ Started Story Universe Factory on port %d" % args.universe_port)
    except Exception as e:
        print("  ! Notice on port %d: %s (service may already be running)" % (args.universe_port, e))
        server_universe = None

    try:
        server_studio = make_server("127.0.0.1", args.port, studio_app, threaded=True)
        t_studio = threading.Thread(target=server_studio.serve_forever, daemon=True)
        t_studio.start()
        print("  ✓ Started Studio Gateway Shell on port %d" % args.port)
    except Exception as e:
        print("  ! Error on port %d: %s" % (args.port, e))
        server_studio = None

    # 2. Verify readiness
    studio_url = "http://127.0.0.1:%d" % args.port
    print("\nWaiting for Studio services to initialize...")
    wait_for_service(studio_url, "Studio Hub")
    print("✓ All Studio services are active and ready!\n")

    # 3. Launch UI Window
    browser_proc = None
    if not args.no_gui:
        chromium_path = None if args.browser else find_chromium_browser()
        if chromium_path:
            profile_dir = project_root / "cache_analysis" / "desktop_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                chromium_path,
                f"--app={studio_url}",
                "--window-size=1440,920",
                f"--user-data-dir={profile_dir}",
                "--disable-features=Translate",
                "--app-id=PLBCreatorStudio"
            ]
            print(f"Launching Native Desktop Window using: {Path(chromium_path).name}...")
            browser_proc = subprocess.Popen(cmd)
        else:
            print("Opening Studio in default browser...")
            webbrowser.open(studio_url)

    # 4. Keep alive and monitor window closure
    print("PLB Creator Studio is running. Close the desktop window or press Ctrl+C to exit.\n")
    try:
        if browser_proc:
            # Wait for user to close desktop window
            browser_proc.wait()
            print("\nDesktop window closed by user.")
        else:
            # Keep alive in headless / standard browser mode
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutdown signal received (Ctrl+C).")
    finally:
        print("Shutting down application servers gracefully...")
        if server_studio:
            server_studio.shutdown()
        if server_universe:
            server_universe.shutdown()
        if server_seo:
            server_seo.shutdown()
        print("✓ PLB Creator Studio shutdown complete. Have a productive day!")

if __name__ == "__main__":
    main()
