#!/usr/bin/env python3
"""
PLB Creator Studio — Frame Evidence & Vision Pipeline
======================================================
Grounds video analysis in multi-timestamp frame evidence using:
1. Directly observed facts (resolution, fps, duration, color distribution, optical motion)
2. Lightweight local neural vision inferences (MobileNetV2-ONNX via OpenCV DNN)
3. Timestamped frame extractions across scene milestones
4. Explicit separation of facts, inferences, metadata hints, and uncertainties
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

# Taxonomy mapping: ImageNet-1k classes to semantic species & categories
IMAGE_NET_TAXONOMY: Dict[str, Dict[str, str]] = {
    # Cats / Felines
    "tabby": {"species": "Cat", "display": "Tabby Cat", "category": "Feline", "temperament": "Curious & Observant"},
    "tiger cat": {"species": "Cat", "display": "Striped Cat", "category": "Feline", "temperament": "Aloof & Agile"},
    "persian cat": {"species": "Cat", "display": "Persian Cat", "category": "Feline", "temperament": "Dignified & Calm"},
    "siamese cat": {"species": "Cat", "display": "Siamese Cat", "category": "Feline", "temperament": "Vocal & Inquisitive"},
    "egyptian cat": {"species": "Cat", "display": "Short-Haired Cat", "category": "Feline", "temperament": "Quick & Playful"},
    "cougar": {"species": "Cat", "display": "Wild Cat", "category": "Feline", "temperament": "Stealthy"},
    "lynx": {"species": "Cat", "display": "Bobcat / Lynx", "category": "Feline", "temperament": "Stealthy"},

    # Poultry & Birds
    "hen": {"species": "Chicken", "display": "Hen", "category": "Poultry", "temperament": "Inquisitive Forager"},
    "cock": {"species": "Chicken", "display": "Rooster", "category": "Poultry", "temperament": "Proud & Vigilant"},
    "partridge": {"species": "Bird", "display": "Partridge / Game Bird", "category": "Avian", "temperament": "Alert Forager"},
    "quail": {"species": "Bird", "display": "Quail", "category": "Avian", "temperament": "Fast Runner"},
    "sulphur-crested cockatoo": {"species": "Parrot", "display": "Cockatoo", "category": "Avian", "temperament": "Expressive & Animated"},
    "macaw": {"species": "Parrot", "display": "Macaw", "category": "Avian", "temperament": "Vibrant & Bold"},
    "lorikeet": {"species": "Parrot", "display": "Lorikeet / Parrot", "category": "Avian", "temperament": "Energetic & Social"},
    "african grey": {"species": "Parrot", "display": "Grey Parrot", "category": "Avian", "temperament": "Clever & Analytical"},
    "drake": {"species": "Duck", "display": "Duck", "category": "Waterfowl", "temperament": "Cheerful Waddler"},
    "goose": {"species": "Goose", "display": "Goose", "category": "Waterfowl", "temperament": "Protective Sentinel"},

    # Rabbits / Leporidae
    "wood rabbit": {"species": "Rabbit", "display": "Cottontail Rabbit", "category": "Lagomorph", "temperament": "Twitchy & Alert"},
    "hare": {"species": "Rabbit", "display": "Hare", "category": "Lagomorph", "temperament": "Swift Runner"},
    "angora": {"species": "Rabbit", "display": "Fluffy Angora Rabbit", "category": "Lagomorph", "temperament": "Gentle & Quiet"},

    # Dogs / Canines
    "golden retriever": {"species": "Dog", "display": "Golden Retriever", "category": "Canine", "temperament": "Gentle & Friendly"},
    "labrador retriever": {"species": "Dog", "display": "Labrador", "category": "Canine", "temperament": "Eager & Cheerful"},
    "border collie": {"species": "Dog", "display": "Collie", "category": "Canine", "temperament": "Focused & Agile"},
    "corgi": {"species": "Dog", "display": "Welsh Corgi", "category": "Canine", "temperament": "Spirited Lowrider"},
    "french bulldog": {"species": "Dog", "display": "French Bulldog", "category": "Canine", "temperament": "Comedic & Sturdy"},
    "pug": {"species": "Dog", "display": "Pug", "category": "Canine", "temperament": "Playful Clown"},
    "beagle": {"species": "Dog", "display": "Beagle", "category": "Canine", "temperament": "Sniffing Explorer"},

    # Other Domestic Animals
    "guinea pig": {"species": "Guinea Pig", "display": "Guinea Pig", "category": "Rodent", "temperament": "Vocal & Furry"},
    "hamster": {"species": "Hamster", "display": "Hamster", "category": "Rodent", "temperament": "Cheek-Stuffer"},
    "box turtle": {"species": "Turtle", "display": "Box Turtle", "category": "Reptile", "temperament": "Unhurried Observer"},
    "mud turtle": {"species": "Turtle", "display": "Turtle", "category": "Reptile", "temperament": "Patience Master"},
    "terrapin": {"species": "Turtle", "display": "Terrapin", "category": "Reptile", "temperament": "Quiet Glide"},
}

_VISION_MODEL_INSTANCE = None
_VISION_MODEL_LOADED = False
_VISION_CLASSES = []

def get_models_dir() -> Path:
    """Locates the models directory, supporting both source and PyInstaller environments."""
    candidates = []
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "story_forge" / "models")
            candidates.append(Path(sys._MEIPASS) / "models")
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "_internal" / "story_forge" / "models")
        candidates.append(exe_dir / "story_forge" / "models")

    # Source tree candidates
    candidates.append(Path(__file__).resolve().parent.parent / "models")
    candidates.append(Path(__file__).resolve().parent.parent.parent / "story_forge" / "models")
    candidates.append(Path.cwd() / "story_forge" / "models")

    for c in candidates:
        if c.exists() and (c / "mobilenetv2-7.onnx").exists():
            return c
    return candidates[0]


def load_vision_model() -> Tuple[Optional[Any], List[str]]:
    """
    Loads MobileNetV2 ONNX model via OpenCV DNN engine.
    Cached singleton across requests.
    """
    global _VISION_MODEL_INSTANCE, _VISION_MODEL_LOADED, _VISION_CLASSES
    if _VISION_MODEL_LOADED:
        return _VISION_MODEL_INSTANCE, _VISION_CLASSES

    models_dir = get_models_dir()
    model_path = models_dir / "mobilenetv2-7.onnx"
    classes_path = models_dir / "imagenet_classes.txt"

    if not model_path.exists() or not classes_path.exists():
        _VISION_MODEL_LOADED = True
        _VISION_MODEL_INSTANCE = None
        _VISION_CLASSES = []
        return None, []

    try:
        with open(classes_path, "r", encoding="utf-8") as f:
            _VISION_CLASSES = [line.strip().lower() for line in f if line.strip()]

        net = cv2.dnn.readNetFromONNX(str(model_path))
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        _VISION_MODEL_INSTANCE = net
        _VISION_MODEL_LOADED = True
        return _VISION_MODEL_INSTANCE, _VISION_CLASSES
    except Exception as e:
        print(f"Warning: Failed to load vision model: {e}")
        _VISION_MODEL_LOADED = True
        _VISION_MODEL_INSTANCE = None
        _VISION_CLASSES = []
        return None, []

def classify_single_frame(
    net: Any,
    classes: List[str],
    frame_bgr: np.ndarray,
    top_k: int = 5
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Runs MobileNetV2 ONNX inference on a single BGR frame.
    Returns (top_predictions, latency_ms).
    """
    t_start = time.time()
    blob = cv2.dnn.blobFromImage(
        frame_bgr,
        scalefactor=1.0 / (255.0 * 0.226),
        size=(224, 224),
        mean=(123.675, 116.28, 103.53),
        swapRB=True,
        crop=False
    )
    net.setInput(blob)
    out = net.forward()
    latency_ms = (time.time() - t_start) * 1000.0

    raw = out[0]
    exp_scores = np.exp(raw - np.max(raw))
    probs = exp_scores / np.sum(exp_scores)
    top_indices = np.argsort(probs)[::-1][:top_k]

    results = []
    for idx in top_indices:
        label = classes[idx] if idx < len(classes) else f"class_{idx}"
        prob = float(probs[idx])
        # Find taxonomy match
        tax = IMAGE_NET_TAXONOMY.get(label, None)
        results.append({
            "class_id": int(idx),
            "label": label,
            "confidence": round(prob, 4),
            "confidence_pct": round(prob * 100.0, 1),
            "species": tax["species"] if tax else "Unclassified",
            "display": tax["display"] if tax else label.title(),
            "category": tax["category"] if tax else "General Object",
            "temperament": tax["temperament"] if tax else "Natural"
        })
    return results, latency_ms

