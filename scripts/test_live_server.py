#!/usr/bin/env python3
import urllib.request
import json
import time
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def test_live_server():
    proc = subprocess.Popen([sys.executable, "app.py"])
    try:
        time.sleep(2)
        # 1. Test GET /
        req = urllib.request.Request("http://127.0.0.1:5000/")
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 200
            print("[LIVE SERVER] GET / => HTTP 200 OK")
            
        test_videos = [
            ("Chicken Coop Video", "C:/Users/Admin/Downloads/vid/Chicken Coop Video_TJX_no_watermark.mp4"),
            ("Active Investigation Target", "C:/Users/Admin/Downloads/test-reel/test-reel.mp4")
        ]
        
        for name, target_path in test_videos:
            print(f"\n>>> TESTING VIDEO: {name} ({target_path})")
            scan_payload = json.dumps({"path": target_path}).encode("utf-8")
            
            # Scan
            req = urllib.request.Request("http://127.0.0.1:5000/api/scan", data=scan_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                scan_res = json.loads(resp.read().decode("utf-8"))
                print(f"[LIVE SERVER] POST /api/scan => {scan_res['file_info']['resolution']}, {scan_res['file_info']['codec']}, Sidecars: {scan_res.get('sidecars_found', [])}")

            # Analyze
            req = urllib.request.Request("http://127.0.0.1:5000/api/analyze", data=scan_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                an_res = json.loads(resp.read().decode("utf-8"))
                task_id = an_res["task_id"]
                print(f"[LIVE SERVER] POST /api/analyze => task_id: {task_id}")
                
            # Poll status
            st = {}
            for _ in range(45):
                req = urllib.request.Request(f"http://127.0.0.1:5000/api/status/{task_id}")
                with urllib.request.urlopen(req) as resp:
                    st = json.loads(resp.read().decode("utf-8"))
                    p = st.get("progress")
                    m = st.get("stage")
                    print(f"  [{name}] Progress: {p}% | Stage: {m}")
                    if st.get("status") == "completed":
                        break
                time.sleep(1)
                
            assert st.get("status") == "completed", f"Analysis did not complete for {name}! Error: {st.get('error')}"
            print(f"[LIVE SERVER] ✅ {name} 100% COMPLETE on live HTTP server!")
            
            # Test Exports
            for exp in ["markdown", "json", "zip"]:
                req = urllib.request.Request(f"http://127.0.0.1:5000/api/export/{exp}/{task_id}")
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    print(f"[LIVE SERVER] ✅ /api/export/{exp}/{task_id} => HTTP 200 ({len(data)} bytes)")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
            
    print("\n[LIVE SERVER] 🎉 All live HTTP tests passed cleanly!")

if __name__ == "__main__":
    test_live_server()
