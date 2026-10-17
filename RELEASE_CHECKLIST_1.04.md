# Release checklist — PS5 Jailbreak Doctor 1.04

- [ ] Validate Python modules and knowledge-base schema.
- [ ] Confirm knowledge database version/hash match `updates.json`.
- [ ] Confirm the session comparison and current diagnostic regression tests pass.
- [ ] Confirm the Windows build creates `PS5JailbreakDoctor.exe` and a SHA-256 file.
- [ ] Test the executable on Windows.
- [ ] Test the HTTP connection and real log retrieval on a local PS5, where available.
- [ ] Review PT/EN UI text and compare/anonymized report actions.
- [ ] Keep the GitHub release in draft while the executable is being tested.
- [ ] Attach only the maintainer-tested `PS5JailbreakDoctor.exe` and `PS5JailbreakDoctor.exe.sha256`.
- [ ] Review the anonymized report output before sharing any diagnostic log externally.
- [ ] Publish only after all intended assets are attached and verified.

**Automation note:** the draft release is created by a main-branch commit whose message contains `[create-draft-release:v1.04]`. The build workflow no longer attaches or overwrites a release executable automatically.
