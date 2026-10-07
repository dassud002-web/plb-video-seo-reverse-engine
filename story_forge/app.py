#!/usr/bin/env python3
"""
PLB Story Forge — Flask Application Server
===========================================
Video → Story Evidence → Story DNA → 50 Root Stories → Recursive Expansion.
Runs on port 5050 (or PORT env var) side-by-side with SEO tools.
"""

import os
import sys
import uuid
import threading
import time
from pathlib import Path
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template, send_file, Response

# Add project root to path
current_dir = Path(__file__).resolve().parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from story_forge.engine.video_story_extractor import extract_video_story_evidence, calculate_video_hash
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.story_generator import generate_50_root_stories
from story_forge.engine.expansion_engine import expand_story_node_50
from story_forge.engine.lineage_engine import build_comparison_view_data
from story_forge.storage.db import (
    init_db,
    save_session,
    save_stories_batch,
    get_session,
    list_recent_sessions,
    get_story,
    get_all_stories_for_session,
    get_lineage_graph
)
from story_forge.exports.exporter import (
    export_session_json,
    export_session_markdown,
    export_session_txt,
    build_session_zip_bundle
)

app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent / "templates"),
    static_folder=str(Path(__file__).resolve().parent / "static")
)

# Background task state
TASKS: Dict[str, Dict[str, Any]] = {}
TASKS_LOCK = threading.Lock()

# Initialize DB on start
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recent", methods=["GET"])
def get_recent():
    """Lists recent story analysis sessions and known local test videos."""
    recent_sessions = list_recent_sessions(limit=10)
    
    # Check for known test assets in the environment
    test_candidates = []
    known_paths = [
        "C:/Users/Admin/Desktop/google-project/temp_uploads/378c9d_Rabbits & Horseradish_TJX_no_watermark.mp4",
        "C:/Users/Admin/Downloads/vid/Chicken Coop Video_TJX_no_watermark.mp4",
        "C:/Users/Admin/Downloads/test-reel/test-reel.mp4",
        "C:/Users/Admin/Downloads/vid/turtle_video.mp4"
    ]
    for p in known_paths:
        path_obj = Path(p)
        if path_obj.exists():
            test_candidates.append({
                "name": path_obj.name,
                "path": str(path_obj).replace("\\", "/"),
                "size_mb": round(path_obj.stat().st_size / (1024 * 1024), 2)
            })

    return jsonify({
        "status": "ok",
        "recent_sessions": recent_sessions,
        "test_candidates": test_candidates
    })

