# -*- mode: python ; coding: utf-8 -*-
"""One-file Windows build with robust project-root/resource discovery."""
from pathlib import Path

_spec_dir = Path(SPECPATH).resolve()
_candidate_roots = [_spec_dir, _spec_dir.parent]
PROJECT_ROOT = None
for _root in _candidate_roots:
    if (_root / "app.py").is_file() and (_root / "knowledge_base.json").is_file():
        PROJECT_ROOT = _root
        break

if PROJECT_ROOT is None:
    _checked = "\n".join(str(p) for p in _candidate_roots)
    raise FileNotFoundError(
        "Could not locate both app.py and knowledge_base.json. "
        "Keep both in the project root. Checked:\n" + _checked
    )

ENTRY_SCRIPT = PROJECT_ROOT / "app.py"
KNOWLEDGE_BASE = PROJECT_ROOT / "knowledge_base.json"

# Passing an absolute source path means PyInstaller does not resolve it under build/.
datas = [(str(KNOWLEDGE_BASE), ".")]

a = Analysis(
    [str(ENTRY_SCRIPT)],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PS5HomebrewDoctor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
