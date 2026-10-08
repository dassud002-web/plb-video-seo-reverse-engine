#!/usr/bin/env python3
"""
Test Suite for PLB Studio Model-Aware Prompt Compiler
=====================================================
Tests:
1. Seedance 2.5 Video Adapter (ByteDance / Volcengine standard, multi-shot timeline, refs, loop)
2. Universal Image Adapter (Midjourney / SDXL / FLUX / Imagen 3 declarative structure)
3. GPT Image Adapter (DALL-E 3 narrative descriptive prose paragraph)
4. Nano Banana Pro Adapter (Token-anchored bracketed syntax)
5. Validation Gate: PASS / PARTIAL / FAIL logic and check boundaries
6. Master compile_prompt_package: Full package with 6 shots, hero frame, continuity block
7. API Endpoints: GET /api/prompt-compiler/... and POST /api/prompt-compiler/compile
8. Diagnostic event logging integration
"""

import unittest
import json
from pathlib import Path
import tempfile
import shutil

from story_forge.engine.prompt_compiler import (
    Seedance25Adapter,
    UniversalImageAdapter,
    GPTImageAdapter,
    NanoBananaProAdapter,
    compile_prompt_package,
    ValidationReport,
    CompiledPromptResult
)
from story_forge.engine.production_pipeline import produce_story_package
from story_forge.app import app
from story_forge.diagnostics.activity_logger import get_diagnostic_state, log_event


