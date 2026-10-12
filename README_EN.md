# PS5 Jailbreak Doctor

**PS5 Jailbreak Doctor is a Windows diagnostic application for the PS5 homebrew community.** It analyzes logs, looks for known error patterns associated with tools such as ShadowMountPlus and KStuff Lite, shows the evidence it found, and suggests what to check next.

> **Important:** this is a diagnostic assistant, not a jailbreak or an exploit. It does not install payloads, change firmware, install games, or automatically apply fixes to the console.

[GitHub project overview](README.md) · [Português (Portugal)](README_PT.md)

![Diagnostic results using sample data](./docs/images/diagnostic-results.png)

*Illustrative results view using sample data. This does not mean that the shown errors are present on every console.*

## What it does

- **Analyzes log files:** import `.log`, `.txt`, and `.json` files for local analysis.
- **Fetches PS5 logs:** optionally connects to the ShadowMountPlus HTTP API over the local network to query the version and retrieve `debug.log` and the kernel log.
- **Detects known patterns:** compares log lines against the local `knowledge_base.json` database, which contributors can extend.
- **Uses additional context:** firmware, ShadowMountPlus and KStuff Lite versions, game location (USB/internal SSD), format (folder/image), and when the issue started can help determine how relevant a rule is.
- **Explains each finding:** shows evidence, estimated confidence, source status, limitations, and suggested next checks.
- **Surfaces unclassified errors:** likely error/crash lines without a matching rule can be shown for further investigation.
- **Exports reports:** save a report to share with the community. The anonymization option redacts IP addresses and common user-folder paths.
- **Supports English and Portuguese**, plus light and dark themes with a locally saved preference.
- **Offers a small number of reversible local rename actions:** only for supported `.ffpfs` / `.ffpfsc` filename scenarios. These actions rename a file on the Windows PC; they do not edit file contents or directly write to the PS5.

## How it works

![Diagnostic workflow](./docs/images/data-flow.png)

Analyzing imported logs works locally and does not require a console connection. To fetch logs automatically, the PC and PS5 must be on the same trusted local network and the ShadowMountPlus API must accept LAN connections.

![ShadowMountPlus connection panel](./docs/images/connection-panel.png)

*The original capture was edited to replace the private LAN IP address with a placeholder.*

## Quick start

### Analyze logs already on your PC

1. Open the application.
2. Select **Import logs** and choose one or more supported files.
3. Click **Analyze logs**.
4. Open a finding to review the matched lines, limitations, and suggested next steps.
5. Save a report if you need to ask the community or tool maintainers for help.

### Fetch logs directly from the PS5

1. Start ShadowMountPlus on the console and confirm its API is active.
2. If required by your installed build, configure the API to accept connections on a local network interface instead of only on `127.0.0.1`.
3. In the connection tab, enter the PS5's current LAN IP and API port. The app defaults to `10101`, but your setup may use a different port.
4. Click **Test connection**. Once the connection is confirmed, click **Get logs and analyze**.
5. Review the results and export a report if needed.

### Connection security

The integration uses the ShadowMountPlus API endpoints `/api/v1/version`, `/api/v1/debug-log`, and `/api/v1/kernel-log`. The supported API integration has no authentication. Keep it limited to a trusted local network, never forward the port on your router, and do not expose it to the Internet. The app does not configure the API on your behalf.

## Understanding the results

- A recognized pattern is **a lead**, not definitive proof of the root cause.
- Confidence is an estimate based on the rule and available evidence, not a statistical guarantee.
- A low-confidence or unclassified finding needs context: the complete log, firmware and tool versions, and the exact action that triggered the issue.
- Suggestions are presented for the user to review. The app does not change the PS5 through the API.

## Privacy and safety

- Logs are analyzed locally by default; they are not automatically uploaded to a project server.
- The console connection is only used when you click a connection or log-fetch button.
- Report anonymization redacts IP addresses and common user-folder paths. Review a report before sharing it: custom paths, usernames in other formats, title IDs, and other identifiers may remain.
- The ShadowMountPlus API has no authentication; use it only on a trusted private network.
- Before any local rename test, confirm the selected file and back it up if it is important. The app blocks rollback if the original name conflicts with an existing file or if the file has changed since the rename.

## Install and run

### Windows executable

On the repository's **Releases** page, download `PS5JailbreakDoctor.exe` from the latest release. The compiled executable does not require Python or `.bat` files on the end user's PC.

The GitHub Actions workflow builds for Windows x64 and attaches the executable and its SHA-256 file when a Release is published. The executable is not commercially code-signed; Windows SmartScreen may display a warning.

### Run from source

Python 3.10 or later is required. The UI and analysis use the Python standard library.

```powershell
py -3.12 app.py
```

### Build the EXE on Windows

For the documented build, use Python 3.12 and install PyInstaller:

```powershell
py -3.12 -m pip install --upgrade pyinstaller
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed --name PS5JailbreakDoctor --add-data "knowledge_base.json;." app.py
```

The output is written to `dist\PS5JailbreakDoctor.exe`. For public releases, the included `.github/workflows/build-windows-exe.yml` workflow is recommended because it validates the source files, bundles the knowledge database, and attaches a SHA-256 checksum to the Release.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Windows UI and ShadowMountPlus API integration |
| `doctor_core.py` | Diagnostic engine, evidence handling, and report generation |
| `knowledge_base.json` | Local error-pattern database, with sources and recommendations |
| `safe_actions.py` | Limited reversible local filename actions |
| `i18n.py` | English and Portuguese UI strings |
| `.github/workflows/build-windows-exe.yml` | Windows x64 executable workflow |
| `FONTES_PT.md` | Public references used by knowledge-base rules |

## Known limitations

The knowledge base does not cover every possible error, and community reports may apply only to specific versions or firmware. The app cannot guarantee that a recommendation will fix an issue. Check the original sources and confirm compatibility before changing files or settings.

## License and disclaimer

The project is distributed under the MIT License; see [`LICENSE.txt`](LICENSE.txt).

This is an experimental community project. It is not affiliated with, sponsored by, or endorsed by Sony Interactive Entertainment, PlayStation, etaHEN, ShadowMountPlus, or the KStuff Lite maintainers. Trademarks belong to their respective owners. Use the software at your own risk.
