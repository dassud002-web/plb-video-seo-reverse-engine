#!/usr/bin/env python3
"""
PLB Creator Studio — Desktop Gateway Application
=================================================
Unifies PLB Story Universe Factory (port 5050) and
PLB Video SEO Reverse Engine (port 5000) into a single desktop studio.
"""

import os
import sys
import subprocess
import webbrowser
import urllib.request
from pathlib import Path
from flask import Flask, render_template, jsonify, request

if getattr(sys, "frozen", False):
    current_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
else:
    current_dir = Path(__file__).resolve().parent.parent

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

studio_app = Flask(
    __name__,
    template_folder=str(current_dir / "studio" / "templates"),
    static_folder=str(current_dir / "studio" / "static")
)

def _is_service_online(url: str, timeout: float = 1.0) -> bool:
    """Fast check whether a service responds with HTTP status."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 500
    except Exception:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return resp.status < 500
        except Exception:
            return False

@studio_app.route("/")
def index():
    return render_template("studio.html")

@studio_app.route("/api/studio/status", methods=["GET"])
def studio_status():
    """Returns live connectivity status of the dual backend engines."""
    universe_ok = _is_service_online("http://127.0.0.1:5050/")
    seo_ok = _is_service_online("http://127.0.0.1:5000/")
    return jsonify({
        "status": "ok",
        "universe_online": universe_ok,
        "seo_online": seo_ok,
        "ports": {
            "universe": 5050,
            "seo": 5000,
            "studio": 5500
        },
        "version": "2.5.0",
        "platform": sys.platform
    })

@studio_app.route("/api/studio/open-folder", methods=["POST"])
def open_folder():
    """Opens local directory in Windows Explorer for convenient creator access."""
    data = request.get_json() or {}
    folder_type = data.get("folder", "uploads")

    target_path = current_dir
    if folder_type == "uploads":
        target_path = current_dir / "temp_uploads"
    elif folder_type == "exports":
        target_path = current_dir / "cache_analysis"
    elif folder_type == "storage":
        target_path = current_dir / "story_forge" / "storage"

    target_path.mkdir(parents=True, exist_ok=True)

    try:
        if sys.platform == "win32":
            os.startfile(str(target_path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(target_path)])
        else:
            subprocess.Popen(["xdg-open", str(target_path)])
        return jsonify({"status": "ok", "path": str(target_path)})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@studio_app.route("/api/studio/open-browser", methods=["POST"])
def open_browser():
    """Opens a target URL in the default web browser."""
    data = request.get_json() or {}
    url = data.get("url", "http://127.0.0.1:5500")
    try:
        webbrowser.open(url)
        return jsonify({"status": "ok", "url": url})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("STUDIO_PORT", 5500))
    studio_app.run(host="127.0.0.1", port=port, debug=False)
