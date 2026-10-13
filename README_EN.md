# PS5 Game Compatibility Atlas — English

The **PS5 Game Compatibility Atlas** organizes public PS5 homebrew compatibility reports by game, firmware, format, storage, symptoms, test scope, and original source. Version 0.2.0 adds a separate, provenance-first section for authorized homebrew downloads and project releases.

## Run locally

From the project directory, run:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. Compatibility browsing works as a static site. The downloads section calls public APIs only when you open that tab or query a release.

## Included in v0.2.0

- 83 test reports across 46 game/title names, 18 public sources, and 7 format guides.
- Search and filters by firmware, format, storage, and reported state, with contradictory reports kept separate.
- Portuguese (Portugal) and English, responsive dark interface, and local contribution export.
- **Downloads & Sources** tab backed by the community `homebrew.page` catalogue and direct metadata from its documented public API.
- Official project/release links for Orbit Store, Spectrum Library and PS5Library; the Atlas does not copy their downstream game catalogues.
- A local queue for eligible homebrew release assets, with progress, pause/resume where HTTP Range is supported, cancellation, size limits, and SHA-256 verification before the Save button becomes available. The Atlas also verifies homebrew.page’s Ed25519-signed manifest and the hashes of the index/app JSON files before trusting their metadata.
- Custom source bookmarks and import/export of local queue/source settings. GitHub repositories can be queried for their latest release; other sites open manually.
- Vikingfile is a manual external provider link. There is no scraper, temporary-link resolver, CAPTCHA bypass, or login bypass.
- The Atlas does not index or distribute unauthorized commercial game copies, dumps, or patches.

## Download integrity and limitations

The SHA-256 check confirms that bytes match the digest published by the catalogue/release; it is **not** a malware audit or proof that a publisher had distribution rights. Check the project, licence, and provenance before using a file. Direct browser downloads only work when the host permits CORS and the asset is on an approved release host; the per-file memory limit is 120 MB. If the browser cannot read the bytes, open the official release page instead. Partially downloaded bytes exist in memory only and are lost on reload.

No files are hosted by this project. Downloads are limited to catalogued homebrew or project releases with published integrity metadata. Source links are not endorsements.

## Interpreting compatibility results

Each record describes one setup and one observation; it does not establish universal compatibility. A short test is not a completed playthrough, and conflicting reports remain separate. Evidence quality describes how well the report is documented, not a statistical probability of success.

Current ShadowMountPlus documentation recommends `.ffpkg`/UFS for general use, describes `.exfat` as a compatibility option for some titles, and labels PFS (`.ffpfs`/`.ffpfsc`) experimental. Per-game reports may differ from these maintainer notes.

## Tests and publication

Run the local validation commands before publishing:

```bash
python build_data.py
python -m unittest discover -s tests -v
node --check app.js
node --check downloads.js
node tests/downloads-smoke.cjs
```

To deploy on GitHub Pages, upload the project root to a new repository, then choose **Settings → Pages → Deploy from a branch → main → /(root)**. See `METHODOLOGY.md`, `DOWNLOADS_SOURCES.md` and `CONTRIBUTING.md` for evidence rules, connector limitations and permitted sources.
