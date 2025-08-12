# qp_cli.py
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from src.core.cve_mapper_new import run as run_mapping
from src.config.encryptor_new import decrypt_file, get_or_create_key

def main():
    p = argparse.ArgumentParser(prog="quietpatch", description="Local CVE tracker with encrypted outputs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("scan", help="Scan installed software and map to CVEs.")
    p_run.add_argument("-o","--output", default="data", help="Output directory (default: data)")

    p_show = sub.add_parser("show", help="Decrypt and print a file (e.g., data/vuln_log.json.enc)")
    p_show.add_argument("path", help="Path to encrypted file")
    p_show.add_argument("--pretty", action="store_true", help="Pretty-print JSON if applicable")

    args = p.parse_args()
    if args.cmd == "scan":
        locs = run_mapping(args.output)
        print(json.dumps(locs, indent=2))
    elif args.cmd == "show":
        raw = decrypt_file(args.path)
        try:
            obj = json.loads(raw.decode())
            if args.pretty:
                print(json.dumps(obj, indent=2))
            else:
                print(raw.decode())
        except Exception:
            sys.stdout.buffer.write(raw)

if __name__ == "__main__":
    main()
