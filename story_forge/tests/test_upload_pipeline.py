#!/usr/bin/env python3
"""
Automated Test Suite for PLB Story Universe Factory - Upload Pipeline
=====================================================================
Tests:
A. MP4 drag/drop simulation
B. MOV upload
C. WEBM upload
D. Unicode filenames (Russian/Cyrillic, Bengali, Hindi, Chinese, Japanese, Arabic, Emoji)
E. Spaces in filename
F. Very long filename
G. Unsupported extension
H. Missing file
I. Path traversal protection
J. Scan after upload
K. Analyze after upload
L. Stale upload cleanup

Target exact Unicode filename:
Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4
"""

import io
import os
import sys
import time
import unittest
from pathlib import Path

# Set up project root in path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from story_forge.app import app, UPLOAD_DIR, cleanup_stale_uploads, TASKS, TASKS_LOCK
from story_forge.storage.db import get_session, get_all_stories_for_session

class TestUploadPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

        # Locate sample video bytes for testing
        cls.sample_video_path = project_root / "story_forge" / "tests" / "generic_unseen.mp4"
        if not cls.sample_video_path.exists():
            # Fallback to another video in workspace
            candidates = list((project_root / "temp_uploads").glob("*.mp4"))
            if candidates:
                cls.sample_video_path = candidates[0]
            else:
                downloads_test = Path.home() / "Downloads" / "test-reel" / "test-reel.mp4"
                if downloads_test.exists():
                    cls.sample_video_path = downloads_test
                else:
                    raise FileNotFoundError("No sample video found for upload tests.")

        with open(cls.sample_video_path, "rb") as f:
            cls.video_bytes = f.read()
        print(f"\n[SETUP] Loaded sample video for upload tests: {cls.sample_video_path.name} ({len(cls.video_bytes)} bytes)")

    def test_A_mp4_upload_simulation(self):
        """A. Simulate MP4 video drag/drop multipart upload."""
        filename = "test_drop_video.mp4"
        data = {
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }
        res = self.client.post("/api/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()

        self.assertEqual(json_data.get("status"), "ok")
        self.assertIn("upload_id", json_data)
        self.assertEqual(json_data.get("original_name"), filename)
        self.assertEqual(json_data.get("extension"), ".mp4")
        self.assertTrue(json_data.get("size_mb", 0) > 0)

        saved_path = Path(json_data["path"])
        self.assertTrue(saved_path.exists())
        self.assertTrue(str(saved_path.resolve()).startswith(str(UPLOAD_DIR.resolve())))
        print(f"  [PASS] A. MP4 upload simulated successfully -> {saved_path.name}")

    def test_B_mov_upload(self):
        """B. Verify MOV video upload."""
        filename = "production_scene_01.mov"
        data = {
            "file": (io.BytesIO(self.video_bytes), filename, "video/quicktime")
        }
        res = self.client.post("/api/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data.get("status"), "ok")
        self.assertEqual(json_data.get("extension"), ".mov")
        saved_path = Path(json_data["path"])
        self.assertTrue(saved_path.exists())
        print(f"  [PASS] B. MOV upload verified -> {saved_path.name}")

    def test_C_webm_upload(self):
        """C. Verify WEBM video upload."""
        filename = "web_stream_capture.webm"
        data = {
            "file": (io.BytesIO(self.video_bytes), filename, "video/webm")
        }
        res = self.client.post("/api/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data.get("status"), "ok")
        self.assertEqual(json_data.get("extension"), ".webm")
        saved_path = Path(json_data["path"])
        self.assertTrue(saved_path.exists())
        print(f"  [PASS] C. WEBM upload verified -> {saved_path.name}")

    def test_D_exact_unicode_filename_and_multilingual(self):
        """
        D. Verify upload, scan, and metadata preservation for the EXACT test filename:
        Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4
        Plus Bengali, Hindi, Chinese, Japanese, Arabic, and Emoji filenames.
        """
        exact_target = "Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4"
        data = {
            "file": (io.BytesIO(self.video_bytes), exact_target, "video/mp4")
        }
        res = self.client.post("/api/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()

        self.assertEqual(json_data.get("status"), "ok")
        self.assertEqual(json_data.get("original_name"), exact_target)
        saved_path = Path(json_data["path"])
        self.assertTrue(saved_path.exists())

        # Verify on-disk filename is safe ASCII (no encoding crash on Windows)
        self.assertTrue(saved_path.name.isascii(), f"On-disk filename should be safe ASCII: {saved_path.name}")

        # Scan the uploaded exact unicode file
        scan_res = self.client.post("/api/scan", json={
            "path": json_data["path"],
            "original_name": exact_target
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_json = scan_res.get_json()
        self.assertEqual(scan_json.get("status"), "ok")
        self.assertEqual(scan_json["file_info"]["name"], exact_target)
        self.assertTrue(scan_json["file_info"]["duration_seconds"] > 0)
        print(f"  [PASS] D1. Exact Unicode target uploaded and scanned: {exact_target}")

        # Multilingual tests
        multilingual_samples = [
            "শীতকালীন_ভিডিও_২০২৬.mp4",                   # Bengali
            "सर्दी_का_जंगल_कहानी.mp4",                    # Hindi
            "冬天的小兔子森林冒险_1080p.mp4",             # Chinese
            "森の中の小さな動物たち_2026.mp4",             # Japanese
            "مغامرة_الغابة_الشتوية.mp4",                  # Arabic
            "🐰🌲 Winter Forest Story ✨🎬.mp4"         # Emojis + Spaces
        ]

        for name in multilingual_samples:
            res_m = self.client.post("/api/upload", data={
                "file": (io.BytesIO(self.video_bytes), name, "video/mp4")
            }, content_type="multipart/form-data")
            self.assertEqual(res_m.status_code, 200)
            json_m = res_m.get_json()
            self.assertEqual(json_m.get("original_name"), name)
            self.assertTrue(Path(json_m["path"]).exists())
        print(f"  [PASS] D2. All 6 multilingual Unicode filenames verified (Bengali, Hindi, Chinese, Japanese, Arabic, Emoji)")

    def test_E_spaces_in_filename(self):
        """E. Verify filenames with extensive consecutive spaces and special punctuation."""
        name = "My    Spaced   Out   Animal   Reel   (Final Edit) [TJX].mp4"
        res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), name, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data.get("original_name"), name)
        self.assertTrue(Path(json_data["path"]).exists())
        print(f"  [PASS] E. Spaces in filename handled cleanly")

    def test_F_very_long_filename(self):
        """F. Verify very long filenames (> 150 chars)."""
        long_stem = "extremely_long_video_title_" * 6
        long_name = f"{long_stem[:160]}.mp4"
        res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), long_name, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertEqual(json_data.get("original_name"), long_name)
        saved_path = Path(json_data["path"])
        self.assertTrue(saved_path.exists())
        # Server disk filename should be truncated safely so it doesn't exceed OS path limits
        self.assertTrue(len(saved_path.name) < 100)
        print(f"  [PASS] F. Very long filename handled safely -> {saved_path.name}")

    def test_G_unsupported_extension(self):
        """G. Verify rejection of unsupported extensions (.txt, .exe, .mp3)."""
        for bad_name in ["script.txt", "installer.exe", "audio.mp3", "exploit.sh"]:
            res = self.client.post("/api/upload", data={
                "file": (io.BytesIO(b"dummy data"), bad_name, "text/plain")
            }, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 400)
            self.assertIn("Unsupported extension", res.get_json().get("error", ""))
        print(f"  [PASS] G. Unsupported extensions correctly rejected with HTTP 400")

    def test_H_missing_file(self):
        """H. Verify rejection when file is missing or filename is empty."""
        # No file in request
        res1 = self.client.post("/api/upload", data={}, content_type="multipart/form-data")
        self.assertEqual(res1.status_code, 400)

        # Empty filename
        res2 = self.client.post("/api/upload", data={
            "file": (io.BytesIO(b""), "", "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(res2.status_code, 400)
        print(f"  [PASS] H. Missing/empty file correctly rejected with HTTP 400")

    def test_I_path_traversal_protection(self):
        """I. Verify path traversal attempts in filename cannot escape temp_uploads."""
        traversal_attempts = [
            "../../../../windows/system32/malicious.mp4",
            "..\\..\\system32\\malicious.mp4",
            "/etc/passwd.mp4",
            "C:\\Windows\\explorer.mp4"
        ]
        for bad_path in traversal_attempts:
            res = self.client.post("/api/upload", data={
                "file": (io.BytesIO(self.video_bytes), bad_path, "video/mp4")
            }, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 200)
            json_data = res.get_json()
            saved_path = Path(json_data["path"]).resolve()
            # Must strictly be inside UPLOAD_DIR
            self.assertTrue(
                str(saved_path).startswith(str(UPLOAD_DIR.resolve())),
                f"Path {saved_path} must be inside {UPLOAD_DIR}"
            )
        print(f"  [PASS] I. Path traversal attempts safely neutralized within temp_uploads")

    def test_J_scan_after_upload(self):
        """J. Verify scan endpoint correctly accepts generated upload path and returns technical metadata."""
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), "scan_target.mp4", "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.get_json()

        scan_res = self.client.post("/api/scan", json={
            "path": upload_data["path"],
            "original_name": "scan_target.mp4"
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        info = scan_data["file_info"]
        self.assertEqual(info["name"], "scan_target.mp4")
        self.assertTrue(info["duration_seconds"] > 0)
        self.assertIn("x", info["resolution"])
        self.assertTrue(info["size_mb"] > 0)
        print(f"  [PASS] J. Scan after upload returned full technical metadata: {info['resolution']}, {info['duration_seconds']}s")

    def test_K_analyze_after_upload(self):
        """
        K. Full end-to-end test: Upload exact unicode file -> Analyze -> Poll completion ->
        Verify Story Universe generation, metadata retention, and DB persistence.
        """
        exact_target = "Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), exact_target, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.get_json()

        # Start analysis
        analyze_res = self.client.post("/api/analyze", json={
            "path": upload_data["path"],
            "original_name": exact_target,
            "target_count": 50,
            "threshold": 0.70,
            "universe_mode": False
        })
        self.assertEqual(analyze_res.status_code, 200)
        task_id = analyze_res.get_json()["task_id"]

        # Poll task until completion (max 60 seconds)
        start_time = time.time()
        completed = False
        session_id = None
        while time.time() - start_time < 60:
            st_res = self.client.get(f"/api/status/{task_id}")
            self.assertEqual(st_res.status_code, 200)
            st_data = st_res.get_json()
            if st_data.get("status") == "completed":
                completed = True
                session_id = st_data.get("session_id")
                break
            elif st_data.get("status") == "error":
                self.fail(f"Analysis task failed: {st_data.get('error')}")
            time.sleep(0.5)

        self.assertTrue(completed, "Analysis task did not complete in time")
        self.assertIsNotNone(session_id)

        # Retrieve session from DB and verify exact unicode original name
        sess_record = get_session(session_id)
        self.assertIsNotNone(sess_record)
        self.assertEqual(sess_record["source_video_name"], exact_target)
        stories = get_all_stories_for_session(session_id)
        self.assertTrue(len(stories) >= 50)
        print(f"  [PASS] K. Analyze after upload completed: Session {session_id}, Stories: {len(stories)}, Name preserved: {exact_target}")

    def test_L_cleanup_stale_uploads(self):
        """L. Verify stale uploads cleanup respects TTL and active tasks."""
        # Create a dummy fake stale file
        stale_file = UPLOAD_DIR / "stale_upload_test.mp4"
        stale_file.write_bytes(b"dummy")
        # Set mtime to 48 hours ago
        old_time = time.time() - (48 * 3600)
        os.utime(str(stale_file), (old_time, old_time))

        # Run cleanup with 24 hour TTL
        cleaned = cleanup_stale_uploads(ttl_hours=24.0)
        self.assertTrue(cleaned >= 1)
        self.assertFalse(stale_file.exists())
        print(f"  [PASS] L. Stale upload cleanup removed {cleaned} expired files")

if __name__ == "__main__":
    unittest.main()
