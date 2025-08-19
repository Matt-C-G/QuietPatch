# qp_cli.py
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from src.core.cve_mapper_new import run as run_mapping
from src.config.encryptor_new import decrypt_file, get_or_create_key
from src.core.rollback import snapshot_system_state, run_canary, rollback_last_checkpoint

def main():
    p = argparse.ArgumentParser(prog="quietpatch", description="Local CVE tracker with encrypted outputs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("scan", help="Scan installed software and map to CVEs.")
    p_run.add_argument("-o","--output", default="data", help="Output directory (default: data)")
    p_run.add_argument("--snapshot", action="store_true", help="Snapshot current app state")
    p_run.add_argument("--canary", action="store_true", help="Run canary checkpoint check")
    p_run.add_argument("--rollback", action="store_true", help="Rollback to last snapshot")

    p_show = sub.add_parser("show", help="Decrypt and print a file (e.g., data/vuln_log.json.enc)")
    p_show.add_argument("path", help="Path to encrypted file")
    p_show.add_argument("--pretty", action="store_true", help="Pretty-print JSON if applicable")
    
    p_report = sub.add_parser("report", help="Generate HTML report from encrypted scan data")
    p_report.add_argument("-i", "--input", required=True, help="Input encrypted file (e.g., data/vuln_log.json.enc)")
    p_report.add_argument("-o", "--output", required=True, help="Output HTML file")
    p_report.add_argument("--age-identity", help="AGE private key file")

    args = p.parse_args()
    if args.cmd == "scan":
        # Handle rollback operations first
        if args.snapshot:
            from src.core.scanner_helper import get_scanner
            scanner = get_scanner()
            apps = scanner.collect_installed_apps()
            print("Snapshot created:", snapshot_system_state(apps))
            return
        
        if args.canary:
            from src.core.scanner_helper import get_scanner
            scanner = get_scanner()
            apps = scanner.collect_installed_apps()
            print(run_canary(apps))
            return
        
        if args.rollback:
            print(rollback_last_checkpoint())
            return
        
        # Normal scan operation
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
    elif args.cmd == "report":
        from report.html import generate_report
        generate_report(args.input, args.output)
        print(f"Report generated: {args.output}")

if __name__ == "__main__":
    main()
