#!/usr/bin/env python3
"""
Regression Test Suite for Bug #002: Source Video Identity & Story DNA Integrity
================================================================================
Verifies that:
1. Video profiles are strictly isolated and never fall back to hardcoded animal profiles.
2. Video A vs Video B produce distinct Story DNA with distinct hashes and entities.
3. Story DNA B contains NO trace of Video A's entities, actions, or settings.
4. Auto-Grow on Video B derives stories strictly from Video B's DNA.
5. Passing a stale session_id for a new video path does NOT cross-pollinate.
6. Shared directory sidecars do NOT pollute unrelated videos.
7. Real-world user videos (dola, HDS, Winter Colobok) never get hijacked into chicken/rabbit profiles.
"""

import sys
import os
import json
import uuid
import tempfile
import numpy as np
import cv2
import pytest
from pathlib import Path

# Project root setup
current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scripts.video_seo_reverse_engineer import (
    detect_visual_narrative_profile,
    build_visual_evidence_profile,
    locate_source_files,
    sanitize_filename_tokens
)
from story_forge.engine.video_story_extractor import extract_video_story_evidence
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.character_universe import extract_canon_characters
from story_forge.engine.universe_engine import generate_story_universe
from story_forge.storage.db import init_db, save_session, get_session
from story_forge.app import app

def create_synthetic_test_video(path: Path, color_bgr: tuple, duration_sec: int = 2, fps: int = 24):
    """Generates a small valid MP4 video with a solid or gradient frame color."""
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = 320, 240
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    for i in range(duration_sec * fps):
        # Create a frame with base color and slight dynamic movement
        frame = np.full((h, w, 3), color_bgr, dtype=np.uint8)
        cv2.circle(frame, (50 + i * 2, 120), 20, (255, 255, 255), -1)
        out.write(frame)
    out.release()
    return path

