#!/usr/bin/env python3
"""
Verification Script for Packaged Executable (PLB-Studio.exe)
============================================================
Launches dist/PLB-Studio/PLB-Studio.exe and verifies:
1. 3-Engine boot & health (/ on 5595, /api/recent on 5094, / on 5095)
2. Diagnostics self-test endpoint (/api/diagnostics/self-test)
3. Upload / inspect endpoint (/api/inspect)
4. Video analysis, Story DNA semantic integrity, zero placeholders
5. Clean shutdown
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

# Ensure UTF-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

project_root = Path(__file__).resolve().parent.parent
exe_path = project_root / "dist" / "PLB-Studio" / "PLB-Studio.exe"

def http_get(url, timeout=5):
    req = urllib.request.Request(url, headers={"User-Agent": "PLB-Verifier"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))

def http_post_json(url, payload, timeout=10):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "PLB-Verifier"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), json.loads(resp.read().decode("utf-8"))

def main():
    print("=" * 70)
    print(" 🔍 VERIFYING COMPILED WINDOWS STANDALONE EXECUTABLE")
    print("=" * 70)
    print(f"Target Executable: {exe_path}")
    assert exe_path.exists(), f"Executable not found at {exe_path}"
    print(f"File Size: {round(exe_path.stat().st_size / (1024 * 1024), 2)} MB")

    port_studio = 5595
    port_seo = 5094
    port_univ = 5095

    cmd = [
        str(exe_path),
        "--port", str(port_studio),
        "--seo-port", str(port_seo),
        "--universe-port", str(port_univ),
        "--no-gui"
    ]

    print(f"\n[STEP 1] Launching packaged executable: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(project_root)
    )

    try:
        # 1. Wait for all 3 ports to respond
        print("[STEP 2] Waiting for all 3 services to initialize...")
        start_time = time.time()
        ready = False
        while time.time() - start_time < 30:
            if proc.poll() is not None:
                out, err = proc.communicate()
                print("Process died prematurely!")
                print("STDOUT:", out)
                print("STDERR:", err)
                sys.exit(1)
            try:
                c1 = urllib.request.urlopen(f"http://127.0.0.1:{port_studio}/", timeout=1).getcode()
                c2 = urllib.request.urlopen(f"http://127.0.0.1:{port_seo}/api/recent", timeout=1).getcode()
                c3 = urllib.request.urlopen(f"http://127.0.0.1:{port_univ}/api/recent", timeout=1).getcode()
                if c1 == 200 and c2 == 200 and c3 == 200:
                    ready = True
                    break
            except Exception:
                time.sleep(0.5)

        assert ready, "Services failed to become ready within 30 seconds."
        print(f"  ✓ All 3 services active! Studio:{port_studio}, SEO:{port_seo}, Universe:{port_univ}")

        # 2. Check Diagnostics Self-Test
        print("\n[STEP 3] Running diagnostics self-test on running executable...")
        status, diag = http_get(f"http://127.0.0.1:{port_univ}/api/diagnostics/self-test")
        assert status == 200, f"Diagnostics failed with {status}"
        assert diag.get("status") == "ok", f"Unexpected diag status: {diag.get('status')}"
        results = diag.get("results", {})
        comp = results.get("components", {})
        print(f"  ✓ Diagnostics status: {diag.get('status')}")
        print(f"  ✓ Components tested: {len(comp)} ({', '.join(comp.keys())})")
        for cname, cinfo in comp.items():
            print(f"    - {cname}: {cinfo.get('status')}")
            assert cinfo.get("status") == "PASS", f"Component {cname} failed self-test!"

        # 3. Inspect video file via /api/scan
        print("\n[STEP 4] Testing video inspection endpoint (/api/scan) on compiled EXE...")
        ref_video = (project_root / "input" / "ref-video.mp4").resolve()
        assert ref_video.exists(), "ref-video.mp4 not found"
        status, insp = http_post_json(
            f"http://127.0.0.1:{port_univ}/api/scan",
            {"path": str(ref_video)}
        )
        assert status == 200, f"Inspect failed: {insp}"
        finfo = insp.get("file_info", {})
        print(f"  ✓ Inspected: {finfo.get('name')}")
        print(f"  ✓ Resolution: {finfo.get('resolution')} | Codec: {finfo.get('codec')} | FPS: {finfo.get('fps')}")
        assert finfo.get("resolution") != "?x?", "Resolution must not be unknown"

        # 4. Analyze video and verify Story DNA integrity
        print("\n[STEP 5] Testing video analysis and Story DNA semantic integrity...")
        status, ares = http_post_json(
            f"http://127.0.0.1:{port_univ}/api/analyze",
            {"path": str(ref_video), "mode": "AUTO", "threshold": 0.70}
        )
        assert status == 200, f"Analyze call failed: {ares}"
        task_id = ares["task_id"]

        print(f"  ✓ Analysis task started: {task_id}. Polling progress...")
        for _ in range(60):
            st_code, st_json = http_get(f"http://127.0.0.1:{port_univ}/api/status/{task_id}")
            if st_json.get("status") == "completed":
                break
            time.sleep(0.5)

        assert st_json.get("status") == "completed", f"Analysis timed out or failed: {st_json}"
        sess_id = st_json["session_id"]
        status, sess_data = http_get(f"http://127.0.0.1:{port_univ}/api/session/{sess_id}")
        assert status == 200
        dna = sess_data["story_dna"]

        print(f"  ✓ Analysis completed! Session ID: {sess_id}")
        print(f"  ✓ Lead Character: {dna['characters'][0]['name']}")
        print(f"  ✓ Metadata Cue: {dna.get('metadata_cue')}")
        print(f"  ✓ CV Limitation Disclosed: {dna.get('cv_limitation_disclosed')}")
        print(f"  ✓ Core Premise: {dna.get('core_premise')[:80]}...")

        # Semantic Integrity assertions
        char_name = dna["characters"][0]["name"]
        print(f"  ✓ Vision Grounding Verification: Character='{char_name}', Limitation Disclosed={dna.get('cv_limitation_disclosed')}")
        assert char_name in ["Cockatoo", "Observed Protagonist"], f"Unexpected character name: {char_name}"
        if char_name == "Cockatoo":
            assert dna.get("cv_limitation_disclosed") is False, "Verified vision entity should not disclose limitation"
        else:
            assert dna.get("cv_limitation_disclosed") is True, "Unverified entity must disclose limitation"
        assert "focal element" not in json.dumps(dna).lower(), "Focal element found in Story DNA!"
        assert "identified as" not in json.dumps(dna).lower(), "Identified as found in Story DNA!"

        print("\n" + "=" * 70)
        print(" 🎉 COMPILED EXECUTABLE PASSED ALL TESTS WITH FULL INTEGRITY!")
        print("=" * 70)

    finally:
        print("\n[STEP 6] Terminating executable...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        print("  ✓ Executable stopped cleanly.")

if __name__ == "__main__":
    main()