def extract_multi_timestamp_evidence(
    video_path: Path,
    num_samples: int = 5,
    output_frames_dir: Optional[Path] = None,
    sampled_frames: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Phase 2 Core: Extracts multi-timestamp frame evidence across the entire video.
    Returns structured evidence distinguishing:
    - directly observed facts
    - model inferences
    - metadata hints
    - unknown information
    """
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    net, classes = load_vision_model()
    has_model = (net is not None and len(classes) > 0)

    timestamp_records = []
    motion_deltas = []
    accum_color_hist = {"green": [], "wood": [], "white": [], "dark": []}
    per_class_accum: Dict[str, List[float]] = {}
    latencies = []

    # Fast path: Reuse frames already extracted by extract_timeline_frames
    if sampled_frames:
        m_frames = [f for f in sampled_frames if f.get("is_milestone")]
        if len(m_frames) < 3 and len(sampled_frames) >= 3:
            step = len(sampled_frames) / float(num_samples)
            m_frames = [sampled_frames[int(i * step)] for i in range(num_samples)]

        first_f = sampled_frames[0]
        width = first_f.get("width", 1280)
        height = first_f.get("height", 720)
        fps = 24.0
        duration_sec = 0.0

        for f in m_frames:
            ts = f.get("timestamp_sec", f.get("timestamp_seconds", 0.0))
            f_idx = f.get("frame_idx", f.get("frame_number", 0))
            pct_str = f.get("milestone_pct", f.get("percentage_str", ""))
            fpath = f.get("file_path")
            fmetrics = f.get("metrics", {})
            delta = f.get("interframe_delta", 0.0)
            motion_deltas.append(delta)

            g_r = fmetrics.get("green_ratio", 0.0)
            w_r = fmetrics.get("wood_ratio", 0.0)
            wh_r = fmetrics.get("white_ratio", 0.0)
            d_r = fmetrics.get("dark_ratio", 0.0)

            accum_color_hist["green"].append(g_r)
            accum_color_hist["wood"].append(w_r)
            accum_color_hist["white"].append(wh_r)
            accum_color_hist["dark"].append(d_r)

            frame_preds = []
            if has_model and fpath and Path(fpath).exists():
                frame_img = cv2.imread(str(fpath))
                if frame_img is not None:
                    frame_preds, latency_ms = classify_single_frame(net, classes, frame_img, top_k=5)
                    latencies.append(latency_ms)
                    for p in frame_preds:
                        cname = p["label"]
                        conf = p["confidence"]
                        if cname not in per_class_accum:
                            per_class_accum[cname] = []
                        per_class_accum[cname].append(conf)

            timestamp_records.append({
                "timestamp_seconds": round(ts, 2),
                "milestone_pct": pct_str or f"{int(round(ts))}s",
                "frame_number": f_idx,
                "motion_magnitude": round(delta, 2),
                "color_ratios": {
                    "green": round(g_r, 3),
                    "wood": round(w_r, 3),
                    "white": round(wh_r, 3),
                    "dark": round(d_r, 3)
                },
                "top_predictions": frame_preds,
                "keyframe_filename": f.get("filename")
            })

    else:
        # Fallback path: Direct video capture
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration_sec = round(total_frames / fps, 2) if (total_frames > 0 and fps > 0) else 0.0

        if output_frames_dir:
            output_frames_dir.mkdir(parents=True, exist_ok=True)

        if num_samples <= 1:
            sample_ratios = [0.5]
        elif num_samples == 3:
            sample_ratios = [0.2, 0.5, 0.8]
        else:
            sample_ratios = [0.1, 0.25, 0.5, 0.75, 0.9]

        prev_gray = None
        for ratio in sample_ratios:
            frame_idx = int(total_frames * ratio)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            ts = round(frame_idx / fps, 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is not None and prev_gray.shape == gray.shape:
                diff = cv2.absdiff(prev_gray, gray)
                motion_mag = float(np.mean(diff))
                motion_deltas.append(motion_mag)
            else:
                motion_mag = 0.0
            prev_gray = gray

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
            green_mask = (h >= 35) & (h <= 85) & (s > 40)
            wood_mask = (h >= 10) & (h <= 25) & (s > 50) & (v < 180)
            white_mask = (v > 210) & (s < 40)
            dark_mask = v < 45

            total_pixels = frame.shape[0] * frame.shape[1]
            g_r = float(np.sum(green_mask)) / total_pixels
            w_r = float(np.sum(wood_mask)) / total_pixels
            wh_r = float(np.sum(white_mask)) / total_pixels
            d_r = float(np.sum(dark_mask)) / total_pixels

            accum_color_hist["green"].append(g_r)
            accum_color_hist["wood"].append(w_r)
            accum_color_hist["white"].append(wh_r)
            accum_color_hist["dark"].append(d_r)

            frame_preds = []
            if has_model:
                frame_preds, latency_ms = classify_single_frame(net, classes, frame, top_k=5)
                latencies.append(latency_ms)
                for p in frame_preds:
                    cname = p["label"]
                    conf = p["confidence"]
                    if cname not in per_class_accum:
                        per_class_accum[cname] = []
                    per_class_accum[cname].append(conf)

            saved_frame_filename = None
            if output_frames_dir:
                f_name = f"keyframe_{int(ratio*100):02d}pct_{ts:.1f}s.jpg"
                f_path = output_frames_dir / f_name
                cv2.imwrite(str(f_path), frame)
                saved_frame_filename = f_name

            timestamp_records.append({
                "timestamp_seconds": ts,
                "milestone_pct": f"{int(ratio * 100)}%",
                "frame_number": frame_idx,
                "motion_magnitude": round(motion_mag, 2),
                "color_ratios": {
                    "green": round(g_r, 3),
                    "wood": round(w_r, 3),
                    "white": round(wh_r, 3),
                    "dark": round(d_r, 3)
                },
                "top_predictions": frame_preds,
                "keyframe_filename": saved_frame_filename
            })

        cap.release()

    # Determine Scene Setting from color spectrum
    avg_green = float(np.mean(accum_color_hist["green"])) if accum_color_hist["green"] else 0.0
    avg_wood = float(np.mean(accum_color_hist["wood"])) if accum_color_hist["wood"] else 0.0
    avg_white = float(np.mean(accum_color_hist["white"])) if accum_color_hist["white"] else 0.0
    avg_dark = float(np.mean(accum_color_hist["dark"])) if accum_color_hist["dark"] else 0.0

    if avg_green > 0.15:
        setting_desc = "Outdoor Natural Landscape / Garden Foliage"
        setting_palette = ["Lush Foliage Green (Hue 35-85)", "Earthy Soil Brown"]
    elif avg_wood > 0.15:
        setting_desc = "Warm Wood-Toned / Rustic Interior / Natural Timber Setting"
        setting_palette = ["Rustic Wood Grain Brown", "Warm Amber Lighting"]
    elif avg_white > 0.20:
        setting_desc = "High-Luminance Bright / Snowy or Daylight Exterior"
        setting_palette = ["High-Luminance White", "Ambient Daylight Accents"]
    elif avg_dark > 0.30:
        setting_desc = "Atmospheric Low-Key / Dramatic Contrast Setting"
        setting_palette = ["Deep Shadow Tone", "Focused Accent Highlight"]
    else:
        setting_desc = "Authentic Dynamic Scene Environment"
        setting_palette = ["Balanced Mid-Tones", "Ambient Daylight"]

    # Synthesize Consensus Visual Entity from Model Predictions with Species-Level Grouping
    consensus_entity = None
    consensus_species = "Unclassified Subject"
    consensus_label = "Observed Protagonist"
    consensus_category = "Visual Subject"
    consensus_confidence = 0.0
    confidence_tier = "UNVERIFIED"

    if has_model and per_class_accum:
        # 1. Group by Species
        species_scores: Dict[str, Dict[str, Any]] = {}
        for cname, scores in per_class_accum.items():
            tax = IMAGE_NET_TAXONOMY.get(cname, {})
            sp = tax.get("species", "Unclassified")
            cat = tax.get("category", "General Object")
            disp = tax.get("display", cname.title())

            if sp not in species_scores:
                species_scores[sp] = {
                    "species": sp,
                    "category": cat,
                    "display_candidates": {},
                    "all_scores": [],
                    "frame_hits": set()
                }
            species_scores[sp]["all_scores"].extend(scores)
            species_scores[sp]["frame_hits"].add(ts)
            if disp not in species_scores[sp]["display_candidates"]:
                species_scores[sp]["display_candidates"][disp] = []
            species_scores[sp]["display_candidates"][disp].extend(scores)

        # Rank species by aggregate evidence
        ranked_species = []
        for sp, sdata in species_scores.items():
            if sp == "Unclassified":
                continue
            max_c = float(np.max(sdata["all_scores"])) if sdata["all_scores"] else 0.0
            avg_c = float(np.mean(sdata["all_scores"])) if sdata["all_scores"] else 0.0
            # Find best display label for this species
            best_disp = max(
                sdata["display_candidates"].items(),
                key=lambda x: np.max(x[1])
            )[0]
            # Combined score: max confidence + frequency boost
            score_metric = (max_c * 0.7) + (avg_c * 0.3)
            ranked_species.append({
                "species": sp,
                "display": best_disp,
                "category": sdata["category"],
                "max_confidence": max_c,
                "avg_confidence": avg_c,
                "score": score_metric,
                "frame_hits_count": len(sdata["frame_hits"]),
                "sample_count": len(sdata["all_scores"])
            })

        ranked_species.sort(key=lambda x: x["score"], reverse=True)

        if ranked_species:
            top_sp = ranked_species[0]
            # Thresholds: High if >= 0.60; Moderate if >= 0.25 (e.g. Cat or Parrot in challenging lighting)
            if top_sp["max_confidence"] >= 0.60:
                confidence_tier = "HIGH"
                consensus_confidence = round(top_sp["max_confidence"] * 100.0, 1)
                consensus_label = top_sp["display"]
                consensus_species = top_sp["species"]
                consensus_category = top_sp["category"]
                consensus_entity = top_sp
            elif top_sp["max_confidence"] >= 0.25:
                confidence_tier = "MODERATE"
                consensus_confidence = round(top_sp["max_confidence"] * 100.0, 1)
                consensus_label = top_sp["display"]
                consensus_species = top_sp["species"]
                consensus_category = top_sp["category"]
                consensus_entity = top_sp
            else:
                confidence_tier = "LOW"
                consensus_confidence = round(top_sp["max_confidence"] * 100.0, 1)
                consensus_label = "Observed Protagonist"
                consensus_species = "Unclassified Subject"
                consensus_category = "Visual Focus"
                consensus_entity = top_sp

    # Distinguish Four Epistemological Layers
    directly_observed_facts = [
        f"Container: {width}x{height} resolution, {fps:.1f} fps, {duration_sec:.2f}s duration",
        f"Sampled {len(timestamp_records)} distinct timestamps ({', '.join(t['milestone_pct'] for t in timestamp_records)})",
        f"Observable setting palette: {', '.join(setting_palette)}",
        f"Kinetic motion energy measured across timeline: avg delta {float(np.mean(motion_deltas)):.1f}" if motion_deltas else "Static camera framing"
    ]

    model_inferences = []
    if has_model and consensus_entity:
        model_inferences.append(
            f"Vision Model: MobileNetV2-ONNX (OpenCV-DNN Engine, avg latency {float(np.mean(latencies)):.1f}ms/frame)"
        )
        model_inferences.append(
            f"Top visual entity: '{consensus_label}' ({consensus_species}) with {consensus_confidence}% confidence [{confidence_tier}]"
        )
        sample_hits = consensus_entity.get("frame_hits_count", consensus_entity.get("sample_count", 1))
        model_inferences.append(
            f"Cross-timestamp agreement: detected in {sample_hits}/{len(timestamp_records)} sampled frames"
        )
    else:
        model_inferences.append(
            "Local neural vision classifier unavailable; operating in offline heuristic CV mode"
        )

    from scripts.video_seo_reverse_engineer import sanitize_filename_tokens
    clean_stem = sanitize_filename_tokens(video_path.stem)
    filename_hint = clean_stem.title() if clean_stem and clean_stem.lower() not in ["video", "vid", "clip", "ref", "test", "target"] else None

    metadata_hints = []
    if filename_hint:
        metadata_hints.append(f"Filename cue: '{filename_hint}' (Creator reference hint only; unverified visual fact)")

    uncertain_information = []
    if confidence_tier in ["LOW", "UNVERIFIED"]:
        uncertain_information.append("Exact biological species / entity taxonomy unverified by visual classifier")
    if not filename_hint:
        uncertain_information.append("Creator intent / project title not present in file metadata")
    uncertain_information.append("Precise background object taxonomy unclassified by lightweight model")
    uncertain_information.append("Audio acoustic semantics unclassified without sound recognition model")

    return {
        "video_path": str(video_path),
        "video_name": video_path.name,
        "duration_seconds": duration_sec,
        "width": width,
        "height": height,
        "fps": fps,
        "timestamp_records": timestamp_records,
        "setting_environment": {
            "description": setting_desc,
            "palette": setting_palette,
            "color_ratios": {
                "avg_green": round(avg_green, 3),
                "avg_wood": round(avg_wood, 3),
                "avg_white": round(avg_white, 3),
                "avg_dark": round(avg_dark, 3)
            }
        },
        "consensus_entity": {
            "label": consensus_label,
            "display": consensus_label,
            "species": consensus_species,
            "category": consensus_category,
            "confidence_tier": confidence_tier,
            "confidence_pct": consensus_confidence,
            "is_verified": confidence_tier in ["HIGH", "MODERATE"]
        },
        "layers": {
            "directly_observed_facts": directly_observed_facts,
            "model_inferences": model_inferences,
            "metadata_hints": metadata_hints,
            "uncertain_information": uncertain_information
        },
        "model_runtime": {
            "model_name": "MobileNetV2-7 ONNX",
            "backend": "OpenCV DNN (CPU)",
            "classes_count": len(classes),
            "avg_latency_ms": round(float(np.mean(latencies)), 1) if latencies else 0.0,
            "is_local_cpu": True,
            "requires_internet": False,
            "cost_usd": 0.0
        }
    }
