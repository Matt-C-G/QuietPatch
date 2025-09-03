#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_VERSION = """PackageIdentifier: QuietPatch.QuietPatch
PackageVersion: {version}
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
"""

TEMPLATE_INSTALLER = """PackageIdentifier: QuietPatch.QuietPatch
PackageVersion: {version}
Installers:
  - Architecture: x64
    InstallerType: zip
    InstallerUrl: {url}
    InstallerSha256: {sha256}
    NestedInstallerType: portable
    NestedInstallerFiles:
      - RelativeFilePath: run_quietpatch.bat
        PortableCommandAlias: quietpatch
    InstallModes: [silent, interactive]
    UpgradeBehavior: install
ManifestType: installer
ManifestVersion: 1.6.0
"""

TEMPLATE_LOCALE = """PackageIdentifier: QuietPatch.QuietPatch
PackageVersion: {version}
PackageName: QuietPatch
Publisher: QuietPatch
ShortDescription: Privacy-first vulnerability scanner with deterministic HTML reports and actionable remediation.
Tags:
  - security
  - vulnerability
  - cve
  - offline
  - scanner
License: MIT
LicenseUrl: https://github.com/Matt-C-G/QuietPatch/blob/main/LICENSE
Homepage: https://github.com/Matt-C-G/QuietPatch
ManifestType: defaultLocale
ManifestVersion: 1.6.0
"""


def main() -> int:
	ap = argparse.ArgumentParser()
	ap.add_argument("--out", default="manifests", help="Output root folder for manifests")
	ap.add_argument("--version", required=True)
	ap.add_argument("--sha256", required=True)
	ap.add_argument("--url", required=True)
	args = ap.parse_args()

	version = args.version.lstrip("v")
	root = Path(args.out) / "q" / "QuietPatch" / "QuietPatch" / version
	root.mkdir(parents=True, exist_ok=True)

	(root / "QuietPatch.QuietPatch.yaml").write_text(
		TEMPLATE_VERSION.format(version=version), encoding="utf-8"
	)
	(root / "QuietPatch.QuietPatch.installer.yaml").write_text(
		TEMPLATE_INSTALLER.format(version=version, url=args.url, sha256=args.sha256.upper()), encoding="utf-8"
	)
	(root / "QuietPatch.QuietPatch.locale.en-US.yaml").write_text(
		TEMPLATE_LOCALE.format(version=version), encoding="utf-8"
	)
	print(root)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
