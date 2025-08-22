# qp_cli.py
from __future__ import annotations
import argparse, json, sys, os, subprocess, time
from pathlib import Path

from src.config.encryptor_v3 import decrypt_file  # for report
from src.core.cve_mapper_new import run as run_mapping  # scan path
from report.html import generate_report  # assumes you have generate_report(input_json, out_html)

def _open_file(path: str) -> None:
    """Best-effort open in default browser when interactive."""
    try:
        # Avoid opening from services/CI
        if not sys.stdout.isatty():
            print(f"Report ready: file://{Path(path).resolve()}")
            return
        if sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        elif os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        print(f"Report ready: file://{Path(path).resolve()}")

def main():
    p = argparse.ArgumentParser(prog="quietpatch", description="Local CVE tracker with encrypted outputs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Scan installed software and map to CVEs.")
    p_scan.add_argument("-o","--output", default="data", help="Output dir (default: data)")
    p_scan.add_argument("--also-report", action="store_true", help="Immediately render HTML report after scan")
    p_scan.add_argument("--open", action="store_true", help="Open the report in a browser (interactive runs)")
    p_scan.add_argument("--snapshot", action="store_true", help="Snapshot current app state")
    p_scan.add_argument("--canary", action="store_true", help="Run canary checkpoint check")
    p_scan.add_argument("--rollback", action="store_true", help="Rollback to last snapshot")
    p_scan.add_argument("--scheduled-run", action="store_true", help="Run scheduled vulnerability scan")

    # report
    p_rep = sub.add_parser("report", help="Render HTML report from JSON/ENCRYPTED input")
    p_rep.add_argument("-i","--input", required=True, help="Path to vuln_log.json or vuln_log.json.enc")
    p_rep.add_argument("-o","--output", default="report.html", help="Output HTML path")
    p_rep.add_argument("--age-identity", help="Path to age identity (for .enc input)")
    p_rep.add_argument("--open", action="store_true", help="Open the report in a browser (interactive runs)")
    p_rep.add_argument("--evidence", help="Create evidence pack ZIP file")
    p_rep.add_argument("--include", nargs="+", choices=["html", "json", "csv", "sbom", "signatures", "manifest"], 
                     default=["html"], help="Evidence pack contents")

    # show (keep existing functionality)
    p_show = sub.add_parser("show", help="Decrypt and print a file (e.g., data/vuln_log.json.enc)")
    p_show.add_argument("path", help="Path to encrypted file")
    p_show.add_argument("--pretty", action="store_true", help="Pretty-print JSON if applicable")

    args = p.parse_args()

    if args.cmd == "scan":
        # Handle rollback operations first
        if args.snapshot:
            from src.core.scanner_helper import get_scanner
            scanner = get_scanner()
            apps = scanner.collect_installed_apps()
            from src.core.rollback import snapshot_system_state
            print("Snapshot created:", snapshot_system_state(apps))
            return
        
        if args.canary:
            from src.core.scanner_helper import get_scanner
            scanner = get_scanner()
            apps = scanner.collect_installed_apps()
            from src.core.rollback import run_canary
            print(run_canary(apps))
            return
        
        if args.rollback:
            from src.core.rollback import rollback_last_checkpoint
            print(rollback_last_checkpoint())
            return
        
        if args.scheduled_run:
            # Scheduled run - just do the scan without output
            run_mapping(args.output)
            print("Scheduled vulnerability scan completed")
            return

        outdir = Path(args.output)
        outdir.mkdir(parents=True, exist_ok=True)

        # optional DB refresh (non-blocking) - simplified
        try:
            # Note: DB refresh logic can be added here later
            pass
        except Exception:
            pass

        locs = run_mapping(str(outdir))
        print(json.dumps(locs, indent=2))

        if args.also_report:
            # prefer plaintext if present; else decrypt
            src_json = outdir / "vuln_log.json"
            if not src_json.exists():
                # decrypt to temp then render
                enc = outdir / "vuln_log.json.enc"
                if not enc.exists():
                    print("No vuln_log.json(.enc) found for reporting", file=sys.stderr)
                    sys.exit(1)
                raw = decrypt_file(str(enc), age_identity=os.environ.get("AGE_IDENTITY") or None)
                src_json.write_bytes(raw)
            html_out = outdir / "report.html"
            generate_report(str(src_json), str(html_out))
            print(f"Report generated: {html_out}")
            if args.open:
                _open_file(str(html_out))

    elif args.cmd == "report":
        inp = Path(args.input)
        html_out = Path(args.output)
        html_out.parent.mkdir(parents=True, exist_ok=True)
        if inp.suffix == ".enc":
            raw = decrypt_file(str(inp), age_identity=args.age_identity or os.environ.get("AGE_IDENTITY"))
            tmp = html_out.with_suffix(".tmp.json")
            tmp.write_bytes(raw)
            try:
                generate_report(str(tmp), str(html_out))
            finally:
                try: tmp.unlink()
                except Exception: pass
        else:
            generate_report(str(inp), str(html_out))
        print(html_out)
        if args.open:
            _open_file(str(html_out))
        
        # Create evidence pack if requested
        if args.evidence:
            from tools.evidence_pack import build_evidence_pack
            build_evidence_pack(args.input, args.output, args.evidence, args.include)
            print(f"Evidence pack created: {args.evidence}")

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
