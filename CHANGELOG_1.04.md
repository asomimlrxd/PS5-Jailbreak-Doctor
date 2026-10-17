# PS5 Jailbreak Doctor 1.04

## What's new

- **Read-only connection diagnostics:** checks TCP reachability, queries the ShadowMountPlus API version, and probes only API capabilities that the installed version advertises.
- **Better connection explanations:** differentiates a network timeout, a refused port, an unavailable API, and optional endpoints unsupported by older builds.
- **Compare log sessions:** compare the current log buffer against an earlier log file and review a local unified diff with counts of added and removed lines.
- **Anonymized share report:** creates a report with redaction forced on and local source paths reduced to filenames.
- **Updated diagnostics:** adds context-aware findings for API listener outages and scans stuck after a game exits. The new rules retain the original issue links and distinguish open reports from released fixes.
- **Knowledge base refresh:** updated to `2026.10.17.1`, with current guidance from the official ShadowMountPlus 1.7beta5 notes.
- **Refreshed UI:** updated slate-based theme palettes, clearer green accents, and slightly larger headings.

## Safety and limitations

- The app keeps the original HTTP API connection. No ELF relay is included or required.
- Connection checks do not change `config.ini`, settings, mounts, games, or scanner state.
- Reports are created locally and are not uploaded automatically.
- The ShadowMountPlus API has no authentication; use it only on a trusted local network.
- The comparison tool shows text differences; it does not prove that a changed line caused a problem.

## Release status

This release is prepared as a **draft**. The Windows executable is intentionally not attached by the automated workflow; the maintainer should add the built and tested `PS5JailbreakDoctor.exe` and its SHA-256 file before publishing.
