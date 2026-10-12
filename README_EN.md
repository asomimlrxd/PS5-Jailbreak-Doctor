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
- **Context-specific compatibility notes:** exact combinations of firmware, ShadowMountPlus/KStuff Lite versions, source type, and trigger can surface separately from log-matched diagnoses. A note is not proof that an error occurred.
- **Read-only scanner inspection:** queries custom scan roots and `manual.lst` sources through supported API endpoints. It does not start a rescan or change settings; older API builds may not expose this information.
- **Error timeline:** highlights suspicious log lines in file order while preserving the original text.
- **Verified diagnostic database updates:** manually check for a newer knowledge base, verify its SHA-256 and JSON schema, keep a backup, and roll back locally if needed. Only diagnostic rules are downloaded; logs are never uploaded.
- **Community-ready reports:** include knowledge-base version information and an optional follow-up template for whether suggested steps were tested and worked.
- **Surfaces unclassified errors:** likely error/crash lines without a matching rule can be shown for further investigation.
- **Exports reports:** save a report to share with the community. The anonymization option redacts IP addresses and common user-folder paths.
- **Language-aware reports:** reports follow the selected UI language, while original log evidence remains unchanged.
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

### Fetch logs directly from the PS5 (recommended mode)

1. Confirm ShadowMountPlus is running and its API is enabled. ShadowMountPlus 1.7 defaults to `api_enabled=1` and `api_bind_address=127.0.0.1`.
2. In the **PS5 connection** tab, keep **ELF relay (no config.ini changes)** selected. If no IP has been saved yet, enter the PS5's current LAN IP; Doctor stores it in its local preferences.
3. Confirm a compatible payload loader is active on the console (usually listening for payloads on TCP port `9021`) and click **Connect automatically (no config.ini)**.
4. Doctor first searches for an active relay. If none is found, it sends the bundled ELF to the PS5 address and waits for the relay to start. The relay uses TCP port `10102`; automatic discovery uses UDP `10103`.
5. When the app confirms the connection, click **Get logs and analyze**.

The relay reads `/data/shadowmount/config.ini` but never modifies it. If ShadowMountPlus is bound only to the console's specific LAN IP, the relay also attempts to expose `127.0.0.1:10101` locally so the bundled launcher can keep working. After a full PS5 reboot, the relay must be loaded again unless you already use a payload autoloader.

If broadcast discovery is blocked by the network/firewall, the app tries the saved PS5 IP directly. If no payload loader is listening on port `9021`, load `PS5JailbreakDoctorRelay.elf` through your existing loader and click **Find relay on network**. If the API is explicitly disabled (`api_enabled=0`), the relay will not enable it or edit the config; enable it through an official UI option if your build provides one, or reconfigure it manually.

### Direct API mode (fallback)

**Direct API** is for ShadowMountPlus versions/configurations that already allow LAN clients. The HTTP API listens on `127.0.0.1:10101` by default, so a PC cannot connect to it directly in that state. On builds with a LAN control in the ShadowMountPlus UI, use that instead of editing files. Manual `api_bind_address=0.0.0.0` remains an alternative, but is not required in Relay ELF mode.

### Connection security

The ShadowMountPlus API and relay have no user authentication. The relay accepts private IPv4 clients and exposes only read-only version, log, and scanner-configuration endpoints; logs may still contain identifiers. Use only a trusted private network and never forward TCP port `10102` or UDP port `10103` on a router, or expose the API to the Internet.

## Understanding the results

- A recognized pattern is **a lead**, not definitive proof of the root cause.
- Confidence is an estimate based on the rule and available evidence, not a statistical guarantee.
- A low-confidence or unclassified finding needs context: the complete log, firmware and tool versions, and the exact action that triggered the issue.
- Suggestions are presented for the user to review. The app does not change the PS5 through the API.

## Updating the diagnostic knowledge base

