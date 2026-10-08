#!/usr/bin/env python3
"""
PLB VIDEO SEO REVERSE ENGINE - Creator Web & Desktop Application Server
========================================================================
Repository: https://github.com/dassud002-web/plb-video-seo-reverse-engine
File: app.py
"""

import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import json
import uuid
import zipfile
import tempfile
import threading
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file, Response

# Add scripts directory to path to import reverse engineering engine
if getattr(sys, "frozen", False):
    current_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_base_dir = Path(sys.executable).resolve().parent
else:
    current_dir = Path(__file__).resolve().parent
    app_base_dir = current_dir

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scripts.video_seo_reverse_engineer import (
    run_full_analysis,
    extract_technical_metadata,
    locate_source_files
)

app = Flask(
    __name__,
    template_folder=str(current_dir / "templates"),
    static_folder=str(current_dir / "static")
)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB max upload

# State tracking for asynchronous analysis tasks
TASKS = {}
UPLOAD_DIR = app_base_dir / "temp_uploads"
CACHE_DIR = app_base_dir / "cache_analysis"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recent", methods=["GET"])
def get_recent_candidates():
    """Scan common local directories for candidate video files to enable 1-click testing."""
    candidates = []
    
    # 1. Check local repo input folder
    local_input = current_dir / "input" / "target.mp4"
    if local_input.exists():
        candidates.append({
            "name": "Local Repo Target (input/target.mp4)",
            "path": str(local_input.resolve()).replace("\\", "/"),
            "size_mb": round(local_input.stat().st_size / (1024 * 1024), 2)
        })
        
    # 2. Check Downloads test-reel
    user_home = Path.home()
    test_reel = user_home / "Downloads" / "test-reel" / "test-reel.mp4"
    if test_reel.exists():
        candidates.append({
            "name": "Active Investigation Target (Downloads/test-reel/test-reel.mp4)",
            "path": str(test_reel.resolve()).replace("\\", "/"),
            "size_mb": round(test_reel.stat().st_size / (1024 * 1024), 2)
        })
        
    # 3. Check Downloads/vid
    vid_folder = user_home / "Downloads" / "vid"
    if vid_folder.exists():
        for mp4 in vid_folder.glob("*.mp4"):
            candidates.append({
                "name": f"Downloads/vid/{mp4.name}",
                "path": str(mp4.resolve()).replace("\\", "/"),
                "size_mb": round(mp4.stat().st_size / (1024 * 1024), 2)
            })
            if len(candidates) >= 5:
                break
                
    return jsonify({"candidates": candidates})

