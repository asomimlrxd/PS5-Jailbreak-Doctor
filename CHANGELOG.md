## 0.8.2 — 2026-10-12

### Added
- Experimental `PS5JailbreakDoctorRelay.elf` payload built with the official PS5 Payload SDK in GitHub Actions and bundled into the Windows release.
- One-click relay discovery and loading from the Doctor, using the existing payload loader rather than editing ShadowMountPlus configuration.
- Read-only LAN relay endpoints for version, debug log, kernel log, scanner settings, and manual scan sources.
- A loopback alias at `127.0.0.1:10101` when needed to preserve ShadowMountPlus' bundled local launcher even if the existing API is bound to a specific console LAN IP.

### Changed
- Relay mode is now the default for new and legacy installs. The saved console IP is preserved, but a console-specific IP is no longer hard-coded for clean installations.
- Automatic relay discovery is best-effort; the relay still accepts a direct connection at the console's IP and TCP port `10102` if UDP discovery is blocked.
- A busy/unavailable UDP discovery port no longer prevents the relay's TCP service from starting.
- Updated Portuguese/English docs and guidance to state that `api_bind_address=0.0.0.0` is no longer required for relay mode.

### Safety and limitations
- The relay reads but never writes `/data/shadowmount/config.ini`; it does not use ShadowMountPlus' private Unix socket.
- The LAN interface accepts only private IPv4 clients and five read-only API paths. No authentication is added, so use trusted LAN only and never forward relay/API ports to the Internet.
- The relay requires ShadowMountPlus API to be enabled and a compatible payload loader when the ELF must be loaded. It does not modify `api_enabled`, install an autoloader, or persist through full reboot.
- This source package has not yet been built by GitHub Actions or validated on physical PS5 hardware in this environment. The ELF is expected to be produced by CI using the pinned official SDK release.

### Validation
- Python unit tests and C host syntax checks are run locally. Full SDK compilation and on-console testing remain required before treating the relay as stable.

## 0.8.1 — 2026-10-12

### Fixed
- Clarified ShadowMountPlus LAN API binding: recommend `api_bind_address=0.0.0.0` instead of binding to the console's specific LAN IP, which can make local loopback access to the ShadowMountPlus interface unavailable.
- Added a copyable config line and contextual connection-refused troubleshooting in Portuguese and English.
- Updated the `API_REFUSED` knowledge-base rule and both localized instructions to distinguish the API listener address from the target PS5 address entered in the Doctor.
- Expanded README setup guidance with the no-authentication/LAN trust warning.

### Safety
- The app does not change the PS5 config remotely. Users must replace the existing `api_bind_address` entry manually and must not expose the unauthenticated API to the Internet.

### Validation
- Python syntax, translation coverage, and knowledge-base manifest/checksum are validated locally; actual ShadowMountPlus GUI/LAN behaviour still needs a test on the user's console.

# Changelog

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
