## [0.4.4] - 2025-09-17
### Added
- Release pipeline now emits `SHA256SUMS.txt` for every tag (universal across OS).
- README includes simple verify commands (macOS/Linux & Windows).

### Changed
- Polished workflows: consistent Python 3.12 across jobs; clearer step names.
- Minor docs updates to reflect new release flow.

### Fixed
- Bulletproofed release triggers & guarded against branch-push runs.
- Ensured universal wheel build is stable and reproducible from tag.
- Made "release-gates" ordering deterministic and cross-platform timeout safe.

## [0.4.3] - 2025-09-17
### Added
- Bulletproof build steps; universal wheel; hermetic constraints; tag/version check.

### Fixed
- Build module shadowing: replaced `python -m build` with `pyproject-build`.
- Version mismatch: added validation to ensure tag matches project version.
- Workspace cleanup: added `rm -rf build/ dist/ *.egg-info` before building.
- Toolchain reliability: explicit installation of `setuptools`, `wheel`, `build`, and `pyproject-hooks`.
- Release-gates workflow: fixed step ordering and cross-platform timeout handling.

### Changed
- Updated all workflows (release, release-gates, pr-checks) with bulletproof build steps.
- Removed old workflow files that could cause conflicts.
- Ensured consistent Python 3.12 usage across all platforms.

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