Use **More options → Update diagnostic database** to check for a newer knowledge base. After confirmation, the app downloads only `knowledge_base.json` from this repository, verifies the SHA-256 listed in `updates.json`, validates the schema and English translations, and stores it in the per-user app-data directory. The previous database is backed up locally and can be restored through **More options → Restore previous diagnostic database**. The executable itself is not silently updated, and no logs, reports, or console addresses are uploaded.

`updates.json` must be published alongside its matching `knowledge_base.json` on the default branch. Until both files are published, this update check will not find the new manifest.

## Privacy and safety

- Logs are analyzed locally by default; they are not automatically uploaded to a project server.
- The console connection is only used when you click a connection or log-fetch button.
- Report anonymization redacts IP addresses and common user-folder paths. Review a report before sharing it: custom paths, usernames in other formats, title IDs, and other identifiers may remain.
- The ShadowMountPlus API has no authentication; use it only on a trusted private network.
- Before any local rename test, confirm the selected file and back it up if it is important. The app blocks rollback if the original name conflicts with an existing file or if the file has changed since the rename.

## Install and run

### Windows executable

On the repository's **Releases** page, download `PS5HomebrewDoctor.exe` from the latest release. The compiled executable does not require Python or `.bat` files on the end user's PC.

The GitHub Actions workflow builds for Windows x64 and attaches the executable and its SHA-256 file when a Release is published. The executable is not commercially code-signed; Windows SmartScreen may display a warning.

### Run from source

Python 3.10 or later is required. The UI and analysis use the Python standard library.

```powershell
py -3.12 app.py
```

### Build the EXE on Windows

For the documented build, use Python 3.12 and install PyInstaller.

To include one-click connection, first compile `ps5-relay/relay.c` with the [official PS5 Payload SDK](https://github.com/ps5-payload-dev/sdk) and place the output at `ps5-relay/build/PS5JailbreakDoctorRelay.elf`. Then run:

```powershell
py -3.12 -m pip install --upgrade pyinstaller
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed --name PS5HomebrewDoctor --add-data "knowledge_base.json;." --add-data "ps5-relay/build/PS5JailbreakDoctorRelay.elf;payloads" app.py
```

The output is written to `dist\PS5HomebrewDoctor.exe`. For public releases, the included `.github/workflows/build-windows-exe.yml` workflow is recommended because it builds the relay ELF with a pinned SDK, validates source files, bundles the knowledge database, runs regression tests, and attaches SHA-256 checksums to the Release.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Windows UI and ShadowMountPlus API integration |
| `doctor_core.py` | Diagnostic engine, evidence handling, and report generation |
| `knowledge_base.json` | Local error-pattern database, with sources and recommendations |
| `safe_actions.py` | Limited reversible local filename actions |
| `i18n.py` | English and Portuguese UI strings |
| `updates.py` / `updates.json` | Explicit, checksum-verified diagnostic knowledge-base updates |
| `relay_client.py` | Relay discovery and loading through a compatible PS5 payload loader |
| `ps5-relay/relay.c` | Read-only LAN relay and local loopback alias for ShadowMountPlus |
| `UPDATES.md` | Maintainer guide for publishing database updates |
| `tests/` | Regression tests for localization, diagnostic context, and updates |
| `CHANGELOG.md` | User-facing changes by version |
| `.github/workflows/build-windows-exe.yml` | Builds the relay ELF and Windows x64 executable |
| `FONTES_PT.md` | Public references used by knowledge-base rules |

## Known limitations

The knowledge base does not cover every possible error, and community reports may apply only to specific versions or firmware. The app cannot guarantee that a recommendation will fix an issue. Check the original sources and confirm compatibility before changing files or settings.

## License and disclaimer

The project is distributed under the MIT License; see [`LICENSE.txt`](LICENSE.txt).

This is an experimental community project. It is not affiliated with, sponsored by, or endorsed by Sony Interactive Entertainment, PlayStation, etaHEN, ShadowMountPlus, or the KStuff Lite maintainers. Trademarks belong to their respective owners. Use the software at your own risk.
