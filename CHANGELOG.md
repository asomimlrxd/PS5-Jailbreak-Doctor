# Changelog

## 1.04 — Diagnostic intelligence, connection checks and report tools

### Added
- Read-only connection diagnostics: TCP reachability, ShadowMountPlus API version, advertised read capabilities, and a clear explanation of local-only API binding versus LAN access.
- Local session comparison: compare current logs with an earlier file, inspect a unified diff, count added/removed lines, and save the diff locally.
- Dedicated anonymized report export: forces log redaction and reduces local source paths to filenames; the user is reminded to review the report before sharing.
- Two context-aware knowledge-base rules for the HTTP API listener becoming unresponsive and scans remaining queued after a game exits.
- Current guidance from the official ShadowMountPlus 1.7beta5 release notes, while keeping open issues and pull requests clearly labelled as unconfirmed.
- Automated regression tests for session comparison, recent diagnostic signatures, dataset/manifest integrity, and the Windows build.

### Updated
- Refined dark/light palettes with slate surfaces, clearer green accents, larger heading typography, and a more structured diagnostic experience.
- Added current sources to the knowledge database and refreshed the update manifest to database version `2026.10.17.1`.
- Preserved the original HTTP API integration. The abandoned ELF relay client was removed; no ELF is included or required.
- Removed automatic executable upload on release events. Draft releases can be created without attaching or overwriting a binary.

### Safety and limitations
- Connection checks call only version, log-read, settings-read, and manual-list endpoints. They do not write ShadowMountPlus settings, rescan, mount, uninstall, move, or delete anything.
- The ShadowMountPlus API has no authentication. Use it only on a trusted local network and never forward the port to the public internet.
- The session comparison is text-based; differences are not automatically treated as the cause of an error.
- Community reports and an open pull request are not represented as confirmed fixes.

### Validation status
- Automated source/database validation and regression tests run in GitHub Actions.
- The Windows executable build runs separately in GitHub Actions.
- Real connection testing on a physical PS5 and final executable testing remain manual checks. The v1.04 GitHub release will stay in draft until the maintainer adds the tested executable.


## 1.02 — Release maintenance

- Align the in-app version with the next release label (`1.02`).
- Standardize the Windows executable and checksum filename as `PS5JailbreakDoctor.exe`.
- Remove the abandoned optional ELF relay from the PyInstaller spec; the project uses the original ShadowMountPlus HTTP API integration.
- Replace the empty GitHub Actions workflow with CI checks for Python syntax, diagnostic rule patterns, English translations, compatibility notes, and the update-manifest SHA-256.


## 0.8.0 — 2026-10-12

### Added
- Context-specific compatibility notes for documented firmware/tool/source combinations.
- Chronological timeline of suspicious log lines, retaining original log evidence unchanged.
- Pre-flight checks when context is incomplete or logs point to scanner/source-layout issues.
- Optional read-only scanner inspection via `/api/v1/settings` and `/api/v1/manual/list`, with graceful fallback when a console API version does not expose these endpoints.
- Duplicate Title ID diagnosis with a warning not to assume file corruption.
- Explicit diagnostic knowledge-base updater using `updates.json`, SHA-256 validation, schema/translation checks, local backup, and rollback.
- Community-friendly report follow-up fields for recording whether a suggestion was tested and worked.
- Regression coverage for localization, timeline extraction, compatibility matching, scanner response parsing, pre-flight checks, and update validation.

### Updated
- Reflected the maintainer code fix linked to ShadowMountPlus issues #145 and #147 while noting that the exact released build must still be confirmed.
- Expanded scanner guidance for `scanpath`, `scan_depth`, `sce_sys/param.json`, and `manual.lst` based on the versioned ShadowMountPlus 1.7 documentation.
- Marked older reports (including the historical image-cache report) as version-specific rather than universal fixes.
- Preserved local analysis and explicit user confirmation; the updater downloads only the diagnostic JSON and does not upload logs.

### Validation
- Python compilation and offline unit tests run locally.
- Windows executable build and real PS5 integration still require validation through the Windows workflow and a local console.
