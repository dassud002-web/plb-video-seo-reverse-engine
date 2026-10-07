#!/usr/bin/env python3
"""
Diversity Engine for PLB Story Forge
====================================
Enforces deterministic anti-duplication checks across generated stories.
Calculates n-gram token similarity and multi-field structural distances.
Guarantees diversity scores >= configurable threshold (default 0.70).
"""

import re
from typing import Dict, Any, List, Set, Tuple

STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with",
    "by", "of", "from", "up", "about", "into", "over", "after", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "but", "if", "or", "because", "as", "until", "while", "that", "this"
}

def normalize_text_to_tokens(text: str) -> Set[str]:
    """Tokenizes and cleans text, removing punctuation and common stop words."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = {w for w in cleaned.split() if len(w) > 2 and w not in STOP_WORDS}
    return tokens

def generate_bigrams(text: str) -> Set[str]:
    """Extracts adjacent word bigrams for phrase-level overlap detection."""
    if not text:
        return set()
    words = re.findall(r"\b\w+\b", text.lower())
    if len(words) < 2:
        return set(words)
    return {f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)}

def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard index between two token sets."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

def compute_pairwise_story_similarity(story_a: Dict[str, Any], story_b: Dict[str, Any]) -> float:
    """
    Computes weighted structural similarity between two story objects.
    Compares premise, title, conflict, twist, and payoff.
    """
    # 1. Premise token + bigram similarity
    tokens_p_a = normalize_text_to_tokens(story_a.get("one_line_premise", ""))
    tokens_p_b = normalize_text_to_tokens(story_b.get("one_line_premise", ""))
    bigrams_p_a = generate_bigrams(story_a.get("one_line_premise", ""))
    bigrams_p_b = generate_bigrams(story_b.get("one_line_premise", ""))
    premise_sim = 0.6 * jaccard_similarity(tokens_p_a, tokens_p_b) + 0.4 * jaccard_similarity(bigrams_p_a, bigrams_p_b)

    # 2. Title similarity
    tokens_t_a = normalize_text_to_tokens(story_a.get("title", ""))
    tokens_t_b = normalize_text_to_tokens(story_b.get("title", ""))
    title_sim = jaccard_similarity(tokens_t_a, tokens_t_b)

    # 3. Conflict similarity
    tokens_c_a = normalize_text_to_tokens(story_a.get("conflict", ""))
    tokens_c_b = normalize_text_to_tokens(story_b.get("conflict", ""))
    conflict_sim = jaccard_similarity(tokens_c_a, tokens_c_b)

    # 4. Payoff & Twist similarity
    tokens_pay_a = normalize_text_to_tokens(story_a.get("payoff", "") + " " + story_a.get("twist", ""))
    tokens_pay_b = normalize_text_to_tokens(story_b.get("payoff", "") + " " + story_b.get("twist", ""))
    payoff_sim = jaccard_similarity(tokens_pay_a, tokens_pay_b)

    # Weighted Composite Similarity Score (0.0 = completely distinct, 1.0 = identical)
    composite = (0.40 * premise_sim) + (0.20 * title_sim) + (0.20 * conflict_sim) + (0.20 * payoff_sim)
    return round(composite, 4)

def calculate_story_diversity_score(candidate: Dict[str, Any], existing_stories: List[Dict[str, Any]]) -> float:
    """
    Computes diversity score of candidate against all existing stories in the corpus.
    diversity_score = 1.0 - max(similarity_with_any_existing)
    """
    if not existing_stories:
        return 1.0

    max_sim = 0.0
    for other in existing_stories:
        sim = compute_pairwise_story_similarity(candidate, other)
        if sim > max_sim:
            max_sim = sim

    diversity_score = round(max(0.0, 1.0 - max_sim), 2)
    return diversity_score

def check_diversity_threshold(
    candidate: Dict[str, Any],
    existing_stories: List[Dict[str, Any]],
    threshold: float = 0.70
) -> Tuple[bool, float]:
    """
    Validates whether candidate meets or exceeds the required diversity threshold.
    """
    score = calculate_story_diversity_score(candidate, existing_stories)
    return (score >= threshold, score)
