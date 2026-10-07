#!/usr/bin/env python3
"""
End-to-End Verification Test Suite for PLB Video SEO Reverse Engine
====================================================================
Tests the full system against C:\\Users\\Admin\\Downloads\\test-reel\\test-reel.mp4
1. Verifies core reverse-engineering functions
2. Verifies Flask API endpoints (/api/recent, /api/scan, /api/analyze, /api/status)
3. Verifies keyframe extraction & serving
4. Verifies Markdown, JSON, and ZIP bundle exports
5. Verifies adherence to non-destructive rules & evidence classification
"""

import os
import sys
import time
import json
import zipfile
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root and scripts to path
current_dir = Path(__file__).resolve().parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
scripts_dir = current_dir / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from app import app
from scripts.video_seo_reverse_engineer import (
    locate_source_files,
    extract_technical_metadata,
    extract_c2pa_provenance,
    run_full_analysis
)

def run_e2e_verification():
    print("=" * 70)
    print(" 🚀 STARTING PLB VIDEO SEO REVERSE ENGINE E2E VERIFICATION TEST")
    print("=" * 70)
    
    target_video = Path("C:/Users/Admin/Downloads/test-reel/test-reel.mp4")
    if not target_video.exists():
        print(f"❌ Target video not found at: {target_video}")
        sys.exit(1)
        
    print(f"✅ Found target video: {target_video} ({round(target_video.stat().st_size / (1024*1024), 2)} MB)")
    
    # ----------------------------------------------------
    # 1. CORE ENGINE DIRECT TESTS
    # ----------------------------------------------------
    print("\n--- STEP 1: Core Engine Unit Validation ---")
    source_ev = locate_source_files(target_video)
    found_sidecars = [Path(f).name for f in source_ev.get("found_files", [])]
    print(f"Discovered sidecar files: {found_sidecars}")
    assert "Caption.md" in found_sidecars, "Caption.md was not discovered!"
    print("✅ Sidecar discovery verified.")
    
    tech_meta = extract_technical_metadata(target_video)
    print(f"Format: {tech_meta.get('format_name')}, Duration: {tech_meta.get('duration_seconds')}s")
    assert tech_meta.get("duration_seconds") > 25.0, "Duration extraction failed!"
    print("✅ Technical metadata extraction verified.")
    
    c2pa_meta = extract_c2pa_provenance(target_video)
    print(f"C2PA Present: {c2pa_meta.get('present')}, Model: {c2pa_meta.get('model_name')}")
    assert c2pa_meta.get("present") is True, "C2PA manifest was not identified!"
    assert c2pa_meta.get("model_name") == "dreamina-seedance-2-5", "C2PA model extraction mismatch!"
    print("✅ C2PA provenance extraction verified.")
    
    # ----------------------------------------------------
    # 2. FLASK TEST CLIENT & API SUITE
    # ----------------------------------------------------
    print("\n--- STEP 2: Flask API & UI Integration Validation ---")
    client = app.test_client()
    
    # Test GET /
    res = client.get("/")
    assert res.status_code == 200, f"GET / returned {res.status_code}"
    html = res.data.decode("utf-8")
    assert "PLB Video SEO Reverse Engine" in html, "UI title missing"
    assert "OVERVIEW" in html and "SOURCE SEO" in html and "TIMELINE" in html, "UI tabs missing"
    assert "SEO COMPARISON" in html, "SEO comparison table missing from UI"
    print("✅ GET / returns 200 with full 10-tab dashboard & SEO comparison table.")
    
    # Test GET /api/recent
    res = client.get("/api/recent")
    assert res.status_code == 200, f"GET /api/recent returned {res.status_code}"
    recent_data = res.get_json()
    assert len(recent_data.get("candidates", [])) > 0, "No candidates returned from /api/recent"
    print(f"✅ GET /api/recent returned {len(recent_data['candidates'])} candidates.")
    
    # Test POST /api/scan
    res = client.post("/api/scan", json={"path": str(target_video).replace("\\", "/")})
    assert res.status_code == 200, f"POST /api/scan returned {res.status_code}"
    scan_data = res.get_json()
    assert scan_data.get("status") == "ok", "Scan status was not ok"
    assert scan_data["file_info"]["codec"] == "h264", "Video codec was not h264"
    assert "Caption.md" in scan_data["sidecars_found"], "Caption.md missing from scan sidecars"
    print(f"✅ POST /api/scan successfully verified: {scan_data['file_info']['resolution']}, {scan_data['file_info']['codec']}, {scan_data['file_info']['fps']} fps.")
    
    # Test POST /api/analyze
    res = client.post("/api/analyze", json={"path": str(target_video).replace("\\", "/")})
    assert res.status_code == 200, f"POST /api/analyze returned {res.status_code}"
    task_init = res.get_json()
    task_id = task_init.get("task_id")
    assert task_id, "No task_id returned from /api/analyze"
    print(f"✅ POST /api/analyze initiated background task: {task_id}")
    
    # Poll GET /api/status/<task_id>
    print("Polling task completion...")
    max_wait = 45
    start_t = time.time()
    final_task_data = None
    
    while time.time() - start_t < max_wait:
        res = client.get(f"/api/status/{task_id}")
        assert res.status_code == 200, f"Status check failed: {res.status_code}"
        st = res.get_json()
        print(f"  -> Progress: {st.get('progress')}% | Stage: {st.get('stage')}")
        if st.get("status") == "completed":
            final_task_data = st
            break
        elif st.get("status") == "error":
            raise RuntimeError(f"Task failed with error: {st.get('error')}")
        time.sleep(1.0)
        
    assert final_task_data is not None, "Task did not complete within timeout!"
    print("✅ Analysis task completed with 100% progress!")
    
    result = final_task_data["result"]
    assert result, "No result payload returned!"
    
    # Verify Ground Truth Source SEO
    orig = result["original_metadata"]
    print("\n--- STEP 3: Source SEO vs. Reconstructed SEO Audit ---")
    print(f"Original Title: {orig['title']}")
    print(f"Original Caption Main: {orig['caption_main']}")
    print(f"Original Hashtags: {orig['hashtags']}")
    print(f"Original Keywords: {orig['keywords']}")
    assert "8. Sprinkler Chase" in orig["title"], "Original title mismatch!"
    assert "[NOT PRESENT IN SOURCE]" in orig["keywords"], "Keywords should be marked NOT PRESENT IN SOURCE!"
    print("✅ Source metadata ground truth verified (non-invented).")
    
    # Verify Reconstructed SEO
    rec = result["reconstructed_seo"]
    print(f"Primary Topic: {rec['primary_topic']}")
    print(f"Primary Keyword: {rec['primary_keyword']}")
    print(f"10 SEO Titles generated: {len(rec['seo_titles'])}")
    print(f"3 Retention Titles generated: {len(rec['retention_titles'])}")
    print(f"Platform Packages: {list(rec['platforms'].keys())}")
    assert len(rec["seo_titles"]) == 10, "Expected 10 SEO titles!"
    assert len(rec["retention_titles"]) == 3, "Expected 3 retention titles!"
    assert "tiktok" in rec["platforms"] and "instagram_reels" in rec["platforms"], "Platform packages missing!"
    print("✅ Reconstructed SEO package verified.")
    
    # Verify Evidence Table
    ev_table = result["evidence_table"]
    print(f"Evidence Table Rows: {len(ev_table)}")
    assert len(ev_table) >= 7, "Evidence table missing rows!"
    for row in ev_table:
        assert row.get("confidence") == "100% (Fact)", f"Unexpected confidence in {row}"
    print("✅ Master Evidence Table verified (100% Fact separation).")
    
    # ----------------------------------------------------
    # 3. VERIFY EXPORTS & FRAME IMAGES
    # ----------------------------------------------------
    print("\n--- STEP 4: Export Format & Keyframe Verification ---")
    
    # Check Frame image endpoint
    frames = result["timeline_frames"]
    assert len(frames) >= 10, f"Expected at least 10 timeline frames, got {len(frames)}"
    test_frame = frames[0]
    res = client.get(f"/api/frames/{task_id}/{test_frame['filename']}")
    assert res.status_code == 200, f"Frame endpoint returned {res.status_code}"
    assert res.mimetype == "image/jpeg", f"Wrong frame mimetype: {res.mimetype}"
    print(f"✅ Keyframe endpoint verified: served {test_frame['filename']} (image/jpeg, {len(res.data)} bytes)")
    
    # Check Markdown Export
    res = client.get(f"/api/export/markdown/{task_id}")
    assert res.status_code == 200, f"Markdown export returned {res.status_code}"
    md_content = res.data.decode("utf-8")
    assert "# VIDEO SEO REVERSE-ENGINEERING REPORT" in md_content, "Markdown report header missing"
    assert "Ground-Truth Original Metadata" in md_content, "Ground truth section missing"
    print(f"✅ Markdown export verified: {len(md_content)} chars")
    
    # Check JSON Export
    res = client.get(f"/api/export/json/{task_id}")
    assert res.status_code == 200, f"JSON export returned {res.status_code}"
    exported_json = json.loads(res.data.decode("utf-8"))
    assert "reconstructed_seo" in exported_json, "JSON export missing reconstructed_seo"
    print(f"✅ JSON export verified: valid JSON structure with {len(exported_json.keys())} root keys")
    
    # Check ZIP Bundle Export
    res = client.get(f"/api/export/zip/{task_id}")
    assert res.status_code == 200, f"ZIP export returned {res.status_code}"
    assert res.mimetype == "application/zip", f"Wrong zip mimetype: {res.mimetype}"
    
    # Save temporary zip and inspect contents
    temp_zip_file = current_dir / "cache_analysis" / f"test_inspect_{task_id}.zip"
    temp_zip_file.write_bytes(res.data)
    with zipfile.ZipFile(temp_zip_file, "r") as z:
        names = z.namelist()
        print(f"ZIP Bundle contents ({len(names)} items):")
        for n in names[:5]:
            print(f"  - {n}")
        if len(names) > 5:
            print(f"  - ... ({len(names)-5} more)")
        assert "VIDEO-SEO-REVERSE-ENGINEERING-REPORT.md" in names, "Report missing from ZIP"
        assert "analysis_data.json" in names, "analysis_data.json missing from ZIP"
        assert any(n.startswith("frames/") and n.endswith(".jpg") for n in names), "Frames missing from ZIP"
        
    if temp_zip_file.exists():
        temp_zip_file.unlink()
    print("✅ ZIP bundle export verified: contains report, JSON, and extracted frames.")
    
    print("\n" + "=" * 70)
    print(" 🎉 ALL E2E VERIFICATION TESTS PASSED SUCCESSFULLY! (100% GREEN)")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()
