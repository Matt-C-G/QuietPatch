#!/usr/bin/env python3
"""
qp_report module: Entry point for qp-report console script
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys

def _which_quietpatch() -> list[str]:
    # 1) Prefer the 'quietpatch' CLI if present
    qp = shutil.which("quietpatch")
    if qp:
        return [qp]
    # 2) Try invoking module via current interpreter
    return [sys.executable, "-m", "quietpatch"]

def _run(cmd: list[str]) -> int:
    try:
        # Print a concise echo for transparency
        print("$ " + " ".join(cmd))
        return subprocess.call(cmd)
    except FileNotFoundError as e:
        sys.stderr.write(f"[qp-report] Could not execute: {e}\n")
        return 127

def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="qp-report",
        description="Thin wrapper over `quietpatch report {tech|exec}`"
    )
    subparsers = parser.add_subparsers(dest="report_type", metavar="{tech|exec}")

    # We don't re-define all options; we pass all args through to QuietPatch.
    tech = subparsers.add_parser("tech", help="Generate technical report")
    tech.add_argument("rest", nargs=argparse.REMAINDER)

    execp = subparsers.add_parser("exec", help="Generate executive report")
    execp.add_argument("rest", nargs=argparse.REMAINDER)

    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        print("\nFor options, run:")
        print("  qp-report tech --help")
        print("  qp-report exec --help")
        return 0

    args, _ = parser.parse_known_args(argv)

    if args.report_type not in ("tech", "exec"):
        parser.print_help()
        return 2

    base = _which_quietpatch()
    # Forward to the QuietPatch CLI:
    # quietpatch report tech <rest...>   or   quietpatch report exec <rest...>
    cmd = base + ["report", args.report_type] + (args.rest or [])

    # If user did `--help` after the subcommand, it sits in args.rest and is forwarded.
    return _run(cmd)

if __name__ == "__main__":
    raise SystemExit(main())
