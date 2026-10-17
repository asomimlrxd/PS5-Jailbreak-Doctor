"""Local, read-only comparison helpers for PS5 diagnostic log sessions."""
from __future__ import annotations

from collections import Counter
from difflib import unified_diff


def compare_log_texts(
    baseline_text: str,
    current_text: str,
    baseline_name: str = "previous.log",
    current_name: str = "current.log",
) -> dict:
    """Compare two log texts without modifying either input or sending data anywhere."""
    if not isinstance(baseline_text, str) or not isinstance(current_text, str):
        raise TypeError("Both log sessions must be text.")
    baseline = baseline_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    current = current_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    if len(baseline) > 200_000 or len(current) > 200_000:
        raise ValueError("A session exceeds the 200,000-line safety limit.")

    old_counts = Counter(line for line in baseline if line.strip())
    new_counts = Counter(line for line in current if line.strip())
    added = list((new_counts - old_counts).elements())
    removed = list((old_counts - new_counts).elements())
    diff = "\n".join(
        unified_diff(
            baseline,
            current,
            fromfile=baseline_name or "previous.log",
            tofile=current_name or "current.log",
            lineterm="",
        )
    )
    return {
        "baseline_lines": len(baseline),
        "current_lines": len(current),
        "added_count": len(added),
        "removed_count": len(removed),
        "added_lines": added[:50],
        "removed_lines": removed[:50],
        "diff": diff,
    }
