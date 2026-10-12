"""Paths for bundled resources and persistent user data."""
from __future__ import annotations
import os
import shutil
import sys
from pathlib import Path


def resource_path(name: str) -> Path:
    """Locate bundled read-only resources in source and PyInstaller one-file mode."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def data_dir() -> Path:
    """Use a per-user writable directory when frozen; keep source-mode files beside code.

    On the first branded launch, copy known user data from the previous app folder if
    the new destination does not already contain the corresponding file.
    """
    if getattr(sys, "frozen", False):
        appdata = Path(os.environ.get("APPDATA", str(Path.home())))
        base = appdata / "PS5JailbreakDoctor"
        legacy = appdata / "PS5HomebrewDoctor"
        base.mkdir(parents=True, exist_ok=True)
        if legacy.is_dir():
            for name in ("settings.json", "resolution_history.json", "changes_journal.json"):
                old_file = legacy / name
                new_file = base / name
                if old_file.is_file() and not new_file.exists():
                    try:
                        shutil.copy2(old_file, new_file)
                    except OSError:
                        # Migration is best-effort and must never stop the app from opening.
                        pass
    else:
        base = Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    return base


def data_path(name: str) -> Path:
    return data_dir() / name


def user_data_dir() -> Path:
    """Return the stable per-user writable directory used for remote KB updates.

    Unlike data_dir(), this never points at the source tree. This prevents an
    in-app update from overwriting project files when running from source.
    """
    appdata = Path(os.environ.get("APPDATA", str(Path.home())))
    base = appdata / "PS5JailbreakDoctor"
    base.mkdir(parents=True, exist_ok=True)
    legacy = appdata / "PS5HomebrewDoctor"
    if legacy.is_dir():
        for name in ("knowledge_base.json", "knowledge_base.backup-*.json"):
            if "*" in name:
                for old_file in legacy.glob(name):
                    new_file = base / old_file.name
                    if old_file.is_file() and not new_file.exists():
                        try:
                            shutil.copy2(old_file, new_file)
                        except OSError:
                            pass
            else:
                old_file = legacy / name
                new_file = base / name
                if old_file.is_file() and not new_file.exists():
                    try:
                        shutil.copy2(old_file, new_file)
                    except OSError:
                        pass
    return base


def user_data_path(name: str) -> Path:
    """Path for update-managed or user-specific files, outside the app bundle."""
    return user_data_dir() / name
