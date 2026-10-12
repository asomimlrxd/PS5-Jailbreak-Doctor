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
