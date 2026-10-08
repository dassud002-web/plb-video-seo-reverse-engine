#!/usr/bin/env python3
"""
PLB Story Universe Factory — Flask Application Server
=====================================================
VIDEO -> STORY DNA -> CHARACTER UNIVERSE -> RELATIONSHIP UNIVERSE ->
STORY GENOME -> CREATIVE MUTATION -> DIVERSITY FIREWALL ->
STORY UNIVERSE (100 / 300 / 500 / 1000+) -> AUTO-GROW ->
STORY SELECTION -> PRODUCTION PIPELINE.

Runs on port 5050 (or PORT env var) side-by-side with SEO tools.
"""

import os
import sys
import re
import uuid
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template, send_file, Response

# Add project root to path
if getattr(sys, "frozen", False):
    current_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    app_base_dir = Path(sys.executable).resolve().parent
else:
    current_dir = Path(__file__).resolve().parent.parent
    app_base_dir = current_dir

if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from story_forge.engine.video_story_extractor import extract_video_story_evidence, calculate_video_hash
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.story_generator import generate_50_root_stories
from story_forge.engine.expansion_engine import expand_story_node_50
from story_forge.engine.lineage_engine import build_comparison_view_data
from story_forge.engine.character_universe import extract_canon_characters, build_character_universe
from story_forge.engine.universe_engine import generate_story_universe
from story_forge.engine.production_pipeline import produce_story_package
from story_forge.engine.quality_engine import rank_story_universe, score_story_quality
from story_forge.engine.story_worlds import get_all_story_worlds
from story_forge.storage.db import (
    init_db,
    save_session,
    save_stories_batch,
    get_session,
    list_recent_sessions,
    get_story,
    get_all_stories_for_session,
    get_lineage_graph,
    save_production_package,
    get_production_package
)
from story_forge.exports.exporter import (
    export_universe_json,
    export_story_bible_markdown,
    export_character_bible_markdown,
    export_relationship_graph_markdown,
    export_top_stories_csv,
    build_full_universe_zip_bundle,
    export_session_json,
    export_session_markdown,
    export_session_txt,
    build_session_zip_bundle
)

app = Flask(
    __name__,
    template_folder=str(current_dir / "story_forge" / "templates"),
    static_folder=str(current_dir / "story_forge" / "static")
)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB max upload

UPLOAD_DIR = app_base_dir / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm"}

# Background task state
TASKS: Dict[str, Dict[str, Any]] = {}
TASKS_LOCK = threading.Lock()

# Initialize DB on start
init_db()

def cleanup_stale_uploads(ttl_hours: float = 24.0, upload_dir: Path = UPLOAD_DIR) -> int:
    """Cleans up temporary uploads older than ttl_hours, skipping files currently in active tasks."""
    removed_count = 0
    now = time.time()
    cutoff = now - (ttl_hours * 3600.0)

    active_paths = set()
    with TASKS_LOCK:
        for t in TASKS.values():
            if t.get("status") == "running" and t.get("target_path"):
                try:
                    active_paths.add(str(Path(t["target_path"]).resolve()).lower())
                except Exception:
                    pass

    try:
        recent = list_recent_sessions(limit=25)
        for s in recent:
            p = s.get("source_video_path")
            if p:
                try:
                    active_paths.add(str(Path(p).resolve()).lower())
                except Exception:
                    pass
    except Exception:
        pass

    if not upload_dir.exists():
        return 0

    for item in upload_dir.iterdir():
        if item.is_file():
            try:
                resolved = str(item.resolve()).lower()
                if resolved in active_paths:
                    continue
                if item.stat().st_mtime < cutoff:
                    item.unlink(missing_ok=True)
                    removed_count += 1
            except Exception:
                pass
    return removed_count

