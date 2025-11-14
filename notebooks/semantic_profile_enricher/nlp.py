from __future__ import annotations

"""
Lightweight NLP helpers for keyword scoring, sentence extraction, and text normalization.
"""

import re
from typing import Iterable


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace for robust keyword matching."""
    lowered = text.lower()
    clean = re.sub(r"[^a-záéíóúñ0-9\s\/\-\+\.,]", " ", lowered)
    return re.sub(r"\s+", " ", clean).strip()


def keyword_score(text: str, keywords: Iterable[str]) -> float:
    """Return a simple score based on keyword hits normalized by length."""
    normalized = normalize_text(text)
    score = 0.0
    for keyword in keywords:
        if not keyword:
            continue
        count = normalized.count(normalize_text(keyword))
        score += float(count)
    if not normalized:
        return 0.0
    return score / max(1.0, len(normalized.split()) / 50.0)


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    """Check if any keyword appears in the text."""
    normalized = normalize_text(text)
    return any(normalize_text(keyword) in normalized for keyword in keywords)


def extract_evidence_snippet(text: str, keyword: str, window: int = 150) -> str:
    """Extract a short evidence snippet around the first keyword occurrence."""
    normalized_keyword = normalize_text(keyword)
    normalized_text = normalize_text(text)
    idx = normalized_text.find(normalized_keyword)
    if idx == -1:
        return normalized_text[:window]
    start = max(0, idx - window // 2)
    end = min(len(normalized_text), idx + window // 2)
    return normalized_text[start:end]


def tokenize_sentences(text: str) -> list[str]:
    """Split text into pseudo sentences."""
    cleaned = normalize_text(text)
    candidates = re.split(r"[.!?;\n]", cleaned)
    return [segment.strip() for segment in candidates if segment.strip()]

