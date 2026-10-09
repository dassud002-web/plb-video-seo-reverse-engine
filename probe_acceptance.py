"""Real-video acceptance: build a real session, produce a real package, export it."""
import sys
sys.path.insert(0, '/c/Users/Admin/Desktop/google-project')

import io
import json
import time
import uuid
from pathlib import Path

from story_forge.app import app, UPLOAD_DIR
from story_forge.storage.db import save_session, save_stories_batch, save_production_package
from story_forge.engine.video_story_extractor import extract_video_story_evidence
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.story_generator import generate_50_root_stories
from story_forge.engine.production_pipeline import produce_story_package, validate_production_package

assert sys.platform.startswith('win'), "run under git-bash"
ROOT = Path(r'C:\Users\Admin\Desktop\google-project')
INPUT = ROOT / 'input'
UPLOADS = ROOT / 'temp_uploads'
client = app.test_client()

def step(title):
    print(f"\n=== {title} ===")

# Load a real video: prefer input/ref-video.mp4 (live reference), else any mp4
video_path = INPUT / 'ref-video.mp4'
if not video_path.exists():
    cands = list(INPUT.glob('*.mp4')) + list(UPLOADS.glob('*.mp4'))
    if cands:
        video_path = cands[0]
    else:
        print("NO REAL VIDEO FOUND — aborting real-video acceptance")
        sys.exit(0)
print(f"=== Real video: {video_path.name}  ({video_path.stat().st_size} bytes) ===")

# Endpoint 1: upload
step("1. API upload")
data = {"file": (io.BytesIO(video_path.read_bytes()), video_path.name, "video/mp4")}
res = client.post("/api/upload", data=data, content_type="multipart/form-data")
print("status:", res.status_code)
print("body:", res.get_json())
up = res.get_json()
saved = Path(up["path"])
print("saved exists:", saved.exists(), "within upload dir:", str(saved.resolve()).startswith(str(UPLOAD_DIR.resolve())))

# Endpoint 2: scan
step("2. API scan")
res = client.post("/api/scan", json={"path": str(saved), "original_name": video_path.name})
print("status:", res.status_code)
info = res.get_json().get("file_info", {})
print("resolution:", info.get("resolution"), "duration:", info.get("duration_seconds"), "fps:", info.get("fps"))

# Endpoint 3: analyze (async)
step("3. API analyze")
res = client.post("/api/analyze", json={
    "path": str(saved), "original_name": video_path.name,
    "target_count": 50, "threshold": 0.70, "universe_mode": False
})
task_id = res.get_json()["task_id"]
print("task_id:", task_id)
completed = False
sess_id = None
for _ in range(60):
    time.sleep(0.5)
    res = client.get(f"/api/status/{task_id}")
    st = res.get_json()
    if st.get("status") == "completed":
        completed = True
        sess_id = st.get("session_id")
        break
    elif st.get("status") == "error":
        print("ERROR:", st.get("error"))
        break
print("completed:", completed, "session_id:", sess_id)

# Verify session
step("4. Session verification")
sess = {}
try:
    sess = client.get(f"/api/session/{sess_id}")
except Exception as e:
    print("session get err", e)
if sess.status_code == 200:
    sd = sess.get_json().get("story_dna", {})
    print("source_video_name:", sd.get("source_video"))
    print("confidence:", sd.get("confidence"))
    print("cv_limitation_disclosed:", sd.get("cv_limitation_disclosed"))
    print("characters[0]:", sd.get("characters")[0] if sd.get("characters") else None)
    print("core_premise:", (sd.get("core_premise") or "")[:90])

# Endpoint 5: production package
step("5. API produce")
if sess_id:
    stories = client.get(f"/api/session/{sess_id}")
    if stories.status_code == 200:
        all_stories = stories.get_json().get("stories", [])
        if all_stories:
            story = all_stories[0]
            res = client.post(f"/api/produce/{sess_id}/{story['story_id']}", json={"aspect_ratio": "9:16"})
            print("produce status:", res.status_code)
            pkg = res.get_json().get("package", {})
            print("package keys:", list(pkg.keys())[:8])
            print("seedance present:", bool(pkg.get("seedance_25_prompt")))
            print("veo present:", bool(pkg.get("veo_prompt")))
            # validate
            warnings = validate_production_package(pkg)
            print("field warnings:", warnings)

# Endpoint 6: export markdown (individual story)
step("6. API export production_markdown")
if sess_id:
    stories = client.get(f"/api/session/{sess_id}")
    if stories.status_code == 200:
        all_stories = stories.get_json().get("stories", [])
        if all_stories:
            story = all_stories[0]
            res = client.get(f"/api/export/production_markdown/{sess_id}/{story['story_id']}")
            print("export status:", res.status_code, "mimetype:", res.mimetype, "chars:", len(res.data))
            print("has title:", story['story_id'] in res.data.decode('utf-8', errors='replace'))

# Endpoint 7: full universe zip export (if universe_mode session)
step("7. Export universe JSON")
if sess_id:
    res = client.get(f"/api/export/universe_json/{sess_id}")
    print("export status:", res.status_code, "bytes:", len(res.data), "mimetype:", res.mimetype)

print("\n=== REAL-VIDEO ACCEPTANCE COMPLETE ===")