@app.route("/api/upload", methods=["POST"])
def upload_video():
    """
    Accepts video files via multipart/form-data upload.
    Validates extension (.mp4, .mov, .webm).
    Generates safe unique server filename in temp_uploads/.
    Preserves full original filename (including Unicode) as metadata.
    """
    try:
        cleanup_stale_uploads(ttl_hours=24.0)
    except Exception:
        pass

    if "file" not in request.files:
        return jsonify({"status": "error", "error": "No file field found in request"}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"status": "error", "error": "No file selected or empty filename"}), 400

    raw_filename = uploaded_file.filename
    # Sanitize away any client-side directory components (prevents path traversal in filename)
    original_name = Path(raw_filename).name.strip()
    if not original_name:
        return jsonify({"status": "error", "error": "Invalid filename"}), 400

    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "status": "error",
            "error": f"Unsupported extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400

    # Validate MIME type if provided and not generic binary
    mime = uploaded_file.content_type or ""
    if mime and not (mime.startswith("video/") or mime in {"application/octet-stream", "application/x-matroska"}):
        return jsonify({
            "status": "error",
            "error": f"Unsupported MIME type '{mime}'. Must be a video file."
        }), 400

    upload_id = uuid.uuid4().hex
    stem = Path(original_name).stem
    clean_stem = re.sub(r'[^a-zA-Z0-9_\.-]', '_', stem)[:40].strip('_')
    if not clean_stem:
        clean_stem = "video"
    safe_filename = f"{upload_id[:12]}_{clean_stem}{ext}"

    dest_path = (UPLOAD_DIR / safe_filename).resolve()
    try:
        dest_path.relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        return jsonify({"status": "error", "error": "Path traversal detected"}), 400

    try:
        uploaded_file.save(str(dest_path))
        size_bytes = dest_path.stat().st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)

        return jsonify({
            "status": "ok",
            "upload_id": upload_id,
            "original_name": original_name,
            "path": str(dest_path).replace("\\", "/"),
            "size_mb": size_mb,
            "extension": ext
        })
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to save uploaded file: {str(e)}"}), 500

@app.route("/api/cleanup", methods=["POST"])
def cleanup_uploads():
    """Manual trigger for cleaning up stale uploads."""
    data = request.get_json() or {}
    ttl_hours = float(data.get("ttl_hours", 24.0))
    cleaned = cleanup_stale_uploads(ttl_hours=ttl_hours)
    return jsonify({"status": "ok", "cleaned_files": cleaned})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recent", methods=["GET"])