class TestBug002SourceVideoIdentity:
    """Rigorous tests ensuring 1:1 fidelity between uploaded videos and their Story DNA."""

    def test_profile_detection_no_broad_fallbacks(self):
        """Ensure arbitrary videos with outdoor/wood colors do NOT match chicken, rabbit, or duck profiles."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Video with high wood/brown and white (which previously triggered chicken_coop_lime fallback)
            wood_video = tmp_path / "mountain_cabin_retreat.mp4"
            create_synthetic_test_video(wood_video, (30, 60, 120))  # Brown/wood tone
            
            profile = detect_visual_narrative_profile(wood_video)
            assert profile == "generic", f"Expected 'generic', got '{profile}'"

            # Video with high green and white (which previously triggered duck or rabbit fallback)
            green_video = tmp_path / "golf_course_championship.mp4"
            create_synthetic_test_video(green_video, (30, 180, 40))  # Green foliage tone
            
            profile2 = detect_visual_narrative_profile(green_video)
            assert profile2 == "generic", f"Expected 'generic', got '{profile2}'"

    def test_real_user_videos_profile_isolation(self):
        """Verify actual user videos on disk do NOT get hijacked into chicken_coop_lime."""
        dola_path = Path("temp_uploads/d70c5a_dola_20261007060757_video.mp4")
        if dola_path.exists():
            prof = detect_visual_narrative_profile(dola_path)
            assert prof == "generic", f"Dola video must be 'generic', not '{prof}'"

        hds_path = Path("temp_uploads/f4ec53_HDS_2026-10-05_04-31-24_Generated_video.mp4")
        if hds_path.exists():
            prof = detect_visual_narrative_profile(hds_path)
            assert prof == "generic", f"HDS video must be 'generic', not '{prof}'"

        colobok_matches = list(Path("input").glob("*Winter*"))
        if colobok_matches:
            prof = detect_visual_narrative_profile(colobok_matches[0])
            assert prof == "generic", f"Winter Colobok must be 'generic', not '{prof}'"

    def test_video_a_vs_video_b_story_dna_integrity(self):
        """Prove Video A and Video B produce completely distinct DNA with zero cross-contamination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            video_a_path = tmp_path / "Forest_Adventurer_Quest.mp4"
            video_b_path = tmp_path / "Cyber_Drone_Over_City.mp4"

            create_synthetic_test_video(video_a_path, (20, 120, 30))   # Forest green
            create_synthetic_test_video(video_b_path, (120, 40, 20))   # Urban blue/dark

            # Extract Evidence & DNA for Video A
            ev_a = extract_video_story_evidence(video_a_path)
            dna_a = build_story_dna(ev_a)

            # Extract Evidence & DNA for Video B
            ev_b = extract_video_story_evidence(video_b_path)
            dna_b = build_story_dna(ev_b)

            # 1. Video hashes must be distinct
            assert dna_a["source_video_hash"] != dna_b["source_video_hash"]

            # 2. Characters must match their respective videos
            char_a_name = dna_a["characters"][0]["name"]
            char_b_name = dna_b["characters"][0]["name"]
            assert "Forest" in char_a_name or "Adventurer" in char_a_name
            assert "Cyber" in char_b_name or "Drone" in char_b_name
            assert char_a_name != char_b_name

            # 3. Core Premises must NOT contain the other video's entities
            assert "Drone" not in dna_a["core_premise"]
            assert "Cyber" not in dna_a["core_premise"]
            assert "Forest" not in dna_b["core_premise"]
            assert "Adventurer" not in dna_b["core_premise"]

            # 4. Absolutely ZERO test asset animals in either
            forbidden = ["silkie", "chicken", "rabbit", "bunny", "horseradish", "pekin duck", "puppy", "grapefruit"]
            for f in forbidden:
                assert f not in dna_a["core_premise"].lower(), f"Leaked '{f}' into DNA A!"
                assert f not in dna_b["core_premise"].lower(), f"Leaked '{f}' into DNA B!"

    def test_canon_characters_profile_isolation(self):
        """Canon characters must be derived from actual video, never defaulting to Silkie or Bunny."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            video_path = tmp_path / "Arctic_Polar_Fox.mp4"
            create_synthetic_test_video(video_path, (200, 200, 200))

            ev = extract_video_story_evidence(video_path)
            dna = build_story_dna(ev)
            canon = extract_canon_characters(ev, dna)

            assert len(canon) >= 1
            assert "Fox" in canon[0].name or "Arctic" in canon[0].name
            assert canon[0].name not in ["White Silkie", "Spotted Bunny", "Pekin Duck", "Slider Turtle"]

    def test_sidecar_discovery_isolation_in_shared_folder(self):
        """In a shared directory, sidecar files belonging to Video A must never attach to Video B."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            video_a = tmp_path / "clip_alpha.mp4"
            video_b = tmp_path / "clip_beta.mp4"

            create_synthetic_test_video(video_a, (100, 100, 100))
            create_synthetic_test_video(video_b, (200, 200, 200))

            # Create sidecar specifically for video A
            sidecar_a = tmp_path / "clip_alpha_notes.txt"
            sidecar_a.write_text("Notes for clip alpha about forest bears", encoding="utf-8")

            # Create generic unrelated file
            unrelated = tmp_path / "unrelated_doc.txt"
            unrelated.write_text("Secret chicken recipes", encoding="utf-8")

            # Check Video B's sidecars
            ev_b = locate_source_files(video_b)
            found_files_b = [Path(p).name for p in ev_b["found_files"]]

            assert "clip_alpha_notes.txt" not in found_files_b
            assert "unrelated_doc.txt" not in found_files_b

    def test_auto_grow_stale_session_invalidation(self):
        """Auto-grow with a new video path must invalidate an old session ID and use the new video's DNA."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            video_old = tmp_path / "old_rabbit_session.mp4"
            video_new = tmp_path / "new_superhero_flight.mp4"

            create_synthetic_test_video(video_old, (50, 50, 50))
            create_synthetic_test_video(video_new, (150, 150, 150))

            client = app.test_client()

            # Create session for video_old
            old_session_id = f"test_{uuid.uuid4().hex[:6]}"
            ev_old = extract_video_story_evidence(video_old)
            dna_old = build_story_dna(ev_old)
            save_session(
                session_id=old_session_id,
                meta=ev_old,
                story_dna=dna_old,
                settings={"target_count": 10}
            )

            # Now call /api/universe/generate with video_new PATH, but passing old_session_id!
            res = client.post("/api/universe/generate", json={
                "session_id": old_session_id,
                "path": str(video_new),
                "target_count": 10,
                "diversity_threshold": 0.75,
                "quality_threshold": 80.0
            })
            assert res.status_code == 200
            data = res.get_json()
            task_id = data["task_id"]

            # Wait for task completion
            import time
            completed = False
            for _ in range(30):
                st = client.get(f"/api/universe/status/{task_id}").get_json()
                if st.get("status") == "completed":
                    completed = True
                    break
                time.sleep(0.5)

            assert completed, "Auto-grow task did not complete"
            new_session_id = st.get("session_id")

            # Must have created a new session or updated with video_new's metadata
            assert new_session_id != old_session_id
            sess_res = client.get(f"/api/session/{new_session_id}").get_json()
            assert "Superhero" in sess_res["story_dna"]["characters"][0]["name"] or "Flight" in sess_res["story_dna"]["characters"][0]["name"]
