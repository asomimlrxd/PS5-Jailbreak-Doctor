# PS5 Homebrew Doctor v0.7.4 — build a standalone EXE with GitHub Actions

This package builds a single `PS5HomebrewDoctor.exe` on a temporary Windows runner. The target PC does not need Python or BAT files.

The workflow builds directly from `app.py`, generates its temporary PyInstaller spec outside the repository, validates source files and the JSON knowledge base, and emits additional diagnostics if the EXE is missing. Replace the existing `.github/workflows/build-windows-exe.yml` and remove older/duplicate workflows that build the same app, or an old workflow may still be the one failing.

1. Extract this ZIP and replace the files in your GitHub repository.
2. Ensure `app.py`, `doctor_core.py`, `app_paths.py`, `i18n.py`, `safe_actions.py`, `session_utils.py`, and `knowledge_base.json` are at the repository root.
3. Replace `.github/workflows/build-windows-exe.yml`. The old `PS5HomebrewDoctor.spec` is no longer used and may be removed.
4. Commit the changes and open **Actions**.
5. Open the newest **Build PS5 Homebrew Doctor EXE** run and download the `PS5HomebrewDoctor-Windows-x64` artifact when green.
6. Extract the artifact and run `PS5HomebrewDoctor.exe`.

If it fails again, send the complete log from **Build one-file EXE directly from app.py**, not only the final missing-file message. The Windows executable is built in GitHub Actions; it is not included in this source ZIP.
