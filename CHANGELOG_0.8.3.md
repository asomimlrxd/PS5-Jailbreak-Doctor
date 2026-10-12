# PS5 Jailbreak Doctor 0.8.3

## Interface redesign
- Reorganised the window into a compact dashboard inspired by the supplied reference: header/preferences, a single connection/action bar, source/session panel, diagnostic results, console status/tools, and a docked log viewer.
- The console IP field is blank on first launch instead of assuming a specific home network address; the chosen address is saved locally after use.
- Kept the original HTTP API integration. No ELF relay is included.
- Preserved PT-PT/English selection, dark/light themes, source separation, context-aware rules, scanner inspection, reports, history and verified diagnostic-database updates.
- Standardised Windows executable naming to `PS5JailbreakDoctor.exe`.
- Updated README screenshots in Portuguese and English to show the new interface.

## Validation
- Python syntax checks and all 22 automated unit tests pass in the development environment.
- GUI smoke tests passed at 1280×720 and 1500×1000 virtual display sizes, including PT/EN switching and sample analysis.
- A native Windows GUI launch and a live PS5 connection still need testing.
