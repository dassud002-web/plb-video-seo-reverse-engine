#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

video_path = Path("story_forge/tests/generic_unseen.mp4")
video_bytes = video_path.read_bytes()

print("=" * 60)
print("LIVE REAL-SERVER VALIDATION ON WINDOWS (PORT 5050)")
print("=" * 60)

# 1. Upload ref-video.mp4
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    b"--" + boundary.encode("utf-8") + b"\r\n"
    b'Content-Disposition: form-data; name="file"; filename="ref-video.mp4"\r\n'
    b"Content-Type: video/mp4\r\n\r\n" + video_bytes + b"\r\n"
    b"--" + boundary.encode("utf-8") + b"--\r\n"
)

req = urllib.request.Request(
    "http://127.0.0.1:5050/api/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
with urllib.request.urlopen(req) as resp:
    upload_res = json.loads(resp.read().decode("utf-8"))
print("✓ 1. Upload Response:", upload_res)

# 2. Inspect with path: 'ref-video.mp4' (reproducing user scenario)
scan_payload = json.dumps({"path": "ref-video.mp4"}).encode("utf-8")
req2 = urllib.request.Request(
    "http://127.0.0.1:5050/api/scan",
    data=scan_payload,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req2) as resp2:
    scan_res = json.loads(resp2.read().decode("utf-8"))

print("\n✓ 2. Inspect Response for 'ref-video.mp4':")
print(json.dumps(scan_res, indent=2, ensure_ascii=False))

file_info = scan_res["file_info"]
assert scan_res["status"] == "ok", "Status must be ok"
assert file_info["name"] == "ref-video.mp4", "Name must match"
assert file_info["resolution"] != "?x?", f"Resolution must not be ?x?: got {file_info['resolution']}"
assert file_info["codec"] != "unknown", f"Codec must not be unknown: got {file_info['codec']}"
assert file_info["duration_seconds"] > 0, "Duration must be > 0"
assert file_info["fps"] > 0, "FPS must be > 0"
assert file_info["size_mb"] > 0, "Size MB must be > 0"
print(f"  -> Resolution: {file_info['resolution']}")
print(f"  -> Codec: {file_info['codec']}")
print(f"  -> FPS: {file_info['fps']}")
print(f"  -> Duration: {file_info['duration_seconds']}s")
print(f"  -> Size: {file_info['size_mb']} MB")

# 3. Test non-existent file returns 404
print("\n✓ 3. Testing non-existent file handling:")
scan_bad = json.dumps({"path": "non_existent_fake_video.mp4"}).encode("utf-8")
req_bad = urllib.request.Request(
    "http://127.0.0.1:5050/api/scan",
    data=scan_bad,
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req_bad) as resp_bad:
        print("ERROR: Expected 404 but got status", resp_bad.status)
        sys.exit(1)
except urllib.error.HTTPError as err:
    err_body = json.loads(err.read().decode("utf-8"))
    print(f"  -> Received expected HTTP {err.code}: {err_body}")
    assert err.code == 404
    assert "File does not exist: non_existent_fake_video.mp4" in err_body["error"]

# 4. Test Russian Unicode upload & inspect
print("\n✓ 4. Testing Russian Unicode file upload & inspect:")
cyrillic_name = "Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4"
body_ru = (
    b"--" + boundary.encode("utf-8") + b"\r\n"
    b'Content-Disposition: form-data; name="file"; filename="' + cyrillic_name.encode("utf-8") + b'"\r\n'
    b"Content-Type: video/mp4\r\n\r\n" + video_bytes + b"\r\n"
    b"--" + boundary.encode("utf-8") + b"--\r\n"
)
req_ru = urllib.request.Request(
    "http://127.0.0.1:5050/api/upload",
    data=body_ru,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
with urllib.request.urlopen(req_ru) as resp_ru:
    ru_upload_res = json.loads(resp_ru.read().decode("utf-8"))
print("  -> Upload OK, on-disk safe path:", ru_upload_res["path"])

scan_ru_payload = json.dumps({"path": cyrillic_name}).encode("utf-8")
req_ru_scan = urllib.request.Request(
    "http://127.0.0.1:5050/api/scan",
    data=scan_ru_payload,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req_ru_scan) as resp_ru_scan:
    ru_scan_res = json.loads(resp_ru_scan.read().decode("utf-8"))
print("  -> Inspect by bare Cyrillic name OK:")
print(f"     Name: {ru_scan_res['file_info']['name']}")
print(f"     Resolution: {ru_scan_res['file_info']['resolution']}")
print(f"     Codec: {ru_scan_res['file_info']['codec']}")
assert ru_scan_res["file_info"]["resolution"] != "?x?"
assert ru_scan_res["file_info"]["codec"] != "unknown"

print("\n" + "=" * 60)
print("ALL LIVE REAL-SERVER WINDOWS VALIDATIONS PASSED! 100% GREEN")
print("=" * 60)
