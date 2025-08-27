# quietpatch/cli.py
import os
import platform
import sys

REQ = (3, 11)
if sys.version_info[:2] != REQ:
	print(f"QuietPatch PEX requires Python {REQ[0]}.{REQ[1]} on this release. "
	      f"Detected {sys.version.split()[0]}.", file=sys.stderr)
	sys.exit(86)

# Guardrails for Windows users
if platform.system() == "Windows" and sys.maxsize <= 2**31:
	print("QuietPatch requires 64-bit Python.", file=sys.stderr)
	sys.exit(86)


def main() -> None:
	# Import the real CLI entry point (kept at repo root for now)
	from qp_cli import main as real_main
	res = real_main()
	try:
		code = int(res or 0)
	except Exception:
		code = 0
	sys.exit(code)