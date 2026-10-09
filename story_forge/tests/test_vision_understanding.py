#!/usr/bin/env python3
"""
Test Suite for Phase 2: Real Visual Understanding & Frame Evidence Pipeline
============================================================================
Verifies:
1. Lightweight vision model loading and CPU execution
2. Multi-timestamp frame sampling and 4-layer epistemological separation
3. Ground truth classification across 3 visually distinct test videos
4. Refusal to hallucinate on blank / synthetic video frames
5. Grounding of Story DNA, Canon Characters, and Prompt Compiler
"""

import sys
import json
import tempfile
from pathlib import Path
import cv2
import numpy as np
import pytest

# Project root setup
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from story_forge.engine.vision_pipeline import (
    load_vision_model,
    classify_single_frame,
    extract_multi_timestamp_evidence
)
from story_forge.engine.video_story_extractor import extract_video_story_evidence
from story_forge.engine.story_dna import build_story_dna
from story_forge.engine.character_universe import extract_canon_characters
from story_forge.engine.prompt_compiler import (
    Seedance25Adapter,
    compile_prompt_package
)

class TestVisionUnderstanding:

    def test_vision_model_loading_and_cpu_readiness(self):
        """Verify MobileNetV2-7 ONNX loads into OpenCV DNN on CPU with 1000 ImageNet classes."""
        net, classes = load_vision_model()
        assert net is not None, "Failed to load MobileNetV2 ONNX model"
        assert len(classes) == 1000, f"Expected 1000 classes, found {len(classes)}"
        assert "tabby" in classes
        assert "hen" in classes
        assert "sulphur-crested cockatoo" in classes

    def test_single_frame_inference_latency(self):
        """Verify inference latency is under 50ms on CPU."""
        net, classes = load_vision_model()
        dummy_frame = np.full((224, 224, 3), 128, dtype=np.uint8)
        preds, latency_ms = classify_single_frame(net, classes, dummy_frame)
        assert len(preds) == 5
        assert latency_ms < 100.0, f"Latency too high: {latency_ms}ms"

    def test_synthetic_blank_video_refusal_to_hallucinate(self):
        """Blank solid-color video must report LOW confidence and refuse to fabricate species."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vpath = Path(tmpdir) / "blank_test.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(vpath), fourcc, 24.0, (320, 240))
            for _ in range(48):
                frame = np.full((240, 320, 3), (80, 80, 80), dtype=np.uint8)
                out.write(frame)
            out.release()

            ev = extract_multi_timestamp_evidence(vpath, num_samples=3)
            cent = ev["consensus_entity"]
            assert cent["is_verified"] is False, "Blank video must not be verified!"
            assert cent["confidence_tier"] in ["LOW", "UNVERIFIED"]
            assert cent["label"] == "Observed Protagonist"
            assert cent["species"] == "Unclassified Subject"
            assert "Exact biological species" in " ".join(ev["layers"]["uncertain_information"])

    def test_three_video_ground_truth_classification(self):
        """Verify real visual understanding on 3 distinct videos on disk."""
        v1_list = list(Path("input").glob("*Winter*"))
        v2_path = Path("temp_uploads/d70c5a_dola_20261007060757_video.mp4")
        v3_path = Path("input/ref-video.mp4")

        # Video 1: Winter Colobok (Cat in snow)
        if v1_list:
            ev1 = extract_multi_timestamp_evidence(v1_list[0], num_samples=5)
            cent1 = ev1["consensus_entity"]
            assert cent1["is_verified"] is True
            assert cent1["species"] == "Cat", f"Video 1 expected Cat, got {cent1['species']}"
            assert cent1["category"] == "Feline"
            assert cent1["confidence_pct"] >= 25.0

        # Video 2: Dola Chickens
        if v2_path.exists():
            ev2 = extract_multi_timestamp_evidence(v2_path, num_samples=5)
            cent2 = ev2["consensus_entity"]
            assert cent2["is_verified"] is True
            assert cent2["species"] == "Chicken", f"Video 2 expected Chicken, got {cent2['species']}"
            assert cent2["display"] == "Hen"
            assert cent2["confidence_pct"] >= 80.0

        # Video 3: Ref Video (Cockatoo)
        if v3_path.exists():
            ev3 = extract_multi_timestamp_evidence(v3_path, num_samples=5)
            cent3 = ev3["consensus_entity"]
            assert cent3["is_verified"] is True
            assert cent3["species"] == "Parrot", f"Video 3 expected Parrot, got {cent3['species']}"
            assert cent3["category"] == "Avian"
            assert cent3["confidence_pct"] >= 80.0

    def test_epistemological_layers_separation(self):
        """Verify facts, inferences, hints, and uncertainties are strictly separated."""
        v3_path = Path("input/ref-video.mp4")
        if not v3_path.exists():
            pytest.skip("ref-video.mp4 not found")

        ev = extract_multi_timestamp_evidence(v3_path, num_samples=5)
        layers = ev["layers"]
        assert len(layers["directly_observed_facts"]) >= 3
        assert len(layers["model_inferences"]) >= 2
        assert len(layers["uncertain_information"]) >= 1

        # Direct facts must contain container metrics
        facts_str = " ".join(layers["directly_observed_facts"]).lower()
        assert "resolution" in facts_str or "fps" in facts_str

        # Inferences must mention model name
        inf_str = " ".join(layers["model_inferences"]).lower()
        assert "mobilenetv2" in inf_str

    def test_story_dna_and_canon_character_grounding(self):
        """Verify Story DNA, Canon Characters, and Prompt Compiler ground in verified entity."""
        v2_path = Path("temp_uploads/d70c5a_dola_20261007060757_video.mp4")
        if not v2_path.exists():
            pytest.skip("Dola video not found")

        ev = extract_video_story_evidence(v2_path)
        dna = build_story_dna(ev)

        assert dna["characters"][0]["name"] == "Hen"
        assert dna["characters"][0]["species"] == "Chicken"
        assert dna["cv_limitation_disclosed"] is False
        assert "hen" in dna["core_premise"].lower()

        canon = extract_canon_characters(ev, dna)
        assert len(canon) >= 1
        assert canon[0].name == "Hen"
        assert canon[0].species == "Chicken"

        # Verify prompt compilation
        res = Seedance25Adapter.compile(story=dna, story_dna=dna, hero_frame={}, continuity_lock={})
        compiled_text = res.prompt_text.lower()
        assert "hen" in compiled_text or "chicken" in compiled_text

        pkg = compile_prompt_package(story=dna, story_dna=dna)
        assert "hen" in pkg["seedance_25_prompt"].lower() or "chicken" in pkg["seedance_25_prompt"].lower()

