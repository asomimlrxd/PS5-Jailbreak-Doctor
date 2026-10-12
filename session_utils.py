"""Small pure helpers for keeping log sources separate and testable."""
from __future__ import annotations

from typing import Iterable

def format_source_blocks(outputs: Iterable[tuple[str, str]]) -> tuple[str, list[str]]:
    """Format a fresh snapshot of logs fetched from the PS5. Empty outputs are ignored.

    Callers should replace their current log buffer with the returned text rather
    than append it; that prevents demo/imported text from contaminating a live run.
    """
    blocks: list[str] = []
    labels: list[str] = []
    for label, content in outputs:
        clean_label = str(label).strip() or "Log sem nome"
        clean_content = str(content).strip()
        if not clean_content:
            continue
        blocks.append(f"===== SOURCE: {clean_label} =====\n{clean_content}")
        labels.append(clean_label)
    return "\n\n".join(blocks), labels
