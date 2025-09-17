## [0.4.2] - 2025-09-17
### Fixed
- Hermetic build: ensure build backend is present (setuptools.build_meta) by pinning toolchain in build constraints and `pip<25`.
- PR Checks: reliable wheel build with hashes.
- Release: multi-OS wheels uploaded as assets.

### Changed
- Updated README install/download instructions and version badge.

### Internal
- Constraints regenerated with hashes for build toolchain across platforms.

## v0.3.0
- Enhance HTML report UI with severity badges, stats banner, accessibility
- Add `doctor` command to diagnose environment and provide fixes
- Add package manager install paths (Homebrew, Scoop)
- Refactor README and docs site with improved design and content
- Policies presets and JSON export module docs

## v0.2.1
- Offline macOS agent (PEX) with LaunchDaemon service
- Policy engine: KEV/EPSS-aware, deterministic sorting
- Version-range aware matching (affects.json)
- Actionable remediation in HTML report (Action column)
- Hardware-first AGE encryption (no plaintext spill)