class TestPromptCompiler(unittest.TestCase):

    def setUp(self):
        self.sample_story = {
            "story_id": "STORY-01",
            "title": "The Horseradish Hesitation",
            "characters": [{"name": "Barnaby the Rabbit", "species": "Holland Lop Rabbit"}],
            "objects": [{"name": "Sharp Fresh Horseradish Root"}],
            "setting": "Lush Vegetable Garden Enclosure",
            "hook": "Barnaby spots a pungent root twitching in the breeze",
            "twist": "A single exploratory sniff triggers a comic full-body sneeze shudder",
            "payoff": "Barnaby vigorously head-shakes directly at the camera in disbelief",
            "cinematic_prompt": "Cinematic shot of Barnaby eyeing the horseradish",
            "storyboard_6_shots": [
                {"shot_number": 1, "name": "The Hook", "duration": "00:00-00:03", "shot_type": "Close-Up", "camera_angle": "Low eye-level", "action": "Barnaby locks eyes with horseradish root."},
                {"shot_number": 2, "name": "The Approach", "duration": "00:03-00:06", "shot_type": "Medium Tracking", "camera_angle": "Ground push-in", "action": "Stealthy hop forward with twitching nose."},
                {"shot_number": 3, "name": "The Contact", "duration": "00:06-00:09", "shot_type": "Macro Shot", "camera_angle": "Extreme tight", "action": "Barnaby's whiskers brush the pungent root."},
                {"shot_number": 4, "name": "The Reaction", "duration": "00:09-00:11", "shot_type": "Medium Close-Up", "camera_angle": "Rapid zoom punch", "action": "Startled recoil and giant comic sneeze."},
                {"shot_number": 5, "name": "The Payoff", "duration": "00:11-00:14", "shot_type": "Medium Shot", "camera_angle": "Dutch tilt recovery", "action": "Comedic rapid head shake directly facing camera."},
                {"shot_number": 6, "name": "The Loop Reset", "duration": "00:14-00:15", "shot_type": "Return Medium", "camera_angle": "Slow pull-back", "action": "Barnaby resets to curious stance for infinite loop."}
            ],
            "hero_frame": {
                "composition": "Low-angle ground-level eye-line with Barnaby occupying the left third",
                "lighting": "Natural golden-hour side lighting with warm rim highlights",
                "color_palette": "Earthy forest greens, warm amber soil, clean white fur tones",
                "camera_lens": "50mm prime f/2.8 lens with shallow depth of field and soft background blur"
            },
            "continuity_lock": {
                "character_morphology": "Consistent Holland Lop floppy ears, dense white/grey fur texture, proportional anatomy",
                "environment_lock": "Persistent garden dirt floor, soft green leaf bedding, late-afternoon sun direction",
                "immutable_traits": ["True-to-life rabbit scale", "Zero cartoon warping", "Physical gravity and momentum"]
            }
        }

        self.sample_story_dna = {
            "characters": [{"name": "Barnaby the Rabbit", "species": "Holland Lop Rabbit"}],
            "objects": [{"name": "Sharp Fresh Horseradish Root"}],
            "setting": "Lush Vegetable Garden Enclosure",
            "palette": ["#4a7c59", "#d4a373", "#fefae0"],
            "cinematography": "Macro ground-level wildlife photography"
        }

    # ---------------------------------------------------------------------
    # 1. Seedance 2.5 Video Adapter Tests
    # ---------------------------------------------------------------------
    def test_seedance_25_adapter_structure_and_validation(self):
        result = Seedance25Adapter.compile(
            story=self.sample_story,
            story_dna=self.sample_story_dna,
            hero_frame=self.sample_story["hero_frame"],
            continuity_lock=self.sample_story["continuity_lock"],
            storyboard=self.sample_story["storyboard_6_shots"]
        )

        self.assertIsInstance(result, CompiledPromptResult)
        self.assertEqual(result.model_id, "seedance_25")
        self.assertEqual(result.output_type, "video")
        self.assertIn("[Seedance 2.5 Directive]", result.prompt_text)

        # Verify Base Sequence: Subject -> Action/Event -> Scene/Environment -> Visual Style -> Camera/Shot -> Sound
        self.assertIn("[Subject]:", result.prompt_text)
        self.assertIn("[Action/Event]:", result.prompt_text)
        self.assertIn("[Scene/Environment]:", result.prompt_text)
        self.assertIn("[Visual Style]:", result.prompt_text)
        self.assertIn("[Camera/Shot]:", result.prompt_text)
        self.assertIn("[Sound]:", result.prompt_text)

        # Verify Advanced Features
        self.assertIn("[Roles:", result.prompt_text)
        self.assertIn("@Subject1:", result.prompt_text)
        self.assertIn("@Object1:", result.prompt_text)
        self.assertIn("[Timeline]:", result.prompt_text)
        self.assertIn("[Continuity]:", result.prompt_text)
        self.assertIn("[Workflow]:", result.prompt_text)
        self.assertIn("First Frame Anchor", result.prompt_text)
        self.assertIn("Last Frame Anchor", result.prompt_text)

        # Structure dictionary
        expected_keys = [
            "Subject", "Action/Event", "Scene/Environment", "Visual Style",
            "Camera/Shot", "Sound", "References", "Timeline", "Continuity"
        ]
        for k in expected_keys:
            self.assertIn(k, result.structure, f"Missing structure key: {k}")

        # Validation Report
        val = result.validation
        self.assertEqual(val.status, "PASS")
        self.assertEqual(val.passed_checks, 9)
        self.assertEqual(val.total_checks, 9)
        self.assertEqual(val.score_pct, 100.0)
        self.assertEqual(len(val.warnings), 0)

    # ---------------------------------------------------------------------
    # 2. Universal Image Adapter Tests (Midjourney/SDXL/FLUX/Imagen)
    # ---------------------------------------------------------------------
    def test_universal_image_adapter_structure_and_validation(self):
        result = UniversalImageAdapter.compile(
            story=self.sample_story,
            story_dna=self.sample_story_dna,
            hero_frame=self.sample_story["hero_frame"],
            continuity_lock=self.sample_story["continuity_lock"]
        )

        self.assertEqual(result.model_id, "universal_image")
        self.assertEqual(result.output_type, "image")
        self.assertIn("Award-winning National Geographic wildlife photography", result.prompt_text)
        self.assertIn("Composition:", result.prompt_text)
        self.assertIn("Lighting:", result.prompt_text)

        # 10 Required Check Fields
        expected_checks = [
            "Subject", "Composition", "Environment", "Action", "Visual details",
            "Lighting", "Camera/framing", "Style", "Continuity", "Constraints"
        ]
        for c in expected_checks:
            self.assertIn(c, result.structure)
            self.assertTrue(result.validation.checks.get(c), f"Check failed for: {c}")

        self.assertEqual(result.validation.status, "PASS")
        self.assertEqual(result.validation.passed_checks, 10)
        self.assertEqual(result.validation.total_checks, 10)
        self.assertEqual(result.validation.score_pct, 100.0)

    # ---------------------------------------------------------------------
    # 3. GPT Image Adapter Tests (DALL-E 3 Prose)
    # ---------------------------------------------------------------------
    def test_gpt_image_adapter_narrative_prose(self):
        result = GPTImageAdapter.compile(
            story=self.sample_story,
            story_dna=self.sample_story_dna,
            hero_frame=self.sample_story["hero_frame"],
            continuity_lock=self.sample_story["continuity_lock"]
        )

        self.assertEqual(result.model_id, "gpt_image")
        self.assertEqual(result.output_type, "image")

        # GPT Image strictly avoids comma tag salad and uses flowing descriptive prose
        self.assertNotIn("8k, octane render, masterpiece, photorealistic", result.prompt_text.lower())
        self.assertIn("A realistic, high-detail photograph of", result.prompt_text)
        self.assertIn("Barnaby the Rabbit", result.prompt_text)

        self.assertEqual(result.validation.status, "PASS")
        self.assertEqual(result.validation.passed_checks, 10)
        self.assertEqual(result.validation.total_checks, 10)

    # ---------------------------------------------------------------------
    # 4. Nano Banana Pro Adapter Tests (Token Directives)
    # ---------------------------------------------------------------------
    def test_nano_banana_pro_token_directives(self):
        result = NanoBananaProAdapter.compile(
            story=self.sample_story,
            story_dna=self.sample_story_dna,
            hero_frame=self.sample_story["hero_frame"],
            continuity_lock=self.sample_story["continuity_lock"]
        )

        self.assertEqual(result.model_id, "nano_banana_pro")
        self.assertEqual(result.output_type, "image")

        # Check token brackets
        self.assertIn("[FOCAL_SUBJECT:", result.prompt_text)
        self.assertIn("[ACTION_TENSION:", result.prompt_text)
        self.assertIn("[SETTING_COMPOSITION:", result.prompt_text)
        self.assertIn("[LIGHTING_PALETTE:", result.prompt_text)
        self.assertIn("[OPTICS_DETAIL:", result.prompt_text)
        self.assertIn("[STYLE_QUALITY:", result.prompt_text)
        self.assertIn("[CONTINUITY_LOCK:", result.prompt_text)

        self.assertEqual(result.validation.status, "PASS")
        self.assertEqual(result.validation.passed_checks, 10)
        self.assertEqual(result.validation.total_checks, 10)

    # ---------------------------------------------------------------------
    # 5. Validation Gate Boundary & Failure Triggers
    # ---------------------------------------------------------------------
    def test_validation_gate_partial_and_fail(self):
        # Empty structure -> FAIL
        empty_structure = {}
        val_fail = Seedance25Adapter.validate(empty_structure)
        self.assertEqual(val_fail.status, "FAIL")
        self.assertEqual(val_fail.passed_checks, 0)
        self.assertGreater(len(val_fail.warnings), 0)

        # Incomplete structure with only 6/9 passing -> PARTIAL
        partial_structure = {
            "Subject": "Detailed subject string with sufficient length here",
            "Action/Event": "Detailed action string describing events with sufficient length",
            "Scene/Environment": "Outdoor lush garden environment",
            "Visual Style": "Award-winning wildlife photography style",
            "Camera/Shot": "Ground-level 50mm push-in tracking shot",
            "Sound": "Crisp Foley footsteps and acoustic music",
            "References": "",       # missing @
            "Timeline": "",         # missing [00:
            "Continuity": ""        # missing length
        }
        val_partial = Seedance25Adapter.validate(partial_structure)
        self.assertEqual(val_partial.status, "PARTIAL")
        self.assertEqual(val_partial.passed_checks, 6)

    # ---------------------------------------------------------------------
    # 6. Master compile_prompt_package Verification
    # ---------------------------------------------------------------------
    def test_master_compile_prompt_package(self):
        pkg = compile_prompt_package(
            story=self.sample_story,
            story_dna=self.sample_story_dna,
            hero_frame=self.sample_story["hero_frame"],
            continuity_lock=self.sample_story["continuity_lock"],
            storyboard=self.sample_story["storyboard_6_shots"]
        )

        self.assertEqual(pkg["overall_status"], "PASS")
        self.assertIn("models", pkg)
        self.assertIn("seedance_25", pkg["models"])
        self.assertIn("universal_image", pkg["models"])
        self.assertIn("gpt_image", pkg["models"])
        self.assertIn("nano_banana_pro", pkg["models"])

        # Check shortcuts
        self.assertTrue(len(pkg["seedance_25_prompt"]) > 50)
        self.assertTrue(len(pkg["universal_image_prompt"]) > 50)
        self.assertTrue(len(pkg["gpt_image_prompt"]) > 50)
        self.assertTrue(len(pkg["nano_banana_pro_prompt"]) > 50)
        self.assertTrue(len(pkg["hero_frame_prompt"]) > 50)
        self.assertTrue(len(pkg["continuity_block"]) > 30)

        # Check 6 shot-by-shot prompts
        shots = pkg["shot_by_shot_prompts"]
        self.assertEqual(len(shots), 6)
        for i, s in enumerate(shots, 1):
            self.assertEqual(s["shot_number"], i)
            self.assertTrue(len(s["prompt"]) > 20)
            self.assertIn(f"Shot {i}", s["prompt"])

    # ---------------------------------------------------------------------
    # 7. Production Pipeline Integration
    # ---------------------------------------------------------------------
    def test_production_pipeline_contains_prompt_package(self):
        prod_pkg = produce_story_package(self.sample_story, self.sample_story_dna)
        self.assertIn("prompt_package", prod_pkg)
        self.assertIn("compiled_prompts", prod_pkg)
        self.assertEqual(prod_pkg["prompt_package"]["overall_status"], "PASS")
        self.assertIn("seedance_prompt", prod_pkg)
        self.assertIn("veo_prompt", prod_pkg)
        # Check that seedance_prompt is now updated with Seedance 2.5
        self.assertIn("[Seedance 2.5 Directive]", prod_pkg["seedance_prompt"])
        self.assertIn("Barnaby the Rabbit", prod_pkg["veo_prompt"])
        self.assertIn("tracking shot", prod_pkg["veo_prompt"])

    # ---------------------------------------------------------------------
    # 8. Flask API Endpoints & Diagnostic Integration
    # ---------------------------------------------------------------------
    def test_prompt_compiler_endpoints_and_diagnostics(self):
        client = app.test_client()

        # POST /api/prompt-compiler/compile
        payload = {
            "story": self.sample_story,
            "story_dna": self.sample_story_dna,
            "hero_frame": self.sample_story["hero_frame"],
            "continuity_lock": self.sample_story["continuity_lock"],
            "session_id": "test_session_compile"
        }
        res = client.post("/api/prompt-compiler/compile", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["prompt_package"]["overall_status"], "PASS")

        # Verify diagnostic report logged PROMPT_COMPILED
        state = get_diagnostic_state()
        events = state.get("recent_events", [])
        compile_events = [e for e in events if e.get("event_type") == "PROMPT_COMPILED"]
        self.assertGreater(len(compile_events), 0, "PROMPT_COMPILED event should be recorded in diagnostics")


if __name__ == "__main__":
    unittest.main()