def get_recent():
    """Lists recent story analysis sessions and known local test videos."""
    recent_sessions = list_recent_sessions(limit=15)
    
    # Check for known test assets in the environment
    test_candidates = []
    known_paths = [
        "C:/Users/Admin/Desktop/google-project/temp_uploads/378c9d_Rabbits & Horseradish_TJX_no_watermark.mp4",
        "C:/Users/Admin/Downloads/vid/Chicken Coop Video_TJX_no_watermark.mp4",
        "C:/Users/Admin/Downloads/test-reel/test-reel.mp4",
        "C:/Users/Admin/Downloads/vid/Turtles Eating Grapefruit_TJX_no_watermark.mp4",
        "C:/Users/Admin/Desktop/google-project/story_forge/tests/generic_unseen.mp4"
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
    original_name = None
    target = None

    if "file" in request.files:
        upload_res = upload_video()
        if isinstance(upload_res, tuple) and upload_res[1] != 200:
            return upload_res
        res_data = upload_res.get_json()
        target = Path(res_data["path"])
        original_name = res_data.get("original_name")
    else:
        data = request.get_json() or {}
        path_str = data.get("path", "").strip()
        original_name = data.get("original_name")
        if not path_str:
            return jsonify({"status": "error", "error": "No file path provided"}), 400

        target = Path(path_str)
        if not target.exists():
            return jsonify({"status": "error", "error": f"File does not exist: {path_str}"}), 404

    try:
        from scripts.video_seo_reverse_engineer import extract_technical_metadata
        meta = extract_technical_metadata(target)
        display_name = original_name or target.name
        return jsonify({
            "status": "ok",
            "file_info": {
                "name": display_name,
                "server_filename": target.name,
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

def _run_story_analysis(task_id: str, video_path: Path, settings: Dict[str, Any], original_name: Optional[str] = None):
    """Thread worker: analyzes video, creates DNA, character universe, and initial stories."""
    try:
        def update_task(pct: int, stage: str):
            with TASKS_LOCK:
                if task_id in TASKS:
                    TASKS[task_id]["progress"] = pct
                    TASKS[task_id]["stage"] = stage

        update_task(10, "Verifying video asset and container...")
        time.sleep(0.05)

        update_task(25, "Extracting video narrative evidence & timeline milestones...")
        evidence = extract_video_story_evidence(video_path, original_filename=original_name)
        if original_name:
            evidence["source_video_name"] = original_name
            evidence["original_video_name"] = original_name

        update_task(50, "Synthesizing Story DNA & thematic tension...")
        story_dna = build_story_dna(evidence)

        update_task(65, "Extracting Canon Characters & building Character Universe...")
        canon_chars = extract_canon_characters(evidence, story_dna)
        char_universe = build_character_universe(canon_chars, pool_size=25)

        mode = settings.get("mode", "AUTO")
        threshold = float(settings.get("threshold", 0.70))
        target_count = int(settings.get("target_count", 50))

        if target_count >= 100 or settings.get("universe_mode", False):
            update_task(75, f"Generating {target_count} Story Universe with Auto-Grow...")
            univ_res = generate_story_universe(
                evidence=evidence,
                story_dna=story_dna,
                target_count=target_count,
                diversity_threshold=threshold,
                progress_callback=lambda p, m: update_task(int(70 + (p * 0.25)), m)
            )
            stories = univ_res["universe_stories"]
            metrics = univ_res["metrics"]
            char_universe = univ_res["character_universe"]
        else:
            update_task(75, "Generating 50 distinct root stories across 20 dimensions...")
            stories = generate_50_root_stories(story_dna, mode=mode, threshold=threshold)
            
            # Compute baseline universe metrics for the 50 root stories
            species_set = set()
            settings_set = set()
            for s in stories:
                for c in s.get("characters", []):
                    if c.get("species"):
                        species_set.add(c.get("species").title())
                if s.get("setting"):
                    settings_set.add(s.get("setting"))

            metrics = {
                "total_stories": len(stories),
                "target_requested": 50,
                "unique_species_count": len(species_set) or 1,
                "unique_species_list": sorted(list(species_set)),
                "unique_settings_count": len(settings_set),
                "diversity_score_range": {
                    "avg": round(sum(s.get("diversity_score", 0.75) for s in stories) / len(stories), 2) if stories else 0.75
                },
                "quality_score_range": {
                    "avg": round(sum(s.get("quality_score", 85.0) for s in stories) / len(stories), 1) if stories else 85.0
                }
            }

        update_task(92, "Persisting Story Bible, Character Universe & Lineage...")
        session_id = str(uuid.uuid4())[:8]
        save_session(
            session_id=session_id,
            meta=evidence,
            story_dna=story_dna,
            settings=settings,
            character_universe=char_universe,
            universe_metrics=metrics
        )
        save_stories_batch(session_id, stories)

        update_task(100, f"Analysis complete! {len(stories)} Stories Ready in Universe.")
        with TASKS_LOCK:
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["session_id"] = session_id
            TASKS[task_id]["result"] = {
                "session_id": session_id,
                "story_dna": story_dna,
                "stories_count": len(stories),
                "evidence_items_count": len(evidence.get("evidence_items", [])),
                "character_universe": char_universe,
                "universe_metrics": metrics,
                "video_hash": evidence.get("source_video_hash"),
                "source_video_name": evidence.get("source_video_name")
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
    original_name = data.get("original_name")
    if not path_str:
        return jsonify({"status": "error", "error": "No file path provided"}), 400

    target = Path(path_str)
    if not target.exists():
        return jsonify({"status": "error", "error": f"File does not exist: {path_str}"}), 404

    settings = {
        "mode": data.get("mode", "AUTO"),
        "threshold": float(data.get("threshold", 0.70)),
        "target_count": int(data.get("target_count", 50)),
        "universe_mode": bool(data.get("universe_mode", False)),
        "original_name": original_name
    }

    task_id = str(uuid.uuid4())[:8]
    with TASKS_LOCK:
        TASKS[task_id] = {
            "status": "running",
            "progress": 5,
            "stage": "Initializing Story Universe Factory...",
            "target_path": str(target),
            "original_name": original_name or target.name,
            "session_id": None,
            "result": None,
            "error": None
        }

    thread = threading.Thread(
        target=_run_story_analysis,
        args=(task_id, target, settings, original_name),
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

def _run_universe_generation(
    task_id: str,
    session_id: Optional[str],
    video_path: Optional[Path],
    target_count: int,
    diversity_threshold: float,
    quality_threshold: float
):
    """Background worker for Auto-Grow universe expansion."""
    try:
        def update_task(pct: int, stage: str):
            with TASKS_LOCK:
                if task_id in TASKS:
                    TASKS[task_id]["progress"] = pct
                    TASKS[task_id]["stage"] = stage

        update_task(5, "Resolving session and story DNA context...")

        if session_id:
            sess = get_session(session_id)
            if not sess:
                raise ValueError(f"Session {session_id} not found")
            story_dna = sess.get("story_dna", {})
            evidence = {
                "source_video_name": sess.get("source_video_name", "Video Asset"),
                "source_video_path": sess.get("source_video_path", ""),
                "source_video_hash": sess.get("source_video_hash", ""),
                "file_size_bytes": sess.get("file_size_bytes", 0),
                "technical_metadata": {"duration_seconds": sess.get("duration_seconds", 0.0)},
                "evidence_items": []
            }
        elif video_path:
            update_task(10, "Extracting video narrative evidence...")
            evidence = extract_video_story_evidence(video_path)
            story_dna = build_story_dna(evidence)
            session_id = str(uuid.uuid4())[:8]
        else:
            raise ValueError("Either session_id or video_path must be provided")

        update_task(20, f"Synthesizing Story Universe ({target_count} target stories)...")
        univ_result = generate_story_universe(
            evidence=evidence,
            story_dna=story_dna,
            target_count=target_count,
            diversity_threshold=diversity_threshold,
            quality_threshold=quality_threshold,
            progress_callback=lambda p, m: update_task(int(20 + (p * 0.70)), m)
        )

        update_task(92, "Persisting Universe records and updating metrics...")
        settings = {
            "target_count": target_count,
            "diversity_threshold": diversity_threshold,
            "quality_threshold": quality_threshold,
            "universe_mode": True
        }
        save_session(
            session_id=session_id,
            meta=evidence,
            story_dna=story_dna,
            settings=settings,
            character_universe=univ_result["character_universe"],
            universe_metrics=univ_result["metrics"]
        )
        save_stories_batch(session_id, univ_result["universe_stories"])

        update_task(100, f"Successfully forged {len(univ_result['universe_stories'])} Story Universe!")
        with TASKS_LOCK:
            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["session_id"] = session_id
            TASKS[task_id]["result"] = {
                "session_id": session_id,
                "total_stories": len(univ_result["universe_stories"]),
                "character_universe": univ_result["character_universe"],
                "universe_metrics": univ_result["metrics"],
                "top_rankings": univ_result["top_rankings"]
            }
    except Exception as e:
        with TASKS_LOCK:
            if task_id in TASKS:
                TASKS[task_id]["status"] = "error"
                TASKS[task_id]["error"] = str(e)

@app.route("/api/universe/generate", methods=["POST"])
def generate_universe_endpoint():
    """Generates or auto-grows a story universe (100, 300, 500, 1000+)."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "").strip() or None
    path_str = data.get("path", "").strip() or None
    target_count = int(data.get("target_count", 100))
    diversity_threshold = float(data.get("diversity_threshold", 0.75))
    quality_threshold = float(data.get("quality_threshold", 85.0))

    if not session_id and not path_str:
        return jsonify({"status": "error", "error": "Either session_id or path is required"}), 400

    target_path = Path(path_str) if path_str else None
    if target_path and not target_path.exists():
        return jsonify({"status": "error", "error": f"Path not found: {path_str}"}), 404

    task_id = str(uuid.uuid4())[:8]
    with TASKS_LOCK:
        TASKS[task_id] = {
            "status": "running",
            "progress": 5,
            "stage": f"Starting Universe Auto-Grow ({target_count} stories)...",
            "session_id": session_id,
            "target_count": target_count,
            "result": None,
            "error": None
        }

    thread = threading.Thread(
        target=_run_universe_generation,
        args=(task_id, session_id, target_path, target_count, diversity_threshold, quality_threshold),
        daemon=True
    )
    thread.start()

    return jsonify({"status": "ok", "task_id": task_id})

@app.route("/api/universe/status/<task_id>", methods=["GET"])
def get_universe_status(task_id: str):
    """Polls status of universe generation task."""
    return get_status(task_id)

@app.route("/api/universe/<session_id>", methods=["GET"])
def get_universe_data(session_id: str):
    """Retrieves universe metrics, character universe, worlds, and top rankings."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    stories = get_all_stories_for_session(session_id)
    ranked_10 = rank_story_universe(stories, top_n=10, sort_by="quality")
    ranked_50 = rank_story_universe(stories, top_n=50, sort_by="quality")
    ranked_100 = rank_story_universe(stories, top_n=100, sort_by="quality")

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "session": sess,
        "universe_metrics": sess.get("universe_metrics", {}),
        "character_universe": sess.get("character_universe", {}),
        "story_worlds": get_all_story_worlds(),
        "total_stories": len(stories),
        "top_rankings": {
            "top_10": [s.get("story_id") for s in ranked_10],
            "top_50": [s.get("story_id") for s in ranked_50],
            "top_100": [s.get("story_id") for s in ranked_100]
        }
    })

@app.route("/api/ranking/<session_id>", methods=["GET"])
def get_ranked_stories(session_id: str):
    """Returns ranked universe stories filtered by top_n and sort_by criteria."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    top_n_str = request.args.get("top_n", "50").strip().lower()
    sort_by = request.args.get("sort_by", "quality").strip()

    stories = get_all_stories_for_session(session_id)
    if top_n_str == "all":
        top_n = len(stories)
    else:
        try:
            top_n = int(top_n_str)
        except ValueError:
            top_n = 50

    ranked = rank_story_universe(stories, top_n=top_n, sort_by=sort_by)
    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "count": len(ranked),
        "total_universe_stories": len(stories),
        "sort_by": sort_by,
        "stories": ranked
    })

@app.route("/api/produce/<session_id>/<story_id>", methods=["POST", "GET"])
def produce_story_endpoint(session_id: str, story_id: str):
    """Generates and caches 9-part production package for selected story."""
    story = get_story(session_id, story_id)
    if not story:
        return jsonify({"status": "error", "error": f"Story {story_id} not found"}), 404

    sess = get_session(session_id)
    story_dna = sess.get("story_dna", {}) if sess else {}

    # Check cache if GET request
    if request.method == "GET":
        cached = get_production_package(session_id, story_id)
        if cached:
            return jsonify({"status": "ok", "package": cached, "cached": True})

    # Generate fresh package
    package = produce_story_package(story, story_dna)
    save_production_package(session_id, story_id, package)

    return jsonify({"status": "ok", "package": package, "cached": False})

@app.route("/api/production/<session_id>/<story_id>", methods=["GET"])
def get_production_package_endpoint(session_id: str, story_id: str):
    """Retrieves or auto-generates production package for a story."""
    cached = get_production_package(session_id, story_id)
    if cached:
        return jsonify({"status": "ok", "package": cached, "cached": True})
    
    return produce_story_endpoint(session_id, story_id)

@app.route("/api/session/<session_id>", methods=["GET"])
def get_session_data(session_id: str):
    """Retrieves full session data, Story DNA, all stories, and lineage tree."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    stories = get_all_stories_for_session(session_id)
    lineage = get_lineage_graph(session_id)
    dna = sess.get("story_dna", {})

    return jsonify({
        "status": "ok",
        "session": sess,
        "story_dna": dna,
        "character_universe": sess.get("character_universe", {}),
        "universe_metrics": sess.get("universe_metrics", {}),
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
        parent = session.get("story_dna", {}) if session else {}
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
    """Exports session report in various formats."""
    sess = get_session(session_id)
    if not sess:
        return jsonify({"status": "error", "error": "Session not found"}), 404

    base_name = f"story_universe_{sess.get('source_video_name', 'story')}_{session_id}"

    if format_name in ("universe_json", "json"):
        data = export_universe_json(session_id)
        return Response(
            data,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={base_name}.json"}
        )
    elif format_name in ("story_bible", "markdown", "md"):
        data = export_story_bible_markdown(session_id)
        return Response(
            data,
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}_story_bible.md"}
        )
    elif format_name == "character_bible":
        data = export_character_bible_markdown(session_id)
        return Response(
            data,
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}_character_bible.md"}
        )
    elif format_name == "relationship_graph":
        data = export_relationship_graph_markdown(session_id)
        return Response(
            data,
            mimetype="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}_relationship_graph.md"}
        )
    elif format_name in ("top_stories_csv", "csv", "txt"):
        data = export_top_stories_csv(session_id)
        return Response(
            data,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={base_name}_top_stories.csv"}
        )
    elif format_name == "zip":
        zip_bytes = build_full_universe_zip_bundle(session_id)
        return Response(
            zip_bytes,
            mimetype="application/zip",
            headers={"Content-Disposition": f"attachment; filename={base_name}_universe_bundle.zip"}
        )
    else:
        return jsonify({"status": "error", "error": f"Unsupported format: {format_name}"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"🚀 Starting PLB Story Universe Factory on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
