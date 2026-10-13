# Changelog

## 0.2.0 — Downloads & sources

- Added a Downloads & Sources tab for the community-maintained `homebrew.page` catalogue.
- Added project/release links for Orbit Store, Spectrum Library and PS5Library.
- Added a local GitHub-release source manager with a user authorization acknowledgement.
- Added a local download queue for homebrew artifacts with published SHA-256, progress display, cancellation, pause/resume when HTTP Range is supported, and checksum verification before the save action.
- Added manual provider bookmarks. Vikingfile opens externally; the app does not scrape or bypass provider checks.
- Added verification of the homebrew.page Ed25519-signed manifest, SHA-256 checks for the signed index and per-app JSON, and a local anti-rollback sequence check.
- Added lazy-loaded per-app details sourced from signed JSON records, including description, licence, release notes, source repository and official release link.
- Added local export/import for queue and custom sources.
- Kept commercial game dumps and unauthorized game-download catalogs out of the app.

### Limitations

- The live catalogue and GitHub release lookups require an internet connection and may be blocked by browser CORS or rate limits.
- Browser-based downloads are limited to 120 MB per artifact and are verified in memory. If direct browser fetching fails, use the official release page.
- Custom sources are stored locally and are not submitted to the public Atlas.

## 0.1.0 — Initial compatibility atlas

- Added 83 curated community observations, 46 distinct title names, 18 public sources and 7 format guides.
- Added bilingual search and filters for firmware, format, storage and reported state.
- Added source-linked game report cards and local contribution export.
- Added JSON/CSV export, responsive layout and dataset validation tests.