@app.route("/api/scan", methods=["POST"])
def scan_video():
    """Fast preliminary inspection of selected video."""
    data = request.get_json() or {}
    path_str = data.get("path", "").strip()
    if not path_str:
        return jsonify({"status": "error", "error": "No file path provided"}), 400

    target = Path(path_str)
    if not target.exists():
        return jsonify({"status": "error", "error": f"File does not exist: {path_str}"}), 404

    try:
        from scripts.video_seo_reverse_engineer import extract_technical_metadata
        meta = extract_technical_metadata(target)
        return jsonify({
            "status": "ok",
            "file_info": {
                "name": target.name,
                "path": str(target).replace("\\", "/"),
                "size_bytes": target.stat().st_size,
                "size_mb": round(target.stat().st_size / (1024 * 1024), 2),
                "duration_seconds": meta.get("duration_seconds", 0.0),
                "resolution": f"{meta.get('width', '?')}x{meta.get('height', '?')}",
                "fps": meta.get("fps", 24.0),
                "codec": meta.get("codec", "unknown")
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

def _run_story_analysis(task_id: str, video_path: Path, settings: Dict[str, Any]):
    """Thread worker: analyzes video, creates DNA, generates 50 root stories."""
    try:
        def update_task(pct: int, stage: str):
            with TASKS_LOCK:
                if task_id in TASKS:
                    TASKS[task_id]["progress"] = pct
                    TASKS[task_id]["stage"] = stage

        update_task(10, "Verifying video asset and container...")
        time.sleep(0.1)

        update_task(25, "Extracting video narrative evidence & timeline milestones...")
        evidence = extract_video_story_evidence(video_path)

        update_task(60, "Synthesizing Story DNA & thematic tension...")
        story_dna = build_story_dna(evidence)

        update_task(75, "Generating 50 distinct root stories across 20 dimensions...")
        mode = settings.get("mode", "AUTO")
        threshold = float(settings.get("threshold", 0.70))
        root_stories = generate_50_root_stories(story_dna, mode=mode, threshold=threshold)

        update_task(90, "Persisting Story Bible and lineage database...")
        session_id = str(uuid.uuid4())[:8]
        save_session(session_id, evidence, story_dna, settings)
        save_stories_batch(session_id, root_stories)

        update_task(100, "Analysis complete! 50 Root Stories Ready.")
        with TASKS_LOCK:
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["session_id"] = session_id
            TASKS[task_id]["result"] = {
                "session_id": session_id,
                "story_dna": story_dna,
                "stories_count": len(root_stories),
                "evidence_items_count": len(evidence.get("evidence_items", [])),
                "video_hash": evidence.get("source_video_hash")
            }
    except Exception as e:
        with TASKS_LOCK:
            if task_id in TASKS:
                TASKS[task_id]["status"] = "error"
                TASKS[task_id]["error"] = str(e)

@app.route("/api/analyze", methods=["POST"])
def analyze_video():
    """Starts asynchronous full analysis and root story generation."""
    data = request.get_json() or {}
    path_str = data.get("path", "").strip()
    if not path_str:
        return jsonify({"status": "error", "error": "No file path provided"}), 400

    target = Path(path_str)
    if not target.exists():
        return jsonify({"status": "error", "error": f"File does not exist: {path_str}"}), 404

    settings = {
        "mode": data.get("mode", "AUTO"),
        "threshold": float(data.get("threshold", 0.70))
    }

    task_id = str(uuid.uuid4())[:8]
    with TASKS_LOCK:
        TASKS[task_id] = {
            "status": "running",
            "progress": 5,
            "stage": "Initializing Story Forge engine...",
            "target_path": str(target),
            "session_id": None,
            "result": None,
            "error": None
        }

    thread = threading.Thread(
        target=_run_story_analysis,
        args=(task_id, target, settings),
        daemon=True
    )
    thread.start()

    return jsonify({"status": "ok", "task_id": task_id})

@app.route("/api/status/<task_id>", methods=["GET"])
def get_status(task_id: str):
    """Polls progress of analysis task."""
    with TASKS_LOCK:
        task = TASKS.get(task_id)
        if not task:
            return jsonify({"status": "error", "error": "Task not found"}), 404
        return jsonify(task)

@app.route("/api/session/<session_id>", methods=["GET"])
def get_session_data(session_id: str):
    """Retrieves full session data, Story DNA, all stories, and lineage tree."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    stories = get_all_stories_for_session(session_id)
    lineage = get_lineage_graph(session_id)

    # Attach frame image web URLs for timeline frames
    v_hash = sess.get("source_video_hash")
    dna = sess.get("story_dna", {})

    return jsonify({
        "status": "ok",
        "session": sess,
        "story_dna": dna,
        "stories": stories,
        "lineage_graph": lineage,
        "total_stories": len(stories)
    })

@app.route("/api/expand", methods=["POST"])
def expand_story():
    """Expands a specific story node into 50 child stories."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "").strip()
    story_id = data.get("story_id", "").strip()
    mode = data.get("mode", "AUTO")
    threshold = float(data.get("threshold", 0.70))

    if not session_id or not story_id:
        return jsonify({"status": "error", "error": "session_id and story_id required"}), 400

    parent = get_story(session_id, story_id)
    if not parent:
        return jsonify({"status": "error", "error": f"Story node {story_id} not found"}), 404

    try:
        children = expand_story_node_50(parent, mode=mode, threshold=threshold)
        save_stories_batch(session_id, children)
        updated_lineage = get_lineage_graph(session_id)
        all_stories = get_all_stories_for_session(session_id)

        return jsonify({
            "status": "ok",
            "parent_id": story_id,
            "children_count": len(children),
            "children": children,
            "total_stories_count": len(all_stories),
            "lineage_graph": updated_lineage
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/compare/<session_id>/<story_id>", methods=["GET"])
def compare_story(session_id: str, story_id: str):
    """Compares child story with its parent node."""
    child = get_story(session_id, story_id)
    if not child:
        return jsonify({"status": "error", "error": "Story not found"}), 404

    parent_id = child.get("parent_id")
    if not parent_id or parent_id == "ROOT":
        # Compare with Root DNA
        session = get_session(session_id)
        parent = session.get("story_dna", {})
        parent["story_id"] = "ROOT"
        parent["title"] = "Source Video Story DNA"
    else:
        parent = get_story(session_id, parent_id)
        if not parent:
            return jsonify({"status": "error", "error": f"Parent node {parent_id} not found"}), 404

    compare_data = build_comparison_view_data(parent, child)
    return jsonify({"status": "ok", "comparison": compare_data})

@app.route("/api/frames/<video_hash>/<filename>", methods=["GET"])
def serve_frame(video_hash: str, filename: str):
    """Serves cached timeline keyframe images."""
    frames_dir = Path(__file__).resolve().parent / "storage" / "frames" / video_hash
    target_file = frames_dir / filename
    if not target_file.exists():
        return jsonify({"status": "error", "error": "Frame not found"}), 404
    return send_file(str(target_file), mimetype="image/jpeg")

@app.route("/api/export/<format_name>/<session_id>", methods=["GET"])
def export_file(format_name: str, session_id: str):
    """Exports session report as json, markdown, txt, or zip."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    base_name = f"story_forge_{sess.get('source_video_name', 'story')}_{session_id}"

    if format_name == "json":
        data = export_session_json(session_id)
        return Response(
            data,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={base_name}.json"}
        )
    elif format_name == "markdown":
        data = export_session_markdown(session_id)
        return Response(
            data,
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}.md"}
        )
    elif format_name == "txt":
        data = export_session_txt(session_id)
        return Response(
            data,
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}.txt"}
        )
    elif format_name == "zip":
        zip_bytes = build_session_zip_bundle(session_id)
        return Response(
            zip_bytes,
            mimetype="application/zip",
            headers={"Content-Disposition": f"attachment; filename={base_name}.zip"}
        )
    else:
        return jsonify({"status": "error", "error": f"Unsupported format: {format_name}"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"🚀 Starting PLB Story Forge on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
