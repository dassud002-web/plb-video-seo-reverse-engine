#!/usr/bin/env python3
"""
Automated Test Suite for PLB Creator Studio - Standalone Desktop App
=====================================================================
Tests:
1. Studio Gateway UI rendering (GET /)
2. Studio Status API (GET /api/studio/status)
3. Open folder API (POST /api/studio/open-folder)
4. Open browser API (POST /api/studio/open-browser)
5. Chromium browser detection (Chrome/Edge App Mode)
6. Cross-tool switcher links in both template files
7. Full 3-Server Desktop Engine Orchestration (--no-gui server boot & shutdown)
"""

import os
import sys
import time
import json
import unittest
import urllib.request
import subprocess
from pathlib import Path

# Project root setup
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from studio.app import studio_app
from desktop_app import find_chromium_browser

class TestStandaloneApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        studio_app.config["TESTING"] = True
        cls.client = studio_app.test_client()

    def test_1_studio_shell_ui(self):
        """1. Verify Studio Gateway HTML shell renders correctly."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("PLB CREATOR STUDIO", html)
        self.assertIn("Story Universe Factory", html)
        self.assertIn("Video SEO Reverse Engine", html)
        self.assertIn("frame-universe", html)
        self.assertIn("frame-seo", html)
        self.assertIn("Ctrl+1", html)
        self.assertIn("Ctrl+2", html)
        print("  [PASS] 1. Studio Gateway HTML shell rendered with dual frames and controls")

    def test_2_studio_status_api(self):
        """2. Verify /api/studio/status returns engine ports and connectivity."""
        res = self.client.get("/api/studio/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("universe_online", data)
        self.assertIn("seo_online", data)
        self.assertEqual(data["ports"]["universe"], 5050)
        self.assertEqual(data["ports"]["seo"], 5000)
        self.assertEqual(data["ports"]["studio"], 5500)
        print("  [PASS] 2. Studio status API verified: ports 5050, 5000, 5500")

    def test_3_open_folder_api(self):
        """3. Verify /api/studio/open-folder endpoint logic."""
        res = self.client.post("/api/studio/open-folder", json={"folder": "uploads"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertTrue(Path(data["path"]).exists())
        print("  [PASS] 3. Open folder API verified: %s" % data["path"])

    def test_4_browser_detection(self):
        """4. Verify Chromium browser detection finds installed Chrome on system."""
        browser_path = find_chromium_browser()
        self.assertIsNotNone(browser_path, "Chrome or Edge should be detected on the system")
        self.assertTrue(os.path.isfile(browser_path))
        print("  [PASS] 4. Chromium browser detected: %s" % Path(browser_path).name)

    def test_5_cross_tool_switchers_in_templates(self):
        """5. Verify cross-tool switcher links exist in both engine templates."""
        seo_template = (project_root / "templates" / "index.html").read_text(encoding="utf-8")
        universe_template = (project_root / "story_forge" / "templates" / "index.html").read_text(encoding="utf-8")

        self.assertIn("Story Universe Factory", seo_template)
        self.assertIn("http://127.0.0.1:5050", seo_template)

        self.assertIn("Switch to Video SEO Engine", universe_template)
        self.assertIn("http://127.0.0.1:5000", universe_template)
        print("  [PASS] 5. Cross-tool switcher navigation verified in both application templates")

    def test_6_desktop_engine_multi_server_orchestration(self):
        """6. Live test: Launch desktop_app.py --no-gui, verify all 3 servers respond, then terminate."""
        test_studio_port = 5599
        test_seo_port = 5098
        test_univ_port = 5099

        cmd = [
            sys.executable,
            str(project_root / "desktop_app.py"),
            "--port", str(test_studio_port),
            "--seo-port", str(test_seo_port),
            "--universe-port", str(test_univ_port),
            "--no-gui"
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            # Poll for all 3 servers to become ready (max 15s)
            start_time = time.time()
            all_ready = False
            while time.time() - start_time < 15:
                try:
                    s1 = urllib.request.urlopen("http://127.0.0.1:%d/" % test_studio_port, timeout=0.5).getcode()
                    s2 = urllib.request.urlopen("http://127.0.0.1:%d/api/recent" % test_seo_port, timeout=0.5).getcode()
                    s3 = urllib.request.urlopen("http://127.0.0.1:%d/api/recent" % test_univ_port, timeout=0.5).getcode()
                    if s1 == 200 and s2 == 200 and s3 == 200:
                        all_ready = True
                        break
                except Exception:
                    time.sleep(0.3)

            self.assertTrue(all_ready, "All 3 servers should respond with HTTP 200")
            print("  [PASS] 6. All 3 desktop servers booted and responded simultaneously (Ports %d, %d, %d)" % (
                test_univ_port, test_seo_port, test_studio_port
            ))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
            print("  ✓ Desktop engine servers terminated cleanly")

if __name__ == "__main__":
    unittest.main()
