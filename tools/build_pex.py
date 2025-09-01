#!/usr/bin/env python3
"""
Build PEX executable for QuietPatch.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def build_pex(platform: str, out_dir: Path) -> None:
    """Build PEX for specified platform."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal source directory for PEX
    build_dir = Path("build/minimal")
    if build_dir.exists():
        import shutil

        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # Copy essential files
    essential_files = ["src/", "qp_cli.py", "config/", "requirements.txt"]

    for item in essential_files:
        src = Path(item)
        dst = build_dir / item
        if src.is_dir():
            import shutil

            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())

    # Build PEX
    pex_name = f"quietpatch-{platform}.pex"
    pex_path = out_dir / pex_name

    cmd = [
        "pex",
        "--python-shebang",
        "/usr/bin/env python3",
        "--output-file",
        str(pex_path),
        "--entry-point",
        "qp_cli:main",
        "-r",
        "requirements.txt",
        ".",
    ]

    print(f"Building PEX for {platform}...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=build_dir, capture_output=True, text=True)

    if result.returncode != 0:
        print("PEX build failed:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)

    # Verify PEX was created
    if pex_path.exists():
        size_mb = pex_path.stat().st_size / (1024 * 1024)
        print(f"✅ PEX built successfully: {pex_path}")
        print(f"   Size: {size_mb:.1f} MB")
    else:
        print("❌ PEX file not found after build")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build PEX for QuietPatch")
    parser.add_argument(
        "--platform",
        required=True,
        help="Target platform (macos-latest, ubuntu-latest, windows-latest)",
    )
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output directory")

    args = parser.parse_args()
    build_pex(args.platform, args.out)


if __name__ == "__main__":
    main()
