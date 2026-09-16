from timecapsule.analysis import (
    SnapshotFingerprint,
    classify_change,
    count_visual_changes,
    html_similarity,
    visual_change_score,
)


def fp(phash: str, html_hash: str = "x", html_length: int = 100) -> SnapshotFingerprint:
    return SnapshotFingerprint(phash=phash, html_hash=html_hash, html_length=html_length)


def test_identical_visual_hashes_have_zero_change():
    assert visual_change_score(fp("0000000000000000"), fp("0000000000000000")) == 0.0


def test_html_exact_hash_is_identical():
    assert html_similarity(fp("0" * 16, "same", 50), fp("f" * 16, "same", 999)) == 100.0


def test_html_length_similarity_is_bounded():
    assert html_similarity(fp("0" * 16, "a", 50), fp("f" * 16, "b", 100)) == 50.0


def test_change_labels_are_interpretable():
    assert classify_change(1.9) == "minimal"
    assert classify_change(4.9) == "small"
    assert classify_change(11.9) == "moderate"
    assert classify_change(12.0) == "large"


def test_count_visual_changes_uses_threshold():
    items = [fp("0000000000000000"), fp("0000000000000000"), fp("ffffffffffffffff")]
    assert count_visual_changes(items, threshold=4.0) == 1
