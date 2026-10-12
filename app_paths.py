"""Paths for bundled resources and persistent user data."""
from __future__ import annotations
import os
import sys
from pathlib import Path


def resource_path(name: str) -> Path:
    """Locate bundled read-only resources in source and PyInstaller one-file mode."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def data_dir() -> Path:
    """Use a per-user writable directory when frozen; keep source-mode files beside code."""
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "PS5HomebrewDoctor"
    else:
        base = Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    return base


def data_path(name: str) -> Path:
    return data_dir() / name
