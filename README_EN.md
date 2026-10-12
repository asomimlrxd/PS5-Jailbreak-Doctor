# PS5 Homebrew Doctor v0.7.1 — build a single EXE without local Python

This package uses GitHub Actions to build the app on a temporary Windows runner. You do **not** need Python or PyInstaller installed on your PC. The daily-use result is one file: `PS5HomebrewDoctor.exe`.

See `README_PT.md` for the step-by-step workflow setup in Portuguese. In brief: create a GitHub repository, upload the extracted project files (including `.github/workflows/build-windows-exe.yml`), commit, wait for the Actions workflow, then download the `PS5HomebrewDoctor-Windows-x64` artifact.
