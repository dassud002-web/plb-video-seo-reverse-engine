#!/usr/bin/env python3
"""
Test Suite for Bug #001: Uploaded Video Cannot Be Inspected
===========================================================
Covers all requirements from STEP 4 and STEP 5:
- Uploading a video then inspecting by bare original name (e.g. ref-video.mp4)
- Uploading a video then inspecting by upload_id
- Inspecting by sanitized path
- Inspecting filenames with spaces
- Inspecting filenames with non-English characters (Cyrillic, etc.)
- Verification that Resolution != "?x?" and Codec != "unknown"
- Full technical metadata: duration, width/height, FPS, codec, size
- Attempting to inspect non-existent file returns proper 404 error
- Attempting to inspect invalid ID returns proper error
- Security checks prevent traversal outside allowed directories
- Exact local path workflow still works
"""

import io
import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from story_forge.app import app, UPLOAD_DIR, resolve_video_target, UPLOADED_ASSETS

class TestBug001InspectUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

        # Locate sample video bytes for testing
        cls.sample_video_path = project_root / "story_forge" / "tests" / "generic_unseen.mp4"
        if not cls.sample_video_path.exists():
            candidates = list((project_root / "temp_uploads").glob("*.mp4"))
            if candidates:
                cls.sample_video_path = candidates[0]
            else:
                raise FileNotFoundError("No sample video found for upload tests.")

        with open(cls.sample_video_path, "rb") as f:
            cls.video_bytes = f.read()

    def test_01_upload_and_inspect_by_bare_original_name(self):
        """Test inspecting by bare original name 'ref-video.mp4' after upload."""
        filename = "ref-video.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.get_json()
        self.assertEqual(upload_data["status"], "ok")
        self.assertEqual(upload_data["original_name"], filename)

        # Inspect using bare original name as path (reproducing user scenario)
        scan_res = self.client.post("/api/scan", json={
            "path": filename
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")

        info = scan_data["file_info"]
        self.assertEqual(info["name"], filename)
        self.assertNotEqual(info["resolution"], "?x?")
        self.assertIn("x", info["resolution"])
        self.assertNotEqual(info["codec"], "unknown")
        self.assertTrue(info["duration_seconds"] > 0)
        self.assertTrue(info["fps"] > 0)
        self.assertTrue(info["size_mb"] > 0)
        self.assertTrue(Path(info["path"]).exists())

    def test_02_upload_and_inspect_by_upload_id(self):
        """Test inspecting by upload_id directly."""
        filename = "test_id_inspect.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.get_json()
        upload_id = upload_data["upload_id"]

        # Inspect using upload_id without explicit path
        scan_res = self.client.post("/api/scan", json={
            "upload_id": upload_id
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")
        info = scan_data["file_info"]
        self.assertEqual(info["name"], filename)
        self.assertEqual(info["upload_id"], upload_id)
        self.assertNotEqual(info["resolution"], "?x?")
        self.assertNotEqual(info["codec"], "unknown")

    def test_03_inspect_by_sanitized_server_path(self):
        """Test inspecting by the sanitized server path returned by /api/upload."""
        filename = "test_sanitized_path.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)
        upload_data = upload_res.get_json()
        server_path = upload_data["path"]

        scan_res = self.client.post("/api/scan", json={
            "path": server_path,
            "original_name": filename
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")
        info = scan_data["file_info"]
        self.assertEqual(info["name"], filename)
        self.assertNotEqual(info["resolution"], "?x?")
        self.assertNotEqual(info["codec"], "unknown")

    def test_04_inspect_filenames_with_spaces(self):
        """Test uploading and inspecting filenames with multiple spaces."""
        filename = "Space Cadet Video Final Cut 2026.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)

        # Inspect using bare filename with spaces
        scan_res = self.client.post("/api/scan", json={
            "path": filename
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")
        self.assertEqual(scan_data["file_info"]["name"], filename)
        self.assertNotEqual(scan_data["file_info"]["resolution"], "?x?")
        self.assertNotEqual(scan_data["file_info"]["codec"], "unknown")

    def test_05_inspect_filenames_with_non_english_characters(self):
        """Test uploading and inspecting filenames with Cyrillic / non-English characters."""
        filename = "Татьяна Тумилиевич_Winter colobok, forest c_4457078457880345_1080p_20261007.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)

        # Inspect by bare non-English original name
        scan_res = self.client.post("/api/scan", json={
            "path": filename
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")
        self.assertEqual(scan_data["file_info"]["name"], filename)
        self.assertNotEqual(scan_data["file_info"]["resolution"], "?x?")
        self.assertNotEqual(scan_data["file_info"]["codec"], "unknown")

    def test_06_non_existent_file_returns_404(self):
        """Test that inspecting a non-existent file returns proper 404 error."""
        non_existent_name = "completely_fictional_missing_video_9999.mp4"
        scan_res = self.client.post("/api/scan", json={
            "path": non_existent_name
        })
        self.assertEqual(scan_res.status_code, 404)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "error")
        self.assertIn("File does not exist", scan_data["error"])

    def test_07_invalid_upload_id_returns_404(self):
        """Test that inspecting an invalid or unknown upload_id returns proper 404 error."""
        scan_res = self.client.post("/api/scan", json={
            "upload_id": "nonexistent-id-00000000"
        })
        self.assertEqual(scan_res.status_code, 404)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "error")
        self.assertIn("not found", scan_data["error"].lower())

    def test_08_security_path_traversal_prevention(self):
        """Test that path traversal attempts are rejected."""
        traversal_attempts = [
            "../../../../windows/system32/cmd.exe",
            "..\\..\\system32\\calc.exe",
            "C:\\Windows\\System32\\notepad.exe",
            "/etc/passwd"
        ]
        for bad_path in traversal_attempts:
            scan_res = self.client.post("/api/scan", json={
                "path": bad_path
            })
            # Must return 400, 403, or 404, never 200
            self.assertIn(scan_res.status_code, [400, 403, 404])
            scan_data = scan_res.get_json()
            self.assertEqual(scan_data["status"], "error")

    def test_09_exact_local_path_workflow(self):
        """Test that candidate buttons or exact local path inspection still works."""
        exact_path = str(self.sample_video_path.resolve())
        scan_res = self.client.post("/api/scan", json={
            "path": exact_path
        })
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertEqual(scan_data["status"], "ok")
        info = scan_data["file_info"]
        self.assertEqual(info["name"], self.sample_video_path.name)
        self.assertNotEqual(info["resolution"], "?x?")
        self.assertNotEqual(info["codec"], "unknown")
        self.assertTrue(info["duration_seconds"] > 0)
        self.assertTrue(info["fps"] > 0)

    def test_10_analyze_with_resolved_bare_filename(self):
        """Test that /api/analyze also works with bare original filename after upload."""
        filename = "ref-analyze-test.mp4"
        upload_res = self.client.post("/api/upload", data={
            "file": (io.BytesIO(self.video_bytes), filename, "video/mp4")
        }, content_type="multipart/form-data")
        self.assertEqual(upload_res.status_code, 200)

        analyze_res = self.client.post("/api/analyze", json={
            "path": filename,
            "target_count": 50,
            "universe_mode": False
        })
        self.assertEqual(analyze_res.status_code, 200)
        analyze_data = analyze_res.get_json()
        self.assertEqual(analyze_data["status"], "ok")
        self.assertIn("task_id", analyze_data)

if __name__ == "__main__":
    unittest.main()
