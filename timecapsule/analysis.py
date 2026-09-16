from __future__ import annotations

from dataclasses import dataclass

import imagehash


@dataclass(frozen=True)
class SnapshotFingerprint:
    phash: str
    html_hash: str
    html_length: int


def visual_change_score(a: SnapshotFingerprint, b: SnapshotFingerprint) -> float:
    """Return normalized perceptual-hash distance as a percentage."""
    h1 = imagehash.hex_to_hash(a.phash)
    h2 = imagehash.hex_to_hash(b.phash)
    max_bits = h1.hash.size
    return round((h1 - h2) / max_bits * 100, 1)


def html_similarity(a: SnapshotFingerprint, b: SnapshotFingerprint) -> float:
    """Lightweight HTML similarity signal based on exact hash and page length."""
    if a.html_hash == b.html_hash:
        return 100.0
    if max(a.html_length, b.html_length) == 0:
        return 100.0
    return round(min(a.html_length, b.html_length) / max(a.html_length, b.html_length) * 100, 1)


def classify_change(score: float) -> str:
    if score < 2:
        return "minimal"
    if score < 5:
        return "small"
    if score < 12:
        return "moderate"
    return "large"


def count_visual_changes(items: list[SnapshotFingerprint], threshold: float = 4.0) -> int:
    if len(items) < 2:
        return 0
    return sum(
        visual_change_score(previous, current) >= threshold
        for previous, current in zip(items, items[1:])
    )
