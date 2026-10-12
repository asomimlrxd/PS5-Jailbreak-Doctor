# PS5 Homebrew Doctor v0.7.5 — release-ready Windows EXE

This package prepares the project to publish a single Windows executable (`PS5HomebrewDoctor.exe`) through GitHub Releases. End users do not need Python, batch files, or the source files.

## Why the previous build failed

`Unable to find ... build\knowledge_base.json` comes from an old `.spec` file that referenced the knowledge database relative to the build folder. This workflow does **not** use `PS5HomebrewDoctor.spec`: it creates a temporary spec outside the repository and passes the absolute path to `knowledge_base.json`.

## Update your repository

1. Download and extract this ZIP.
2. Copy its contents into the root of your GitHub repository, including `.github`.
3. Replace the old workflow with `.github/workflows/build-windows-exe.yml`. Remove older workflows that still invoke `PS5HomebrewDoctor.spec` or reference `build\knowledge_base.json`.
4. Keep `app.py`, `app_paths.py`, `doctor_core.py`, `i18n.py`, `safe_actions.py`, `session_utils.py`, and `knowledge_base.json` at the repository root.
5. Commit and push to `main` or `master`.

## Test a build

Open **Actions**, choose **Build and publish PS5 Homebrew Doctor**, and inspect the latest run. When it succeeds, download `PS5HomebrewDoctor-Windows-x64` from the run's **Artifacts** section. The ZIP contains the EXE and its SHA-256 checksum. Actions artifacts expire after 30 days.

## Publish a stable public download

1. Open **Releases** → **Draft a new release**.
2. Create a new tag such as `v0.7.5` targeting the commit to distribute.
3. Set a release title and publish it.
4. The workflow builds the Windows EXE and attaches `PS5HomebrewDoctor.exe` and `PS5HomebrewDoctor.exe.sha256` to the release.
5. End users download just `PS5HomebrewDoctor.exe` from the release page. They do not need Python, batch files, or source files.

## Notes

- The Windows build runs on GitHub Actions, so the end user's PC does not compile anything.
- The EXE is not commercially code-signed; Windows SmartScreen may show a warning.
- Keep the ShadowMountPlus API restricted to a trusted local network and never expose it to the public Internet.

## Official documentation

- PyInstaller data files: https://pyinstaller.org/en/stable/spec-files.html
- GitHub Actions artifacts: https://docs.github.com/en/actions/tutorials/store-and-share-data
