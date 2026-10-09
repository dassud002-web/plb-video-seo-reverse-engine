#!/usr/bin/env python3
"""
Test Suite for Task 4: Dynamic Source Switching & Session Isolation
===================================================================
Tests Video A -> Video B -> Video A dynamic switching without restarting app.
Verifies zero state bleed, independent lineages, auto-grow isolation,
and production compiler purity.
"""

import sys
import time
import json
from pathlib import Path

# Ensure UTF-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from story_forge.app import app

def test_source_switching_e2e():
    client = app.test_client()

    v_a_list = list(Path("input").glob("*Winter*"))
    assert v_a_list, "Video A (Winter Colobok) not found in input/"
    v_a = v_a_list[0].resolve()
    v_b = Path("temp_uploads/d70c5a_dola_20261007060757_video.mp4").resolve()
    assert v_b.exists(), "Video B (Dola) not found in temp_uploads/"

    print("=" * 70)
    print("TASK 4: LIVE SOURCE SWITCHING TEST: VIDEO A -> VIDEO B -> VIDEO A")
    print("=" * 70)

    # 1. Analyze Video A
    print("\n[STEP 1] Analyzing Video A (Winter Colobok)...")
    res_a = client.post("/api/analyze", json={"path": str(v_a), "mode": "AUTO", "threshold": 0.70})
    assert res_a.status_code == 200
    task_a = res_a.get_json()["task_id"]
    for _ in range(60):
        st = client.get(f"/api/status/{task_a}").get_json()
        if st.get("status") == "completed":
            break
        time.sleep(0.5)
    assert st.get("status") == "completed"
    sess_a_id = st["session_id"]
    sess_a = client.get(f"/api/session/{sess_a_id}").get_json()
    dna_a = sess_a["story_dna"]
    print(f"  ✓ Video A Session: {sess_a_id}")
    print(f"  ✓ Video A Hash: {dna_a.get('source_video_hash')}")
    print(f"  ✓ Video A Metadata Cue: {dna_a.get('metadata_cue')}")
    print(f"  ✓ Video A Premise: {dna_a.get('core_premise')[:60]}...")

    # 2. Analyze Video B without restarting
    print("\n[STEP 2] Analyzing Video B (Dola Chickens) without restart...")
    res_b = client.post("/api/analyze", json={"path": str(v_b), "mode": "AUTO", "threshold": 0.70})
    assert res_b.status_code == 200
    task_b = res_b.get_json()["task_id"]
    for _ in range(60):
        st = client.get(f"/api/status/{task_b}").get_json()
        if st.get("status") == "completed":
            break
        time.sleep(0.5)
    assert st.get("status") == "completed"
    sess_b_id = st["session_id"]
    sess_b = client.get(f"/api/session/{sess_b_id}").get_json()
    dna_b = sess_b["story_dna"]
    print(f"  ✓ Video B Session: {sess_b_id}")
    print(f"  ✓ Video B Hash: {dna_b.get('source_video_hash')}")
    print(f"  ✓ Video B Metadata Cue: {dna_b.get('metadata_cue')}")
    print(f"  ✓ Video B Premise: {dna_b.get('core_premise')[:60]}...")

    # Strict Isolation Check between A and B
    assert sess_a_id != sess_b_id, "Session IDs must be distinct!"
    assert dna_a["source_video_hash"] != dna_b["source_video_hash"], "Source hashes must be distinct!"
    assert dna_a.get("metadata_cue") != dna_b.get("metadata_cue"), "Metadata cues must be distinct!"
    assert "colobok" not in json.dumps(dna_b).lower(), "Video A cue leaked into Video B Story DNA!"
    print("  ✓ Strict Isolation Verified: Zero Video A bleed in Video B Story DNA.")

    # 3. Auto-Grow on Video B
    print("\n[STEP 3] Auto-Grow Universe on Video B...")
    res_grow_b = client.post("/api/universe/generate", json={
        "session_id": sess_b_id,
        "path": str(v_b),
        "target_count": 20,
        "diversity_threshold": 0.75,
        "quality_threshold": 80.0
    })
    assert res_grow_b.status_code == 200
    grow_task_b = res_grow_b.get_json()["task_id"]
    for _ in range(60):
        st_g = client.get(f"/api/universe/status/{grow_task_b}").get_json()
        if st_g.get("status") == "completed":
            break
        time.sleep(0.5)
    assert st_g.get("status") == "completed"
    grow_sess_b = client.get(f"/api/session/{st_g['session_id']}").get_json()
    b_stories = grow_sess_b["stories"]
    assert len(b_stories) >= 15, "Expected generated stories for Video B"
    assert "colobok" not in json.dumps(b_stories).lower(), "Video A leaked into Video B Auto-Grow stories!"
    print(f"  ✓ Auto-Grow successfully synthesized {len(b_stories)} stories derived strictly from Video B.")

    # 4. Production Package on Video B
    print("\n[STEP 4] Production Package on Video B root lineage...")
    story_b_id = b_stories[0]["story_id"]
    prod_res = client.get(f"/api/production/{st_g['session_id']}/{story_b_id}").get_json()
    assert prod_res["status"] == "ok"
    pkg = prod_res["package"]
    assert "seedance_prompt" in pkg
    assert "colobok" not in json.dumps(pkg).lower(), "Video A leaked into Video B Production Package!"
    print("  ✓ Production Package & Prompt Compiler verified on Video B with zero Video A contamination.")

    # 5. Switch back to Video A
    print("\n[STEP 5] Switching back to Video A...")
    res_a2 = client.post("/api/analyze", json={"path": str(v_a), "mode": "AUTO", "threshold": 0.70})
    assert res_a2.status_code == 200
    task_a2 = res_a2.get_json()["task_id"]
    for _ in range(60):
        st_a2 = client.get(f"/api/status/{task_a2}").get_json()
        if st_a2.get("status") == "completed":
            break
        time.sleep(0.5)
    assert st_a2.get("status") == "completed"
    sess_a2_id = st_a2["session_id"]
    sess_a2 = client.get(f"/api/session/{sess_a2_id}").get_json()
    dna_a2 = sess_a2["story_dna"]
    assert dna_a2["source_video_hash"] == dna_a["source_video_hash"], "Re-analyzed Video A must match original Video A hash!"
    assert "dola" not in json.dumps(dna_a2).lower(), "Video B content leaked into re-analyzed Video A!"
    print("  ✓ Re-analyzed Video A matches original Video A hash and has ZERO Video B content.")

    print("\n" + "=" * 70)
    print("✅ TASK 4 PASSED: FULL DYNAMIC SOURCE SWITCHING VERIFIED WITH ZERO BLEED")
    print("=" * 70)

if __name__ == "__main__":
    test_source_switching_e2e()