@app.route("/api/scan", methods=["POST"])
def scan_video():
    """Quickly scan a local or uploaded file and return technical summary and discovered sidecars."""
    file_path_str = None
    
    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":
            safe_name = f"{uuid.uuid4().hex[:6]}_{uploaded_file.filename}"
            save_path = UPLOAD_DIR / safe_name
            uploaded_file.save(str(save_path))
            file_path_str = str(save_path.resolve())
    elif request.is_json:
        data = request.get_json() or {}
        file_path_str = data.get("path")
    else:
        file_path_str = request.form.get("path")
        
    if not file_path_str:
        return jsonify({"error": "No video file or path provided"}), 400
        
    vpath = Path(file_path_str)
    if not vpath.exists():
        return jsonify({"error": f"Target file not found at: {file_path_str}"}), 404
        
    try:
        tech_meta = extract_technical_metadata(vpath)
        source_ev = locate_source_files(vpath)
        
        v_stream = next((s for s in tech_meta.get("streams", []) if s.get("type") == "video"), {})
        
        return jsonify({
            "status": "ok",
            "file_info": {
                "path": str(vpath.resolve()).replace("\\", "/"),
                "filename": vpath.name,
                "size_mb": tech_meta.get("file_size_mb"),
                "size_bytes": tech_meta.get("file_size_bytes"),
                "duration_seconds": tech_meta.get("duration_seconds"),
                "format": tech_meta.get("format_name"),
                "codec": v_stream.get("codec") or "Unknown",
                "resolution": f"{v_stream.get('width', '?')}x{v_stream.get('height', '?')}",
                "fps": v_stream.get("fps") or 24.0
            },
            "sidecars_found": [Path(f).name for f in source_ev.get("found_files", [])]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scan video: {str(e)}"}), 500

@app.route("/api/analyze", methods=["POST"])
def start_analysis():
    """Trigger background forensic reverse-engineering analysis."""
    data = request.get_json() or {}
    path_str = data.get("path")
    
    if not path_str:
        return jsonify({"error": "Path parameter is required"}), 400
        
    vpath = Path(path_str)
    if not vpath.exists():
        return jsonify({"error": f"File does not exist: {path_str}"}), 404
        
    task_id = uuid.uuid4().hex[:8]
    task_dir = CACHE_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = task_dir / "frames"
    report_file = task_dir / "VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md"
    
    TASKS[task_id] = {
        "id": task_id,
        "status": "running",
        "progress": 5,
        "stage": "Initializing forensic analysis...",
        "task_dir": str(task_dir),
        "report_file": str(report_file),
        "result": None,
        "error": None
    }
    
    def run_worker():
        try:
            def on_progress(pct, stage_name):
                if task_id in TASKS:
                    TASKS[task_id]["progress"] = pct
                    TASKS[task_id]["stage"] = stage_name
                    
            res = run_full_analysis(
                video_path=vpath,
                output_report_path=report_file,
                frames_dir=frames_dir,
                progress_callback=on_progress
            )
            
            # Map frames relative to endpoint
            for f in res.get("timeline_frames", []):
                f["url"] = f"/api/frames/{task_id}/{f['filename']}"
            if "visual_intelligence" in res and "evidence_frames" in res["visual_intelligence"]:
                for f in res["visual_intelligence"]["evidence_frames"]:
                    f["url"] = f"/api/frames/{task_id}/{f['filename']}"
                
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["progress"] = 100
            TASKS[task_id]["stage"] = "Analysis complete!"
            TASKS[task_id]["result"] = res
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            if task_id in TASKS:
                TASKS[task_id]["status"] = "error"
                TASKS[task_id]["error"] = str(e)
                TASKS[task_id]["stage"] = f"Failed: {str(e)}"
                
    thread = threading.Thread(target=run_worker, daemon=True)
    thread.start()
    
    return jsonify({"task_id": task_id, "status": "running"})

@app.route("/api/status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    """Poll progress and fetch completed analysis payload."""
    if task_id not in TASKS:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(TASKS[task_id])

@app.route("/api/frames/<task_id>/<filename>", methods=["GET"])
def get_frame_image(task_id, filename):
    """Serve extracted timeline frames."""
    if task_id not in TASKS:
        return "Task not found", 404
    frame_path = Path(TASKS[task_id]["task_dir"]) / "frames" / filename
    if not frame_path.exists():
        return "Frame not found", 404
    return send_file(frame_path, mimetype="image/jpeg")

@app.route("/api/export/markdown/<task_id>", methods=["GET"])
def export_markdown(task_id):
    """Download VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md."""
    if task_id not in TASKS or not TASKS[task_id].get("report_file"):
        return "Report not found", 404
    rpath = Path(TASKS[task_id]["report_file"])
    if not rpath.exists():
        return "Report file does not exist", 404
    return send_file(
        rpath,
        as_attachment=True,
        download_name="VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md",
        mimetype="text/markdown"
    )

@app.route("/api/export/json/<task_id>", methods=["GET"])
def export_json(task_id):
    """Download analysis data as JSON."""
    if task_id not in TASKS or not TASKS[task_id].get("result"):
        return "Data not found", 404
    result_data = TASKS[task_id]["result"]
    json_bytes = json.dumps(result_data, indent=2).encode("utf-8")
    return Response(
        json_bytes,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename=video_seo_analysis_{task_id}.json"}
    )

@app.route("/api/export/zip/<task_id>", methods=["GET"])
def export_zip(task_id):
    """Export complete evidence package as a zip archive."""
    if task_id not in TASKS or not TASKS[task_id].get("result"):
        return "Data not found", 404
        
    task_dir = Path(TASKS[task_id]["task_dir"])
    zip_path = task_dir / f"video_seo_evidence_bundle_{task_id}.zip"
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        # Add markdown report
        rpath = Path(TASKS[task_id]["report_file"])
        if rpath.exists():
            z.write(rpath, arcname="VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md")
            
        # Add JSON
        z.writestr("analysis_data.json", json.dumps(TASKS[task_id]["result"], indent=2))
        
        # Add frames
        frames_dir = task_dir / "frames"
        if frames_dir.exists():
            for f in frames_dir.glob("*.jpg"):
                z.write(f, arcname=f"frames/{f.name}")
                
    return send_file(
        zip_path,
        as_attachment=True,
        download_name=f"video_seo_evidence_bundle_{task_id}.zip",
        mimetype="application/zip"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f" PLB VIDEO SEO REVERSE ENGINE - Server Initialized")
    print(f" Local Web Interface: http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host="127.0.0.1", port=port, debug=False)
