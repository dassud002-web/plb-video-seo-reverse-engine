#!/usr/bin/env python3
"""
Base AI Provider Interface for PLB Story Forge
==============================================
Abstract interface for video story analysis, story generation, and expansion.
Enables local rule-based deterministic fallback and optional external providers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List

class BaseStoryProvider(ABC):
    """Abstract base class defining story engine capabilities."""

    @abstractmethod
    def analyze_story_video(self, video_path: Path) -> Dict[str, Any]:
        """Extracts narrative evidence from a video asset."""
        pass

    @abstractmethod
    def generate_stories(
        self,
        story_dna: Dict[str, Any],
        count: int = 50,
        mode: str = "AUTO",
        threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """Generates `count` diverse root stories derived from Story DNA."""
        pass

    @abstractmethod
    def expand_story(
        self,
        parent_story: Dict[str, Any],
        count: int = 50,
        mode: str = "AUTO",
        threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """Recursively expands a parent story into `count` child stories with lineage tracking."""
        pass

    @abstractmethod
    def score_story_similarity(self, story_a: Dict[str, Any], story_b: Dict[str, Any]) -> float:
        """Scores structural similarity between two story objects."""
        pass
