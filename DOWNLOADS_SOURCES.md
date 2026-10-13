# Downloads & Sources — connector guide

Version 0.2.0 adds a separate download/source centre. It does not change the compatibility reports or host files.

References: [homebrew.page API specification](https://github.com/blackbearreloaded/ps5-homebrew-catalog/blob/main/docs/api.md), [Orbit Store project](https://github.com/saawant12/orbit-store-ps5), [Spectrum Library releases](https://github.com/Phoenixx1202/Spectrum-Library/releases), [PS5Library](https://github.com/rdiol12/PS5Library), and [Vikingfile terms](https://vikingfile.com/terms).

## Integrated sources

### `homebrew.page`

The Atlas queries the documented public JSON API (`/api/v1/index.json` and `/api/v1/apps/<TITLEID>.json`) to list native PS5 homebrew apps and read their project/release metadata. Before trusting those records, it verifies `manifest.sig` against the Ed25519 public keys published in the API documentation, checks the manifest sequence against the highest locally accepted sequence, and compares the exact SHA-256 of the index and app JSON files with the signed manifest. Direct queueing is available only when an artifact URL is on the accepted GitHub release hosts and the signed app record publishes a SHA-256 digest. The downloaded bytes are hashed locally and are only offered to the user after the digest and known size match.

### GitHub releases

Orbit Store, Spectrum Library and PS5Library are linked to their public project pages. The Atlas can query the latest GitHub release metadata for those projects and for a user-added public GitHub repository. It only offers direct queueing when GitHub exposes a SHA-256 `digest` for an attached asset and its asset URL is an approved release URL. Otherwise, the app opens the project/release page. The Atlas does not import the downstream game-download catalogs of external store applications.

### Custom sources

A user can bookmark any HTTPS project/release page locally, with an explicit authorization confirmation. GitHub repository links can be inspected through the public Releases API. Other hosts are bookmarks only; adding a URL does not make the Atlas crawl the site or attempt to obtain hidden download URLs. Importing a settings file revalidates HTTPS URLs, derives GitHub repository metadata from the URL instead of trusting imported fields, and sanitizes names.

### Vikingfile and other cyberlockers

Vikingfile is a manual external link only. This version does not scrape pages, reverse-engineer hidden APIs, resolve temporary links, bypass CAPTCHA/login checks, or build an index of unauthorized commercial game copies. The repository's investigation did not establish a supported public API for an automatic Vikingfile connector. If a provider later documents an API for lawful files, a separate connector can be reviewed against its terms and technical behavior.

## Browser download constraints

- The browser queue is for catalogued homebrew/project release assets, not commercial game dumps or patches.
- The direct download allowlist is currently `github.com`, `objects.githubusercontent.com` and `release-assets.githubusercontent.com`.
- An SHA-256 digest must be published by the source. The Atlas independently calculates SHA-256 on the received bytes and rejects mismatches. This checks integrity against the published value; it is not a malware scan, code audit or proof of distribution rights.
- Direct transfer requires the remote host to permit browser CORS. The Atlas does not proxy downloads or bypass host controls.
- The browser queue has a 120 MB per-file limit and holds partial data in memory. A pause can resume when the host supports HTTP Range; otherwise the item has to restart from byte zero. Reloading the page discards unfinished in-memory chunks.
- If CORS, the size, or a missing digest prevents direct transfer, the official source/release link is shown instead.
- Queue entries and custom source bookmarks are stored locally in the browser. Nothing is uploaded to an Atlas server.

## Adding another connector

1. Confirm the provider has a documented public API or stable public release interface.
2. Confirm its terms allow querying and that the content being surfaced is authorized for distribution.
3. Store source URLs, license/provenance notes, release date and a provider-published checksum when possible.
4. Do not treat availability of a URL as proof that a file is safe or legally redistributable.
5. Add regression tests for schema validation, HTTPS-only links, digest handling, size limits, error fallback, and both PT-PT/English UI strings.
