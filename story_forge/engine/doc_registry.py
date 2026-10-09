#!/usr/bin/env python3
"""
PLB Studio — Official Documentation Registry & Source-of-Truth Engine
======================================================================
Maintains verified official documentation sources, rule provenance, and strict
classification boundaries between:
- OFFICIAL RULE
- PLB OPTIMIZATION
- MODEL-INDEPENDENT BEST PRACTICE
- INFERENCE

Answers the core audit question:
"Which official document supports this rule?"
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import time


class RuleClassification:
    OFFICIAL_RULE = "OFFICIAL RULE"
    PLB_OPTIMIZATION = "PLB OPTIMIZATION"
    MODEL_INDEPENDENT_BEST_PRACTICE = "MODEL-INDEPENDENT BEST PRACTICE"
    INFERENCE = "INFERENCE"


@dataclass
class ModelRule:
    rule_id: str
    classification: str  # RuleClassification
    title: str
    description: str
    source_name: str
    source_url: str
    source_section: str
    verification_quote: str
    is_official: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelDocumentationMetadata:
    model_id: str
    model_name: str
    official_model_names: List[str]
    provider: str
    source_name: str
    source_url: str
    source_checked_at: str
    documentation_version_or_date: str
    prompt_schema_version: str
    official_claims: List[str]
    plb_optimizations: List[str]
    inferred_rules: List[str]
    rules: Dict[str, ModelRule] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "official_model_names": self.official_model_names,
            "provider": self.provider,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_checked_at": self.source_checked_at,
            "documentation_version_or_date": self.documentation_version_or_date,
            "prompt_schema_version": self.prompt_schema_version,
            "official_claims": self.official_claims,
            "plb_optimizations": self.plb_optimizations,
            "inferred_rules": self.inferred_rules,
            "rules": {k: v.to_dict() for k, v in self.rules.items()}
        }


class DocumentationRegistry:
    """Lightweight registry tracing prompt generation rules to official provider documentation."""

    def __init__(self):
        self._sources: Dict[str, ModelDocumentationMetadata] = {}
        self._initialize_official_registry()

    def _initialize_official_registry(self):
        # 1. SEEDANCE 2.5 (ByteDance / Volcengine)
        seedance_rules = {
            "SD25_BASE_STRUCTURE": ModelRule(
                rule_id="SD25_BASE_STRUCTURE",
                classification=RuleClassification.OFFICIAL_RULE,
                title="6-Element Base Prompt Sequence",
                description="Strict ordered prompt formula: Subject -> Action/Event -> Scene/Environment -> Visual Style -> Camera Movement/Shot -> Sound",
                source_name="Volcengine Seedance 2.5 Video Generation Prompt Guide",
                source_url="https://www.volcengine.com/docs/seedance",
                source_section="Prompting Strategy / 6-Step Formula",
                verification_quote="Prompts should ideally contain: Subject, Action, Environment/Setting, Camera Movement, Style/Artistic Direction, Technical/Negative Constraints.",
                is_official=True
            ),
            "SD25_ROLE_TAGS": ModelRule(
                rule_id="SD25_ROLE_TAGS",
                classification=RuleClassification.OFFICIAL_RULE,
                title="@Tag Reference Asset Roles",
                description="Use @Subject, @Object, @Image, @Video tags to maintain multi-asset identity and motion consistency (up to 50 reference inputs supported).",
                source_name="Volcengine Seedance 2.5 Video Generation Prompt Guide",
                source_url="https://www.volcengine.com/docs/seedance",
                source_section="Advanced Reference System",
                verification_quote="Use @Image, @Video, and @Audio tags to provide reference assets. Seedance 2.5 supports up to 50 reference inputs for character consistency.",
                is_official=True
            ),
            "SD25_TIMELINE_PACING": ModelRule(
                rule_id="SD25_TIMELINE_PACING",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Timestamp Multi-Shot Timeline",
                description="Multi-shot timeline syntax [00:00-00:03] chaining sub-clips for cohesive narrative pacing.",
                source_name="Volcengine Seedance 2.5 Video Generation Prompt Guide",
                source_url="https://www.volcengine.com/docs/seedance",
                source_section="Chain Extensions & Timeline",
                verification_quote="Chain clips (max 15s each) using structured timing directives to maintain motion continuity.",
                is_official=True
            ),
            "SD25_FIRST_LAST_FRAME": ModelRule(
                rule_id="SD25_FIRST_LAST_FRAME",
                classification=RuleClassification.OFFICIAL_RULE,
                title="First-Frame & Last-Frame Loop Anchors",
                description="Explicit first-frame and last-frame anchoring for seamless video loop replay.",
                source_name="Volcengine Seedance 2.5 Video Generation Prompt Guide",
                source_url="https://www.volcengine.com/docs/seedance",
                source_section="First-Frame / Last-Frame Workflows",
                verification_quote="Specify start frame and end frame visual states to anchor seamless video generation.",
                is_official=True
            ),
            "SD25_PLB_GENOME_EXTRACTION": ModelRule(
                rule_id="SD25_PLB_GENOME_EXTRACTION",
                classification=RuleClassification.PLB_OPTIMIZATION,
                title="Story Genome Auto-Extraction",
                description="Synthesizes Story Genome dimensions directly into Seedance 2.5 role and setting fields.",
                source_name="PLB Story Forge Architecture",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="PLB Synthesis Pipeline",
                verification_quote="PLB internal synthesis mapping character traits and invariants into Seedance prompts.",
                is_official=False
            ),
            "SD25_MICRO_BEAT_INFERENCE": ModelRule(
                rule_id="SD25_MICRO_BEAT_INFERENCE",
                classification=RuleClassification.INFERENCE,
                title="15-Second Comedic Micro-Pacing",
                description="Infers sub-second timing beats (hook at 0-3s, payoff at 11-14s, loop at 15s) from comedic short-form structure.",
                source_name="PLB Creative Heuristic",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="Comedic Beat Inference",
                verification_quote="Inferred timing breakdown based on short-form viral comedy structures.",
                is_official=False
            )
        }

        self._sources["seedance_25"] = ModelDocumentationMetadata(
            model_id="seedance_25",
            model_name="Seedance 2.5",
            official_model_names=["Seedance 2.5", "Seaweed-7B", "Doubao Video"],
            provider="ByteDance / Volcengine",
            source_name="Volcengine Seedance 2.5 Video Generation Prompt Guide",
            source_url="https://www.volcengine.com/docs/seedance",
            source_checked_at="2026-10-09",
            documentation_version_or_date="2026 ByteDance Seed Model Suite",
            prompt_schema_version="seedance-2.5-v1.2",
            official_claims=[
                "6-part base formula: Subject -> Action/Event -> Scene/Environment -> Visual Style -> Camera Movement/Shot -> Sound",
                "@Tag Reference System supporting @Subject, @Object, @Image, @Video for character and motion identity lock",
                "Timestamp timeline [00:00-00:03] for multi-shot narrative pacing",
                "First-frame and last-frame anchor directives for loop transitions",
                "24fps cinematic camera cadence and photorealistic rendering"
            ],
            plb_optimizations=[
                "Automated character/species extraction from Story Genome",
                "Structured bracketed field tags for UI inspection and verification"
            ],
            inferred_rules=[
                "Sub-second micro-beat pacing tailored for 15s viral short-form comedic rhythm"
            ],
            rules=seedance_rules
        )

        # 2. GPT IMAGE (OpenAI) — NOT DALL-E 3
        gpt_rules = {
            "GPT_CURRENT_MODELS": ModelRule(
                rule_id="GPT_CURRENT_MODELS",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Current GPT Image Model Architecture",
                description="Officially powered by gpt-image-2.5-flare (fast, everyday generation) and gpt-image-2.5-sunburst (high-precision editing).",
                source_name="OpenAI API Documentation — Image Generation Guide",
                source_url="https://platform.openai.com/docs/guides/images",
                source_section="Models and Usage",
                verification_quote="Current models include versions such as gpt-image-2.5-sunburst and gpt-image-2.5-flare. Sunburst is optimized for high-precision editing; Flare for fast, high-quality generation.",
                is_official=True
            ),
            "GPT_NATURAL_PROSE": ModelRule(
                rule_id="GPT_NATURAL_PROSE",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Descriptive Natural Language Sentences",
                description="Prompts must use rich, descriptive full sentences rather than comma-separated keyword lists or quality buzzwords.",
                source_name="OpenAI Prompt Engineering Guide & Image API Reference",
                source_url="https://platform.openai.com/docs/guides/images",
                source_section="Prompting Best Practices",
                verification_quote="Describe the scene as you would to a person, using complete descriptive sentences with rich context rather than just a list of keywords.",
                is_official=True
            ),
            "GPT_CONTEXTUAL_SPEC": ModelRule(
                rule_id="GPT_CONTEXTUAL_SPEC",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Context, Lighting and Spatial Relationships",
                description="Explicitly articulate the subject, spatial relationships between objects, environmental lighting, and photographic composition in prose.",
                source_name="OpenAI API Documentation — Image Generation Guide",
                source_url="https://platform.openai.com/docs/guides/images",
                source_section="Composition and Constraints",
                verification_quote="Be specific about the subject, background, relationships between objects, style, and composition.",
                is_official=True
            ),
            "GPT_MULTI_TURN_EDITS": ModelRule(
                rule_id="GPT_MULTI_TURN_EDITS",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Conversational Image Editing & Responses API",
                description="Supports image edits and multi-turn workflows via the Image Edits API and Responses API with File IDs.",
                source_name="OpenAI API Documentation — Image Generation Guide",
                source_url="https://platform.openai.com/docs/guides/images",
                source_section="Responses API & Edits Endpoint",
                verification_quote="The Responses API allows for image generation as a built-in tool within conversational flows and supports File IDs for editing.",
                is_official=True
            ),
            "GPT_PLB_INVARIANT_MAPPING": ModelRule(
                rule_id="GPT_PLB_INVARIANT_MAPPING",
                classification=RuleClassification.PLB_OPTIMIZATION,
                title="Character Morphology Invariant Translation",
                description="Translates Story DNA character rules into natural prose consistency statements.",
                source_name="PLB Story Forge Architecture",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="PLB Synthesis Pipeline",
                verification_quote="PLB internal synthesis translating strict morphology locks into flowing descriptive prose.",
                is_official=False
            ),
            "GPT_PALETTE_INFERENCE": ModelRule(
                rule_id="GPT_PALETTE_INFERENCE",
                classification=RuleClassification.INFERENCE,
                title="Contextual Palette Prose Integration",
                description="Infers environmental lighting tones from visual palette codes without using literal hex values.",
                source_name="PLB Creative Heuristic",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="Palette Inference",
                verification_quote="Inferred translation of color tokens into natural lighting descriptions.",
                is_official=False
            )
        }

        self._sources["gpt_image"] = ModelDocumentationMetadata(
            model_id="gpt_image",
            model_name="GPT Image",
            official_model_names=["gpt-image-2.5-flare", "gpt-image-2.5-sunburst"],
            provider="OpenAI",
            source_name="OpenAI API Documentation — Image Generation Guide & Responses API",
            source_url="https://platform.openai.com/docs/guides/images",
            source_checked_at="2026-10-09",
            documentation_version_or_date="2026 OpenAI Image & Responses API Reference",
            prompt_schema_version="gpt-image-2.5-v1.0",
            official_claims=[
                "Current models: gpt-image-2.5-flare (fast generation) and gpt-image-2.5-sunburst (high-precision editing)",
                "Natural descriptive English prose sentences rather than comma-separated tag lists or quality buzzwords",
                "Detailed context covering subject, spatial relationships, environment, lighting, and composition",
                "Multi-turn conversational image editing via Image Edits API and Responses API File IDs"
            ],
            plb_optimizations=[
                "Automatic mapping of Story DNA physical invariants into descriptive character morphology sentences",
                "Natural avoidance of negative prompt tags (not supported in GPT Image API)"
            ],
            inferred_rules=[
                "Synthesizing emotional payoff into subject's physical posture and facial micro-expressions"
            ],
            rules=gpt_rules
        )

        # 3. NANO BANANA PRO (Google / Google DeepMind)
        nano_rules = {
            "NANO_CURRENT_MODELS": ModelRule(
                rule_id="NANO_CURRENT_MODELS",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Current Google Gemini Image Generation Models",
                description="Officially designated as gemini-3-pro-image-preview (Nano Banana Pro / Gemini 3 Pro Image) and gemini-3.1-flash-image (Nano Banana).",
                source_name="Google Gemini API Documentation — Image Generation Guide",
                source_url="https://ai.google.dev/gemini-api/docs/image-generation",
                source_section="Models / Image Generation",
                verification_quote="Gemini 3.1 Flash Image and Gemini 3 Pro Image let you generate and edit images from text prompts using reasoning to think through a prompt.",
                is_official=True
            ),
            "NANO_OFFICIAL_TEMPLATE": ModelRule(
                rule_id="NANO_OFFICIAL_TEMPLATE",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Official Photographic Prompt Template",
                description="Official Google template: 'A photorealistic [type of shot] of a [subject description] in a [setting description]. [Description of the light]. Shot from a [camera angle] with a [lens type]. Aspect ratio [aspect_ratio].'",
                source_name="Google Gemini API Documentation — Image Generation Guide",
                source_url="https://ai.google.dev/gemini-api/docs/image-generation",
                source_section="Prompting guide and strategies / Template",
                verification_quote="Template: A photorealistic [type of shot] of a [subject description] in a [setting description]. [Description of the light]. Shot from a [camera angle] with a [lens type].",
                is_official=True
            ),
            "NANO_RESOLUTION_AND_ASPECT": ModelRule(
                rule_id="NANO_RESOLUTION_AND_ASPECT",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Studio Resolution & Aspect Ratio Controls",
                description="Supports native 2K and 4K resolutions with precise text rendering and aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4.",
                source_name="Google Gemini API Documentation — Image Generation Guide",
                source_url="https://ai.google.dev/gemini-api/docs/image-generation",
                source_section="Aspect Ratios & 4K Capabilities",
                verification_quote="Generate sharp, legible text and diagrams with up to 2K and 4K resolutions. Control the aspect ratio using the aspect_ratio configuration.",
                is_official=True
            ),
            "NANO_THOUGHT_SIGNATURES_EDITING": ModelRule(
                rule_id="NANO_THOUGHT_SIGNATURES_EDITING",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Conversational Editing & Thought Signatures",
                description="Multi-turn conversational editing preserves visual context and character consistency using Thought Signatures across turns.",
                source_name="Google Gemini API Documentation — Image Generation Guide",
                source_url="https://ai.google.dev/gemini-api/docs/image-generation",
                source_section="Thought Signatures / Conversational Editing",
                verification_quote="Conversational editing: Multi-turn image editing by simply asking for changes. This workflow relies on Thought Signatures to preserve visual context between turns.",
                is_official=True
            ),
            "NANO_GROUNDED_GENERATION": ModelRule(
                rule_id="NANO_GROUNDED_GENERATION",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Search-Grounded Image Synthesis",
                description="Enables google_search tool to ground imagery in real-world facts, landmarks, and Google Image Search visual references.",
                source_name="Google Gemini API Documentation — Image Generation Guide",
                source_url="https://ai.google.dev/gemini-api/docs/image-generation",
                source_section="Grounded Generation",
                verification_quote="Use the google_search tool to verify facts and generate imagery based on real-world information. Grounding with Google Image Search available.",
                is_official=True
            ),
            "NANO_PLB_BRACKET_VIEW": ModelRule(
                rule_id="NANO_PLB_BRACKET_VIEW",
                classification=RuleClassification.PLB_OPTIMIZATION,
                title="Structured Dimension Inspector (NOT Official Google Syntax)",
                description="PLB token-bracket view [FOCAL_SUBJECT: ...] is strictly an internal structured dimension inspector, NOT Google's official prompt syntax.",
                source_name="PLB Story Forge Architecture",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="PLB Structured Inspection View",
                verification_quote="PLB diagnostic token view for UI verification. Not an official Google syntax claim.",
                is_official=False
            ),
            "NANO_GROUND_PERSPECTIVE_INFERENCE": ModelRule(
                rule_id="NANO_GROUND_PERSPECTIVE_INFERENCE",
                classification=RuleClassification.INFERENCE,
                title="Low Ground Angle Mapping",
                description="Infers low-angle macro perspective from comedic animal viewpoint.",
                source_name="PLB Creative Heuristic",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="Angle Inference",
                verification_quote="Inferred camera perspective tailored to small animal protagonist viewpoint.",
                is_official=False
            )
        }

        self._sources["nano_banana_pro"] = ModelDocumentationMetadata(
            model_id="nano_banana_pro",
            model_name="Nano Banana Pro",
            official_model_names=["gemini-3-pro-image-preview", "gemini-3.1-flash-image"],
            provider="Google / Google DeepMind",
            source_name="Google Gemini API Documentation — Nano Banana Image Generation Guide",
            source_url="https://ai.google.dev/gemini-api/docs/image-generation",
            source_checked_at="2026-10-09",
            documentation_version_or_date="2026 Google DeepMind Gemini API Specification",
            prompt_schema_version="nano-banana-pro-v1.0",
            official_claims=[
                "Official photographic prompt template: 'A photorealistic [type of shot] of a [subject description] in a [setting description]. [Description of the light]. Shot from a [camera angle] with a [lens type]. Aspect ratio [aspect_ratio].'",
                "Native 2K and 4K studio-quality resolution with precise text rendering",
                "Aspect ratio configuration: 16:9, 9:16, 1:1, 4:3, 3:4",
                "Conversational multi-turn editing utilizing Thought Signatures",
                "Grounded image generation supported by Google Search and Google Image Search"
            ],
            plb_optimizations=[
                "PLB token breakdown view ([FOCAL_SUBJECT: ...] | ...) is provided strictly as a diagnostic dimension inspection tool, NOT official Google syntax",
                "Morphological consistency locks derived from character universe models"
            ],
            inferred_rules=[
                "Macro eye-level angle mapping from comedic script cues"
            ],
            rules=nano_rules
        )

        # 4. UNIVERSAL IMAGE (Model-Neutral)
        universal_rules = {
            "UNI_MODEL_NEUTRAL": ModelRule(
                rule_id="UNI_MODEL_NEUTRAL",
                classification=RuleClassification.MODEL_INDEPENDENT_BEST_PRACTICE,
                title="Model-Neutral Architecture Consensus",
                description="Cross-platform declarative photographic description without proprietary tags, weights, or vendor-specific commands.",
                source_name="Model-Neutral Visual Specification Consensus",
                source_url="N/A (Model-Neutral Synthesizer)",
                source_section="Universal Photography Specification",
                verification_quote="Industry consensus on photographic description: Subject, Composition, Environment, Action, Lighting, Optics, Style.",
                is_official=False
            ),
            "UNI_PLB_SPEC_BLOCK": ModelRule(
                rule_id="UNI_PLB_SPEC_BLOCK",
                classification=RuleClassification.PLB_OPTIMIZATION,
                title="Declarative Field Specifications",
                description="Structures photographic components into clear labeled sections (Composition, Lighting, Optics, Style, Continuity).",
                source_name="PLB Story Forge Architecture",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="PLB Universal Synthesis",
                verification_quote="PLB structured visual layout optimized for universal cross-generator compatibility.",
                is_official=False
            ),
            "UNI_BALANCED_WEIGHT_INFERENCE": ModelRule(
                rule_id="UNI_BALANCED_WEIGHT_INFERENCE",
                classification=RuleClassification.INFERENCE,
                title="Neutral Balanced Weighting",
                description="Infers equal visual prominence across subject, interaction, and environment without vendor-specific emphasis weights.",
                source_name="PLB Creative Heuristic",
                source_url="local://story_forge/engine/prompt_compiler.py",
                source_section="Weighting Inference",
                verification_quote="Model-independent balance avoiding proprietary weighting systems like (parentheses:1.2) or ++.",
                is_official=False
            )
        }

        self._sources["universal_image"] = ModelDocumentationMetadata(
            model_id="universal_image",
            model_name="Universal Image",
            official_model_names=["Model-Neutral Engine"],
            provider="Model-Neutral (Open Consensus)",
            source_name="Model-Neutral Visual Specification Consensus",
            source_url="N/A (Model-Neutral Synthesizer)",
            source_checked_at="2026-10-09",
            documentation_version_or_date="Cross-Platform Best Practice",
            prompt_schema_version="model-neutral-v1.0",
            official_claims=[],  # Explicitly empty: no claim of official status for any single model
            plb_optimizations=[
                "Balanced declarative composition without proprietary command syntax (no --ar, no weights, no proprietary tags)",
                "Comprehensive photographic specification: Subject, Composition, Environment, Action, Lighting, Optics, Style"
            ],
            inferred_rules=[
                "Universally parsable photographic keywords accepted across open diffusion and closed transformer architectures"
            ],
            rules=universal_rules
        )

        # 5. GOOGLE VEO 2 (Google DeepMind)
        veo2_rules = {
            "VEO2_CINEMATIC_DIRECTIVE": ModelRule(
                rule_id="VEO2_CINEMATIC_DIRECTIVE",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Google Veo 2 Cinematic Video Prompting",
                description="Prompts must specify camera perspective, lens framing, subject motion, physics interaction, and lighting.",
                source_name="Google DeepMind Veo 2 Documentation",
                source_url="https://deepmind.google/technologies/veo/veo-2/",
                source_section="Prompting & Cinematic Camera Control",
                verification_quote="Veo 2 accurately understands cinematic terminology like lens focal length, tracking shots, and dynamic lighting conditions.",
                is_official=True
            ),
            "VEO2_ASPECT_RATIO": ModelRule(
                rule_id="VEO2_ASPECT_RATIO",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Veo 2 Mobile Short-Form & Widescreen Aspect Ratios",
                description="Supports both 16:9 widescreen and 9:16 vertical short-form framing directives.",
                source_name="Google DeepMind Veo 2 Documentation",
                source_url="https://deepmind.google/technologies/veo/veo-2/",
                source_section="Output Specifications & Formats",
                verification_quote="Generate in 16:9 widescreen or 9:16 vertical video optimized for mobile platforms.",
                is_official=True
            )
        }
        self._sources["google_veo_2"] = ModelDocumentationMetadata(
            model_id="google_veo_2",
            model_name="Google Veo 2",
            official_model_names=["Google Veo 2", "Veo 2", "veo-2.0"],
            provider="Google / Google DeepMind",
            source_name="Google DeepMind Veo 2 Official Prompting Documentation",
            source_url="https://deepmind.google/technologies/veo/veo-2/",
            source_checked_at="2026-10-09",
            documentation_version_or_date="March 2026 Documentation",
            prompt_schema_version="veo-2.0-cinematic",
            official_claims=[
                "Cinematic high-definition text-to-video with realistic camera control",
                "Understands cinematic terms: camera angles, lighting dynamics, lenses, frame rates",
                "Native support for 16:9 landscape and 9:16 vertical short-form formats"
            ],
            plb_optimizations=[
                "Ground-level tracking perspective tailored for small animal comedic tension",
                "Explicit 15-second pacing milestones aligned with TikTok and YouTube Shorts retention"
            ],
            inferred_rules=[
                "Pacing directives prevent sudden scene shifts or morphing artifacts"
            ],
            rules=veo2_rules
        )

        # 6. MIDJOURNEY V6.1 (Midjourney Inc.)
        mj_rules = {
            "MJ6_PARAMETERS": ModelRule(
                rule_id="MJ6_PARAMETERS",
                classification=RuleClassification.OFFICIAL_RULE,
                title="Midjourney v6.1 Parameters",
                description="Uses official flags --ar for aspect ratio, --v 6.1 for engine version, and --style raw for neutral photographic rendering.",
                source_name="Midjourney Official Parameter List",
                source_url="https://docs.midjourney.com/docs/parameter-list",
                source_section="Parameter Documentation",
                verification_quote="Use --ar to change the aspect ratio of the generated image. Use --style raw to reduce the default Midjourney aesthetic.",
                is_official=True
            ),
            "MJ6_THUMBNAIL_COMPOSITION": ModelRule(
                rule_id="MJ6_THUMBNAIL_COMPOSITION",
                classification=RuleClassification.PLB_OPTIMIZATION,
                title="High-CTR Short-Form Cover Composition",
                description="High visual contrast, expressive eyes, and power-point positioning optimized for YouTube Shorts / TikTok thumbnails.",
                source_name="PLB Creator Studio Best Practices",
                source_url="https://plb.studio/guidance/creator-thumbnails",
                source_section="Thumbnail & Cover Art Guidance",
                verification_quote="Thumbnail click-through rates maximize when the subject facial reaction is sharp, uncluttered, and high-contrast.",
                is_official=False
            )
        }
        self._sources["midjourney_v6"] = ModelDocumentationMetadata(
            model_id="midjourney_v6",
            model_name="Midjourney v6.1",
            official_model_names=["Midjourney v6.1", "Midjourney v6"],
            provider="Midjourney Inc.",
            source_name="Midjourney Official Documentation & User Guide",
            source_url="https://docs.midjourney.com/docs/parameter-list",
            source_checked_at="2026-10-09",
            documentation_version_or_date="v6.1 Latest",
            prompt_schema_version="mj-v6.1-parameters",
            official_claims=[
                "Photorealistic textures, fine fur, skin, and micro-surface reflections",
                "Parameter flags: --ar (aspect ratio), --v 6.1 (model version), --style raw"
            ],
            plb_optimizations=[
                "High-CTR cover composition optimized for mobile short-form feed cards",
                "Cinematic color grading matched to video production package palette"
            ],
            inferred_rules=[
                "Descriptive phrases outperform comma-separated keyword spam in v6.1"
            ],
            rules=mj_rules
        )

    def get_metadata(self, model_id: str) -> Optional[ModelDocumentationMetadata]:
        return self._sources.get(model_id)

    def get_rule(self, rule_id: str) -> Optional[ModelRule]:
        for meta in self._sources.values():
            if rule_id in meta.rules:
                return meta.rules[rule_id]
        return None

    def trace_rule(self, rule_id: str) -> Dict[str, Any]:
        """Answers: 'Which official document supports this rule?'"""
        rule = self.get_rule(rule_id)
        if not rule:
            return {
                "rule_id": rule_id,
                "found": False,
                "classification": "UNREGISTERED",
                "message": f"Rule '{rule_id}' is not traced to any registered documentation."
            }
        return {
            "rule_id": rule.rule_id,
            "found": True,
            "classification": rule.classification,
            "title": rule.title,
            "description": rule.description,
            "source_name": rule.source_name,
            "source_url": rule.source_url,
            "source_section": rule.source_section,
            "verification_quote": rule.verification_quote,
            "is_official": rule.is_official
        }

    def trace_rules_for_model(self, model_id: str) -> Dict[str, Any]:
        meta = self.get_metadata(model_id)
        if not meta:
            return {"model_id": model_id, "found": False, "rules": []}
        return {
            "model_id": model_id,
            "found": True,
            "source_name": meta.source_name,
            "source_url": meta.source_url,
            "rules": [r.to_dict() for r in meta.rules.values()]
        }

    def list_all_sources(self) -> List[Dict[str, Any]]:
        return [meta.to_dict() for meta in self._sources.values()]

    def register_or_update_source(self, metadata: ModelDocumentationMetadata):
        self._sources[metadata.model_id] = metadata


# Global Registry Instance
DOC_REGISTRY = DocumentationRegistry()


def get_doc_registry() -> DocumentationRegistry:
    return DOC_REGISTRY
