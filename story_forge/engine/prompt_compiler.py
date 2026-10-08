#!/usr/bin/env python3
"""
PLB Studio — Model-Aware Prompt Compiler
========================================
Authoritative multi-model prompt compilation engine for PLB Creator Studio.

Source of Truth:
- Official Seedance 2.5 prompting guidance from ByteDance / Volcengine:
  Base structure: Subject -> Action/Event -> Scene/Environment -> Visual Style -> Camera/Shot -> Sound
  Advanced capabilities: Timestamps, Reference-role mapping, Continuity, Camera movements, Sound,
  Extension/edit prompts, First-frame / Last-frame loop workflows.

Model-Aware Adapters:
1. Seedance 2.5 (Video Model)
2. Universal Image (Image Model - Midjourney / SDXL / FLUX)
3. GPT Image (Image Model - DALL-E 3 / ChatGPT Image)
4. Nano Banana Pro (Image Model - Fast Edge / Stylized / Token-Anchored)

Outputs a comprehensive PROMPT PACKAGE with structure breakdowns and validation gates (PASS / PARTIAL / FAIL).
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
import re


# -------------------------------------------------------------------------
# 1. Data Structures & Validation Schemas
# -------------------------------------------------------------------------

@dataclass
class ValidationReport:
    status: str  # "PASS", "PARTIAL", "FAIL"
    passed_checks: int
    total_checks: int
    score_pct: float
    checks: Dict[str, bool]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompiledPromptResult:
    model_id: str
    model_name: str
    output_type: str  # "video" | "image"
    prompt_text: str
    structure: Dict[str, str]
    validation: ValidationReport

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "output_type": self.output_type,
            "prompt_text": self.prompt_text,
            "structure": self.structure,
            "validation": self.validation.to_dict()
        }


# -------------------------------------------------------------------------
# 2. Seedance 2.5 Video Adapter (ByteDance / Volcengine Standard)
# -------------------------------------------------------------------------

class Seedance25Adapter:
    """
    Official ByteDance / Volcengine Seedance 2.5 prompting standard.
    Base Sequence:
      Subject -> Action/Event -> Scene/Environment -> Visual Style -> Camera/Shot -> Sound
    Plus:
      Timeline/Shot Structure, Reference-Role Mapping, Continuity Lock, Loop Anchor.
    """

    MODEL_ID = "seedance_25"
    MODEL_NAME = "Seedance 2.5"
    OUTPUT_TYPE = "video"

    @classmethod
    def compile(
        cls,
        story: Dict[str, Any],
        story_dna: Dict[str, Any],
        hero_frame: Dict[str, Any],
        continuity_lock: Dict[str, Any],
        script: Optional[Dict[str, Any]] = None,
        storyboard: Optional[List[Dict[str, Any]]] = None
    ) -> CompiledPromptResult:
        # 1. Extract context variables
        chars = story.get("characters") or story_dna.get("characters") or [{"name": "Protagonist", "species": "Animal"}]
        primary_char = chars[0].get("name", "Curious Animal")
        primary_species = chars[0].get("species", "Animal")
        secondary_char = chars[1].get("name", "") if len(chars) > 1 else ""

        objects = story.get("objects") or story_dna.get("objects") or [{"name": "Mystery Object"}]
        obj_name = objects[0].get("name", "Focal Object")

        setting = story.get("setting") or story_dna.get("setting", "Sunny Enclosure")
        twist = story.get("twist") or "A comically dramatic reaction"
        payoff = story.get("payoff") or "A hilarious freeze-frame head shake directly into camera"

        comp_style = hero_frame.get("composition") or "Rule-of-thirds low angle eye-level"
        lighting = hero_frame.get("lighting") or hero_frame.get("focal_lighting") or "Golden hour natural rim lighting"
        palette = hero_frame.get("color_palette") or "Warm earth tones, natural green, crisp highlights"
        lens = hero_frame.get("camera_lens") or hero_frame.get("depth_of_field") or "50mm prime lens, f/2.8 shallow depth of field"

        morph_lock = continuity_lock.get("character_morphology") or f"Preserve realistic fur/feather coat texture for {primary_char}."
        env_lock = continuity_lock.get("environment_lock") or f"Strict persistence of {setting} lighting and architecture."
        traits_lock = continuity_lock.get("immutable_traits") or "Object scale and real-world gravity invariants"
        if isinstance(traits_lock, list):
            traits_lock = ", ".join(traits_lock)

        # 2. Build Structured Dimensions (ByteDance Seedance 2.5 standard)
        ref_mapping = f"@Subject1: {primary_char} ({primary_species}, natural realistic anatomy) | @Object1: {obj_name}"
        if secondary_char:
            ref_mapping += f" | @Subject2: {secondary_char}"

        subject_dim = f"{primary_char}, an expressive {primary_species} with authentic physical scale, detailed fur/feather textures, and lively curious eyes"
        action_dim = f"Cautiously advances toward {obj_name}, conducts an investigative inspection, experiences {twist}, and executes {payoff}"
        scene_dim = f"{setting}, realistic ground texture with subtle environment details, atmospheric depth"
        style_dim = f"Photorealistic 8k video capture, award-winning nature cinematography, 24fps cinema cadence, palette anchored in {palette}"
        camera_dim = f"Ground-level tracking push-in at eye level, {lens}, smooth cinematic stabilization, {comp_style}"
        sound_dim = f"Playful rhythmic Foley footsteps, crisp tactile interaction with {obj_name}, comedic acoustic pizzicato accompaniment, zero human speech"
        continuity_dim = f"Anatomical lock: {morph_lock} | Environment lock: {env_lock} | Invariants: {traits_lock}"

        # 3. Build Timeline Beats (0-15s)
        timeline_dim = (
            f"[00:00-00:03] Shot 1: The Visual Hook - Extreme low angle as {primary_char} locks eyes with {obj_name}. "
            f"[00:03-00:07] Shot 2: Cautious Approach - Stealth creeping steps forward with twitching whiskers/feathers. "
            f"[00:07-00:11] Shot 3: Decisive Contact - Sudden inquisitive contact leading to {twist}. "
            f"[00:11-00:15] Shot 4-6: Payoff & Loop - {payoff}, concluding with a seamless loop reset to opening posture."
        )

        first_last_frame_dim = (
            f"[First Frame Anchor: {primary_char} poised at camera left, eyeing {obj_name} across {setting}] "
            f"[Last Frame Anchor: {primary_char} shakes off surprise and returns to initial curious posture for infinite replay]"
        )

        # 4. Synthesize Full Seedance 2.5 Prompt
        prompt_text = (
            f"[Seedance 2.5 Directive]\n"
            f"[Roles: {ref_mapping}]\n"
            f"[Subject]: {subject_dim}.\n"
            f"[Action/Event]: {action_dim}.\n"
            f"[Scene/Environment]: {scene_dim}.\n"
            f"[Visual Style]: {style_dim}, {lighting}.\n"
            f"[Camera/Shot]: {camera_dim}.\n"
            f"[Sound]: {sound_dim}.\n"
            f"[Timeline]: {timeline_dim}\n"
            f"[Continuity]: {continuity_dim}.\n"
            f"[Workflow]: {first_last_frame_dim}"
        )

        structure = {
            "Subject": subject_dim,
            "Action/Event": action_dim,
            "Scene/Environment": scene_dim,
            "Visual Style": style_dim,
            "Camera/Shot": camera_dim,
            "Sound": sound_dim,
            "References": ref_mapping,
            "Timeline": timeline_dim,
            "Continuity": continuity_dim
        }

        # 5. Validation Gate
        validation = cls.validate(structure)

        return CompiledPromptResult(
            model_id=cls.MODEL_ID,
            model_name=cls.MODEL_NAME,
            output_type=cls.OUTPUT_TYPE,
            prompt_text=prompt_text,
            structure=structure,
            validation=validation
        )

    @classmethod
    def validate(cls, structure: Dict[str, str]) -> ValidationReport:
        checks = {
            "Subject": bool(structure.get("Subject") and len(structure["Subject"].strip()) >= 15),
            "Action/Event": bool(structure.get("Action/Event") and len(structure["Action/Event"].strip()) >= 20),
            "Scene/Environment": bool(structure.get("Scene/Environment") and len(structure["Scene/Environment"].strip()) >= 10),
            "Visual Style": bool(structure.get("Visual Style") and len(structure["Visual Style"].strip()) >= 15),
            "Camera/Shot": bool(structure.get("Camera/Shot") and len(structure["Camera/Shot"].strip()) >= 15),
            "Sound": bool(structure.get("Sound") and len(structure["Sound"].strip()) >= 15),
            "References": bool(structure.get("References") and "@" in structure["References"]),
            "Timeline": bool(structure.get("Timeline") and "[00:" in structure["Timeline"]),
            "Continuity constraints": bool(structure.get("Continuity") and len(structure["Continuity"].strip()) >= 20)
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score_pct = round((passed / total) * 100, 1)

        warnings = []
        for k, v in checks.items():
            if not v:
                warnings.append(f"Seedance field '{k}' incomplete or below required specification threshold.")

        if passed == total:
            status = "PASS"
        elif passed >= 6:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return ValidationReport(
            status=status,
            passed_checks=passed,
            total_checks=total,
            score_pct=score_pct,
            checks=checks,
            warnings=warnings
        )


# -------------------------------------------------------------------------
# 3. Universal Image Adapter (Midjourney / SDXL / FLUX / Imagen 3)
# -------------------------------------------------------------------------

class UniversalImageAdapter:
    """
    Declarative, high-density positive prompt syntax optimized for Midjourney,
    SDXL, FLUX, and Imagen 3.
    """

    MODEL_ID = "universal_image"
    MODEL_NAME = "Universal Image"
    OUTPUT_TYPE = "image"

    @classmethod
    def compile(
        cls,
        story: Dict[str, Any],
        story_dna: Dict[str, Any],
        hero_frame: Dict[str, Any],
        continuity_lock: Dict[str, Any]
    ) -> CompiledPromptResult:
        chars = story.get("characters") or story_dna.get("characters") or [{"name": "Protagonist", "species": "Animal"}]
        primary_char = chars[0].get("name", "Curious Animal")
        primary_species = chars[0].get("species", "Animal")

        objects = story.get("objects") or story_dna.get("objects") or [{"name": "Mystery Object"}]
        obj_name = objects[0].get("name", "Focal Object")

        setting = story.get("setting") or story_dna.get("setting", "Sunny Natural Habitat")

        comp = hero_frame.get("composition") or "Dynamic rule-of-thirds low angle, ground-level perspective"
        lighting = hero_frame.get("lighting") or hero_frame.get("focal_lighting") or "Soft golden hour side lighting with warm rim highlights"
        palette = hero_frame.get("color_palette") or "Rich organic earth tones and vivid accents"
        lens = hero_frame.get("camera_lens") or hero_frame.get("depth_of_field") or "85mm f/1.8 macro telephoto, sharp focal plane, creamy bokeh"

        morph = continuity_lock.get("character_morphology") or f"Strict natural species anatomy for {primary_species}"
        env = continuity_lock.get("environment_lock") or f"Consistent natural architecture of {setting}"

        subject_dim = f"Hyper-detailed close-up portrait of {primary_char} ({primary_species}), expressive wide eyes filled with curious tension"
        comp_dim = f"{comp}, subject anchored on the primary power point, balanced visual weight"
        env_dim = f"{setting}, tactile surface textures, soft background depth"
        action_dim = f"Tense paused anticipation, paw/snout hovering centimeters above {obj_name}"
        details_dim = f"Crisp individual fur/feather fibers, wet snout reflections, authentic organic anatomical proportions"
        lighting_dim = f"{lighting}, volumetric dust motes caught in sunbeams, palette dominated by {palette}"
        camera_dim = f"{lens}, ultra-sharp focus on subject eyes, cinematic shallow depth of field"
        style_dim = f"Award-winning National Geographic wildlife photography, 8k resolution, authentic raw camera render, masterpiece"
        continuity_dim = f"Identity lock: {morph}, scene fidelity: {env}"
        constraints_dim = f"Zero anatomical distortion, no AI artifacts, no watermarks, realistic physical lighting"

        prompt_text = (
            f"{subject_dim}. {action_dim} in {env_dim}. "
            f"Composition: {comp_dim}. "
            f"Lighting: {lighting_dim}. "
            f"Optics: {camera_dim}. "
            f"Visual Details: {details_dim}. "
            f"Style: {style_dim}. "
            f"Continuity & Constraints: {continuity_dim}, {constraints_dim}."
        )

        structure = {
            "Subject": subject_dim,
            "Composition": comp_dim,
            "Environment": env_dim,
            "Action": action_dim,
            "Visual details": details_dim,
            "Lighting": lighting_dim,
            "Camera/framing": camera_dim,
            "Style": style_dim,
            "Continuity": continuity_dim,
            "Constraints": constraints_dim
        }

        validation = cls.validate(structure)

        return CompiledPromptResult(
            model_id=cls.MODEL_ID,
            model_name=cls.MODEL_NAME,
            output_type=cls.OUTPUT_TYPE,
            prompt_text=prompt_text,
            structure=structure,
            validation=validation
        )

    @classmethod
    def validate(cls, structure: Dict[str, str]) -> ValidationReport:
        checks = {
            "Subject": bool(structure.get("Subject") and len(structure["Subject"].strip()) >= 15),
            "Composition": bool(structure.get("Composition") and len(structure["Composition"].strip()) >= 15),
            "Environment": bool(structure.get("Environment") and len(structure["Environment"].strip()) >= 10),
            "Action": bool(structure.get("Action") and len(structure["Action"].strip()) >= 15),
            "Visual details": bool(structure.get("Visual details") and len(structure["Visual details"].strip()) >= 15),
            "Lighting": bool(structure.get("Lighting") and len(structure["Lighting"].strip()) >= 15),
            "Camera/framing": bool(structure.get("Camera/framing") and len(structure["Camera/framing"].strip()) >= 15),
            "Style": bool(structure.get("Style") and len(structure["Style"].strip()) >= 15),
            "Continuity": bool(structure.get("Continuity") and len(structure["Continuity"].strip()) >= 15),
            "Constraints": bool(structure.get("Constraints") and len(structure["Constraints"].strip()) >= 10)
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score_pct = round((passed / total) * 100, 1)

        warnings = []
        for k, v in checks.items():
            if not v:
                warnings.append(f"Universal Image field '{k}' below specification threshold.")

        if passed == total:
            status = "PASS"
        elif passed >= 7:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return ValidationReport(
            status=status,
            passed_checks=passed,
            total_checks=total,
            score_pct=score_pct,
            checks=checks,
            warnings=warnings
        )


# -------------------------------------------------------------------------
# 4. GPT Image Adapter (DALL-E 3 / ChatGPT Image Standard)
# -------------------------------------------------------------------------

class GPTImageAdapter:
    """
    Natural-language narrative descriptive prompting optimized for DALL-E 3 / GPT Image.
    Avoids tag-soup / comma spam. Focuses on full sentence contextual storytelling,
    character emotional nuance, atmosphere, and cinematic photographic realism.
    """

    MODEL_ID = "gpt_image"
    MODEL_NAME = "GPT Image"
    OUTPUT_TYPE = "image"

    @classmethod
    def compile(
        cls,
        story: Dict[str, Any],
        story_dna: Dict[str, Any],
        hero_frame: Dict[str, Any],
        continuity_lock: Dict[str, Any]
    ) -> CompiledPromptResult:
        chars = story.get("characters") or story_dna.get("characters") or [{"name": "Protagonist", "species": "Animal"}]
        primary_char = chars[0].get("name", "Curious Animal")
        primary_species = chars[0].get("species", "Animal")

        objects = story.get("objects") or story_dna.get("objects") or [{"name": "Mystery Object"}]
        obj_name = objects[0].get("name", "Focal Object")

        setting = story.get("setting") or story_dna.get("setting", "Sunny Enclosure")

        comp = hero_frame.get("composition") or "A low-angle ground-level shot that emphasizes the scale of the environment"
        lighting = hero_frame.get("lighting") or hero_frame.get("focal_lighting") or "Warm golden hour sunlight streaming across the scene"
        palette = hero_frame.get("color_palette") or "Warm golden amber, lush greens, and soft shadows"
        lens = hero_frame.get("camera_lens") or hero_frame.get("depth_of_field") or "Shot with a high-end prime lens resulting in smooth blurred background"

        morph = continuity_lock.get("character_morphology") or f"A completely natural, realistic {primary_species} without cartoonish anthropomorphism"
        env = continuity_lock.get("environment_lock") or f"Authentic real-world {setting}"

        subject_dim = f"A photorealistic portrait of an adorable {primary_species} named {primary_char}"
        comp_dim = f"{comp}, placing the viewer directly on the ground beside the creature"
        env_dim = f"In the picturesque environment of {setting}, featuring authentic natural textures and gentle ambient atmosphere"
        action_dim = f"The creature pauses mid-step, head tilted in deep comical curiosity as it inspects a {obj_name}"
        details_dim = f"Fine individual fur fibers, glossy moisture on the nose, and luminous amber eyes capturing sharp reflections"
        lighting_dim = f"{lighting}, casting subtle elongated shadows across the ground and highlighting the edges of its coat in {palette}"
        camera_dim = f"{lens}, emphasizing crystal-clear focus on the subject while the background melts into soft bokeh"
        style_dim = f"Authentic nature documentary still with natural color grading and balanced exposure, looking like a real captured photograph"
        continuity_dim = f"{morph}, strictly maintaining organic biological proportions"
        constraints_dim = f"Free of distortion, clean compositions, no text overlays, realistic physics"

        # Coherent descriptive paragraph format preferred by DALL-E 3
        prompt_text = (
            f"A realistic, high-detail photograph of {subject_dim}. "
            f"{env_dim}. {comp_dim}. "
            f"{action_dim}. "
            f"The image reveals {details_dim}. "
            f"{lighting_dim}. "
            f"{camera_dim}. "
            f"{style_dim}. {continuity_dim}, {constraints_dim}."
        )

        structure = {
            "Subject": subject_dim,
            "Composition": comp_dim,
            "Environment": env_dim,
            "Action": action_dim,
            "Visual details": details_dim,
            "Lighting": lighting_dim,
            "Camera/framing": camera_dim,
            "Style": style_dim,
            "Continuity": continuity_dim,
            "Constraints": constraints_dim
        }

        validation = cls.validate(structure)

        return CompiledPromptResult(
            model_id=cls.MODEL_ID,
            model_name=cls.MODEL_NAME,
            output_type=cls.OUTPUT_TYPE,
            prompt_text=prompt_text,
            structure=structure,
            validation=validation
        )

    @classmethod
    def validate(cls, structure: Dict[str, str]) -> ValidationReport:
        checks = {
            "Subject": bool(structure.get("Subject") and len(structure["Subject"].strip()) >= 15),
            "Composition": bool(structure.get("Composition") and len(structure["Composition"].strip()) >= 15),
            "Environment": bool(structure.get("Environment") and len(structure["Environment"].strip()) >= 15),
            "Action": bool(structure.get("Action") and len(structure["Action"].strip()) >= 15),
            "Visual details": bool(structure.get("Visual details") and len(structure["Visual details"].strip()) >= 15),
            "Lighting": bool(structure.get("Lighting") and len(structure["Lighting"].strip()) >= 15),
            "Camera/framing": bool(structure.get("Camera/framing") and len(structure["Camera/framing"].strip()) >= 15),
            "Style": bool(structure.get("Style") and len(structure["Style"].strip()) >= 15),
            "Continuity": bool(structure.get("Continuity") and len(structure["Continuity"].strip()) >= 15),
            "Constraints": bool(structure.get("Constraints") and len(structure["Constraints"].strip()) >= 10)
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score_pct = round((passed / total) * 100, 1)

        warnings = []
        for k, v in checks.items():
            if not v:
                warnings.append(f"GPT Image field '{k}' below narrative specification threshold.")

        if passed == total:
            status = "PASS"
        elif passed >= 7:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return ValidationReport(
            status=status,
            passed_checks=passed,
            total_checks=total,
            score_pct=score_pct,
            checks=checks,
            warnings=warnings
        )


# -------------------------------------------------------------------------
# 5. Nano Banana Pro Adapter (Edge / Mobile / Token-Anchored Format)
# -------------------------------------------------------------------------

class NanoBananaProAdapter:
    """
    Concise, high-density token-anchored prompt syntax optimized for
    Nano Banana Pro / lightweight edge models.
    Organized into bracketed functional directives for maximum token efficiency.
    """

    MODEL_ID = "nano_banana_pro"
    MODEL_NAME = "Nano Banana Pro"
    OUTPUT_TYPE = "image"

    @classmethod
    def compile(
        cls,
        story: Dict[str, Any],
        story_dna: Dict[str, Any],
        hero_frame: Dict[str, Any],
        continuity_lock: Dict[str, Any]
    ) -> CompiledPromptResult:
        chars = story.get("characters") or story_dna.get("characters") or [{"name": "Protagonist", "species": "Animal"}]
        primary_char = chars[0].get("name", "Animal")
        primary_species = chars[0].get("species", "Animal")

        objects = story.get("objects") or story_dna.get("objects") or [{"name": "Mystery Object"}]
        obj_name = objects[0].get("name", "Object")

        setting = story.get("setting") or story_dna.get("setting", "Natural Enclosure")

        comp = hero_frame.get("composition") or "low-angle rule-of-thirds"
        lighting = hero_frame.get("lighting") or hero_frame.get("focal_lighting") or "golden rim lighting"
        palette = hero_frame.get("color_palette") or "warm natural tones"
        lens = hero_frame.get("camera_lens") or hero_frame.get("depth_of_field") or "50mm prime f/2.8"

        morph = continuity_lock.get("character_morphology") or f"natural {primary_species} anatomy"
        env = continuity_lock.get("environment_lock") or f"persistent {setting}"

        subject_dim = f"{primary_char} ({primary_species}), hyper-crisp facial expression, high-contrast pupil focus"
        comp_dim = f"{comp}, tight ground perspective, dynamic negative space balance"
        env_dim = f"{setting}, clean background depth, micro surface texture"
        action_dim = f"Inquisitive advance toward {obj_name}, kinetic tension freeze"
        details_dim = f"Ultra-fine fur and feather texture, high-specular eye highlights, organic realism"
        lighting_dim = f"{lighting}, sharp directional key, soft ambient fill, palette: {palette}"
        camera_dim = f"{lens}, macro center sharpness, creamy background falloff"
        style_dim = f"Masterpiece animal photography, 8k crisp details, ultra-high dynamic range"
        continuity_dim = f"Morphology locked: {morph}, scene locked: {env}"
        constraints_dim = f"Zero anatomical flaws, no blur artifacts, no watermark, strictly organic"

        prompt_text = (
            f"[FOCAL_SUBJECT: {subject_dim}] | "
            f"[ACTION_TENSION: {action_dim}] | "
            f"[SETTING_COMPOSITION: {env_dim}, {comp_dim}] | "
            f"[LIGHTING_PALETTE: {lighting_dim}] | "
            f"[OPTICS_DETAIL: {camera_dim}, {details_dim}] | "
            f"[STYLE_QUALITY: {style_dim}] | "
            f"[CONTINUITY_LOCK: {continuity_dim}, {constraints_dim}]"
        )

        structure = {
            "Subject": subject_dim,
            "Composition": comp_dim,
            "Environment": env_dim,
            "Action": action_dim,
            "Visual details": details_dim,
            "Lighting": lighting_dim,
            "Camera/framing": camera_dim,
            "Style": style_dim,
            "Continuity": continuity_dim,
            "Constraints": constraints_dim
        }

        validation = cls.validate(structure)

        return CompiledPromptResult(
            model_id=cls.MODEL_ID,
            model_name=cls.MODEL_NAME,
            output_type=cls.OUTPUT_TYPE,
            prompt_text=prompt_text,
            structure=structure,
            validation=validation
        )

    @classmethod
    def validate(cls, structure: Dict[str, str]) -> ValidationReport:
        checks = {
            "Subject": bool(structure.get("Subject") and len(structure["Subject"].strip()) >= 10),
            "Composition": bool(structure.get("Composition") and len(structure["Composition"].strip()) >= 10),
            "Environment": bool(structure.get("Environment") and len(structure["Environment"].strip()) >= 10),
            "Action": bool(structure.get("Action") and len(structure["Action"].strip()) >= 10),
            "Visual details": bool(structure.get("Visual details") and len(structure["Visual details"].strip()) >= 10),
            "Lighting": bool(structure.get("Lighting") and len(structure["Lighting"].strip()) >= 10),
            "Camera/framing": bool(structure.get("Camera/framing") and len(structure["Camera/framing"].strip()) >= 10),
            "Style": bool(structure.get("Style") and len(structure["Style"].strip()) >= 10),
            "Continuity": bool(structure.get("Continuity") and len(structure["Continuity"].strip()) >= 10),
            "Constraints": bool(structure.get("Constraints") and len(structure["Constraints"].strip()) >= 10)
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        score_pct = round((passed / total) * 100, 1)

        warnings = []
        for k, v in checks.items():
            if not v:
                warnings.append(f"Nano Banana Pro token directive '{k}' incomplete.")

        if passed == total:
            status = "PASS"
        elif passed >= 7:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return ValidationReport(
            status=status,
            passed_checks=passed,
            total_checks=total,
            score_pct=score_pct,
            checks=checks,
            warnings=warnings
        )


# -------------------------------------------------------------------------
# 6. Master Prompt Compiler Engine
# -------------------------------------------------------------------------

def compile_prompt_package(
    story: Dict[str, Any],
    story_dna: Dict[str, Any],
    hero_frame: Optional[Dict[str, Any]] = None,
    continuity_lock: Optional[Dict[str, Any]] = None,
    script: Optional[Dict[str, Any]] = None,
    storyboard: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Compiles a comprehensive, model-aware PROMPT PACKAGE across Video and Image models.
    Preserves exact creative intent while adapting to each target model's documented syntax.
    """
    hero = hero_frame or story.get("hero_frame") or {}
    cont = continuity_lock or story.get("continuity_lock") or {}

    # Compile each model-aware adapter
    res_seedance = Seedance25Adapter.compile(story, story_dna, hero, cont, script, storyboard)
    res_universal = UniversalImageAdapter.compile(story, story_dna, hero, cont)
    res_gpt = GPTImageAdapter.compile(story, story_dna, hero, cont)
    res_nano = NanoBananaProAdapter.compile(story, story_dna, hero, cont)

    # Compile Hero Frame prompt (direct extraction)
    hero_frame_prompt = res_universal.prompt_text

    # Compile Shot-by-Shot prompts (Shots 1 to 6)
    chars = story.get("characters") or story_dna.get("characters") or [{"name": "Protagonist", "species": "Animal"}]
    primary_char = chars[0].get("name", "Animal")
    primary_species = chars[0].get("species", "Animal")
    objects = story.get("objects") or story_dna.get("objects") or [{"name": "Mystery Object"}]
    obj_name = objects[0].get("name", "Object")
    setting = story.get("setting") or story_dna.get("setting", "Garden Run")

    shot_by_shot_prompts = []
    sb_list = storyboard or story.get("storyboard_6_shots") or story.get("storyboard_6shot") or []
    
    if sb_list:
        for s in sb_list:
            s_num = s.get("shot_number", len(shot_by_shot_prompts) + 1)
            s_name = s.get("name") or s.get("beat") or f"Shot {s_num}"
            s_dur = s.get("duration", "2-3s")
            s_type = s.get("shot_type") or s.get("framing") or "Medium Shot"
            s_cam = s.get("camera_angle") or s.get("camera_movement") or "Eye-level tracking"
            s_act = s.get("action") or s.get("description") or f"{primary_char} interacts with {obj_name}"

            shot_prompt = (
                f"[Shot {s_num}: {s_name} ({s_dur})] {s_type}, {s_cam}. "
                f"{primary_char} ({primary_species}) in {setting}. {s_act}. "
                f"Photorealistic 8k video, 24fps, cinematic natural lighting."
            )
            shot_by_shot_prompts.append({
                "shot_number": s_num,
                "name": s_name,
                "duration": s_dur,
                "prompt": shot_prompt
            })
    else:
        # Default 6 canonical beats
        default_beats = [
            (1, "The Visual Hook", "00:00 - 00:03", "Extreme Close-Up", "Low-angle eye-level static", f"{primary_char} locks eyes with {obj_name}"),
            (2, "The Approach", "00:03 - 00:07", "Medium Tracking", "Smooth push-in", f"{primary_char} sneaks forward with twitching whiskers"),
            (3, "The Climax", "00:07 - 00:10", "Macro Tight Shot", "Dynamic handheld tension", f"Decisive contact with {obj_name}"),
            (4, "The Reaction", "00:10 - 00:12", "Medium Reaction", "Rapid zoom punch-in", f"Comedic startled double-take"),
            (5, "The Payoff", "00:12 - 00:14", "Wide Return", "Gentle pedestal rise", f"{primary_char} proudly accepts the outcome"),
            (6, "The Loop Transition", "00:14 - 00:15", "Return Medium", "Slow pull-back", f"{primary_char} resets to opening curiosity pose")
        ]
        for s_num, s_name, s_dur, s_type, s_cam, s_act in default_beats:
            shot_by_shot_prompts.append({
                "shot_number": s_num,
                "name": s_name,
                "duration": s_dur,
                "prompt": f"[Shot {s_num}: {s_name} ({s_dur})] {s_type}, {s_cam}. {primary_char} in {setting}. {s_act}. Photorealistic 8k video, 24fps."
            })

    # Continuity Block
    morph_txt = cont.get("character_morphology") or f"Consistent realistic fur/feather coat for {primary_char}."
    env_txt = cont.get("environment_lock") or f"Strict persistence of {setting} lighting."
    traits_txt = cont.get("immutable_traits") or "Realistic physical scaling and momentum."
    if isinstance(traits_txt, list):
        traits_txt = ", ".join(traits_txt)

    continuity_block = (
        f"--- CONTINUITY LOCK RULES ---\n"
        f"Character Morphology: {morph_txt}\n"
        f"Environment Consistency: {env_txt}\n"
        f"Immutable Invariants: {traits_txt}\n"
        f"-----------------------------"
    )

    # Package Summary & Overall Status
    all_statuses = [
        res_seedance.validation.status,
        res_universal.validation.status,
        res_gpt.validation.status,
        res_nano.validation.status
    ]

    if all(s == "PASS" for s in all_statuses):
        overall_status = "PASS"
    elif any(s == "FAIL" for s in all_statuses):
        overall_status = "FAIL"
    else:
        overall_status = "PARTIAL"

    return {
        "compiler_version": "PLB_PROMPT_COMPILER_V1",
        "overall_status": overall_status,
        "story_id": story.get("story_id", "STORY-01"),
        "title": story.get("title", "Story Concept"),
        "models": {
            "seedance_25": res_seedance.to_dict(),
            "universal_image": res_universal.to_dict(),
            "gpt_image": res_gpt.to_dict(),
            "nano_banana_pro": res_nano.to_dict()
        },
        # Direct prompt shortcuts
        "seedance_25_prompt": res_seedance.prompt_text,
        "universal_image_prompt": res_universal.prompt_text,
        "gpt_image_prompt": res_gpt.prompt_text,
        "nano_banana_pro_prompt": res_nano.prompt_text,
        "hero_frame_prompt": hero_frame_prompt,
        "shot_by_shot_prompts": shot_by_shot_prompts,
        "continuity_block": continuity_block
    }
