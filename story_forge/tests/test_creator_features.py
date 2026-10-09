#!/usr/bin/env python3
"""
Creator-Centric Workflow & Model Tests for PLB Studio
=====================================================
Validates:
1. Google Veo 2 Prompt Compiler Adapter (Cinematic video directives)
2. Midjourney v6.1 Prompt Compiler Adapter (High-CTR Cover Art)
3. Aspect Ratio switching (9:16 vs 16:9) across adapters
4. Batch 6-shot prompts generation
5. Clean Markdown Production Package generation
6. Production Markdown export endpoint
7. Creator Social Media Schedule CSV export endpoint
"""

import unittest
import csv
import io
from story_forge.app import app
from story_forge.engine.prompt_compiler import (
    GoogleVeo2Adapter,
    MidjourneyAdapter,
    compile_prompt_package
)
from story_forge.engine.production_pipeline import (
    produce_story_package,
    format_production_package_markdown
)
from story_forge.storage.db import (
    save_session,
    save_stories_batch,
    save_production_package
)

class TestCreatorFeatures(unittest.TestCase):
    def setUp(self):
        self.mock_dna = {
            "characters": [{"name": "White Silkie", "species": "Chicken"}],
            "setting": "Rustic Farmyard Run",
            "visual_style": "Golden Hour Natural Documentary",
            "camera_style": "Ground-level low angle dynamic tracking",
            "color_palette": ["Lush Natural Green", "Warm Terracotta", "High-Luminance White"]
        }
        self.mock_story = {
            "story_id": "TEST-CREATOR-01",
            "title": "Silkie vs Bubble Machine",
            "one_line_premise": "A curious White Silkie encounters an automated bubble machine.",
            "hook": "Extreme low-angle close-up of White Silkie staring down floating iridescent spheres.",
            "conflict": "Silkie pecks at a bubble which vanishes with a micro-pop.",
            "twist": "A giant cluster of bubbles floats directly above, creating shimmering reflections.",
            "payoff": "Silkie does an ecstatic celebratory head-feather shake straight into the lens.",
            "characters": [{"name": "White Silkie", "species": "Chicken"}],
            "setting": "Rustic Farmyard Run",
            "objects": [{"name": "Bubble Machine"}]
        }
        self.mock_hero = {
            "composition": "Rule-of-thirds low angle, Silkie on left third facing center",
            "lighting": "Golden hour rim light with soft fill",
            "color_palette_lock": ["Lush Natural Green", "High-Luminance White", "Warm Amber"],
            "camera_lens": "50mm prime f/2.8 shallow depth with creamy background bokeh"
        }
        self.mock_cont = {
            "character_morphology_rules": ["Preserve fluffy crest feathers", "Zero distortion"],
            "environment_rules": ["Preserve farmyard wooden rails"],
            "immutable_traits": ["Object scale: Bubble Machine proportional to Silkie"]
        }

    def test_google_veo_2_adapter_and_validation(self):
        adapter = GoogleVeo2Adapter()
        res_vertical = adapter.compile(
            self.mock_story, self.mock_dna, self.mock_hero, self.mock_cont, aspect_ratio="9:16"
        )
        self.assertEqual(res_vertical.model_id, "google_veo_2")
        self.assertEqual(res_vertical.validation.status, "PASS")
        self.assertEqual(res_vertical.validation.score_pct, 100)
        self.assertIn("9:16", res_vertical.prompt_text)
        self.assertIn("White Silkie", res_vertical.prompt_text)
        self.assertIn("cinematic", res_vertical.prompt_text.lower())

        # Test landscape
        res_land = adapter.compile(
            self.mock_story, self.mock_dna, self.mock_hero, self.mock_cont, aspect_ratio="16:9"
        )
        self.assertIn("16:9", res_land.prompt_text)

    def test_midjourney_adapter_and_validation(self):
        adapter = MidjourneyAdapter()
        res_vertical = adapter.compile(
            self.mock_story, self.mock_dna, self.mock_hero, self.mock_cont, aspect_ratio="9:16"
        )
        self.assertEqual(res_vertical.model_id, "midjourney_v6")
        self.assertEqual(res_vertical.validation.status, "PASS")
        self.assertEqual(res_vertical.validation.score_pct, 100)
        self.assertIn("--ar 9:16", res_vertical.prompt_text)
        self.assertIn("--v 6.1", res_vertical.prompt_text)
        self.assertIn("White Silkie", res_vertical.prompt_text)

        # Test landscape
        res_land = adapter.compile(
            self.mock_story, self.mock_dna, self.mock_hero, self.mock_cont, aspect_ratio="16:9"
        )
        self.assertIn("--ar 16:9", res_land.prompt_text)

    def test_batch_shots_prompt(self):
        compiled = compile_prompt_package(
            story=self.mock_story,
            story_dna=self.mock_dna,
            hero_frame=self.mock_hero,
            continuity_lock=self.mock_cont
        )
        batch = compiled.get("batch_shots_prompt", "")
        self.assertTrue(len(batch) > 100)
        self.assertIn("Shot 1", batch)
        self.assertIn("Shot 6", batch)

    def test_format_production_package_markdown(self):
        pkg = produce_story_package(self.mock_story, self.mock_dna, aspect_ratio="9:16")
        md = pkg.get("markdown_package", "")
        self.assertTrue(len(md) > 500)
        self.assertIn("# 🎬 PRODUCTION PACKAGE:", md)
        self.assertIn("## ⏱️ 1. 15-SECOND SHORT-FORM PRODUCTION SCRIPT", md)
        self.assertIn("## 🎬 2. 6-SHOT VIRAL STORYBOARD", md)
        self.assertIn("## 🤖 5. MODEL-AWARE AI VIDEO PROMPTS", md)
        self.assertIn("Google Veo 2", md)
        self.assertIn("Midjourney v6.1", md)
        self.assertIn("## 📱 7. MULTI-PLATFORM VIRAL CAPTIONS", md)
        self.assertIn("## 📈 8. EVIDENCE-BASED SEO & DISCOVERY PACK", md)

    def test_production_markdown_endpoint(self):
        client = app.test_client()
        sess_id = "test_creator_sess"
        save_session(
            sess_id,
            {"source_video_name": "test.mp4", "source_video_path": "test.mp4"},
            self.mock_dna,
            {}
        )
        save_stories_batch(sess_id, [self.mock_story])

        # GET /api/export/production_markdown/<sess_id>/<story_id>
        res = client.get(f"/api/export/production_markdown/{sess_id}/{self.mock_story['story_id']}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "text/markdown")
        data_text = res.data.decode("utf-8")
        self.assertIn(self.mock_story["title"], data_text)
        self.assertIn("Google Veo 2", data_text)

    def test_creator_schedule_csv_endpoint(self):
        client = app.test_client()
        sess_id = "test_schedule_sess"
        save_session(
            sess_id,
            {"source_video_name": "test.mp4", "source_video_path": "test.mp4"},
            self.mock_dna,
            {}
        )
        save_stories_batch(sess_id, [self.mock_story])

        res = client.get(f"/api/export/creator_schedule_csv/{sess_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "text/csv")
        csv_text = res.data.decode("utf-8")
        reader = csv.reader(io.StringIO(csv_text))
        rows = list(reader)
        self.assertGreaterEqual(len(rows), 2)
        headers = rows[0]
        self.assertIn("Viral Hook (0-3s)", headers)
        self.assertIn("TikTok Caption", headers)
        self.assertIn("Instagram Reels Caption", headers)
        self.assertIn("YouTube Shorts Caption", headers)
        self.assertIn("Google Veo 2 Prompt", headers)

if __name__ == "__main__":
    unittest.main()
