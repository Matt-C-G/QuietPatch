# qp_cli.py
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path


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


def _get_db_snapshot_date() -> str | None:
    """Try to determine the DB snapshot date from available sources."""
    try:
        # Check for qp_db-latest.tar.* or legacy db-latest.tar.* in data directory
        data_dir = Path(os.environ.get("QP_DATA_DIR", "data"))
        for ext in [".tar.zst", ".tar.gz", ".tar.bz2"]:
            db_file = data_dir / f"qp_db-latest{ext}"
            if db_file.exists():
                # Get file modification time as a proxy for snapshot date
                mtime = db_file.stat().st_mtime
                return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        for ext in [".tar.zst", ".tar.gz", ".tar.bz2"]:
            db_file = data_dir / f"db-latest{ext}"
            if db_file.exists():
                mtime = db_file.stat().st_mtime
                return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

        # Check for any qp_db-*.tar.* files (preferred) or legacy db-*.tar.*
        for db_file in list(data_dir.glob("qp_db-*.tar.*")) + list(data_dir.glob("db-*.tar.*")):
            base_name = db_file.stem.split('.')[0]
            # qp_db-YYYYMMDD or db-YYYYMMDD
            date_part = base_name.replace("qp_db-", "").replace("db-", "")
            if len(date_part) >= 8 and date_part[:8].isdigit():
                # Try to extract date from filename (db-YYYYMMDD.tar.*)
                date_str = date_part[:8]
                try:
                    return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
                except ValueError:
                    continue
    except Exception:
        pass
    return None


def main():
    # Handle --version flag first, before parsing subcommands
    if "--version" in sys.argv:
        # Try local development version first, then installed package
        try:
            from quietpatch import __version__
            version = __version__
        except ImportError:
            try:
                version = metadata.version("quietpatch")
            except metadata.PackageNotFoundError:
                version = "dev"
        print(f"QuietPatch {version}")
        sys.exit(0)

    p = argparse.ArgumentParser(
        prog="quietpatch", description="Local CVE tracker with encrypted outputs."
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Scan installed software and map to CVEs.")
    p_scan.add_argument("-o", "--output", default="data", help="Output dir (default: data)")
    p_scan.add_argument(
        "--also-report", action="store_true", help="Immediately render HTML report after scan"
    )
    p_scan.add_argument(
        "--open", action="store_true", help="Open the report in a browser (interactive runs)"
    )
    p_scan.add_argument("--json-out", metavar="PATH", help="Also write machine-readable JSON report")
    p_scan.add_argument("--sarif", metavar="PATH", help="Write SARIF v2.1.0 file for CI")
    p_scan.add_argument("--csv", metavar="PATH", help="Write CSV export")
    p_scan.add_argument("--sbom", metavar="PATH", help="Scan from CycloneDX JSON (no host probing)")
    p_scan.add_argument("--offline", action="store_true", help="Disable online lookups; use local DB only")
    p_scan.add_argument("--html", action="store_true", help="Alias for --also-report")
    p_scan.add_argument("--out", metavar="PATH", help="Write HTML report to this path (implies --also-report)")
    p_scan.add_argument(
        "--exit-on",
        metavar="SEVERITY",
        choices=["low", "medium", "high", "critical"],
        help="Exit non-zero if any finding meets or exceeds this severity",
    )
    p_scan.add_argument("--snapshot", action="store_true", help="Snapshot current app state")
    p_scan.add_argument("--canary", action="store_true", help="Run canary checkpoint check")
    p_scan.add_argument("--rollback", action="store_true", help="Rollback to last snapshot")
    p_scan.add_argument(
        "--scheduled-run", action="store_true", help="Run scheduled vulnerability scan"
    )

    # report
    p_rep = sub.add_parser("report", help="Render HTML report from JSON/ENCRYPTED input")
    p_rep.add_argument(
        "-i", "--input", required=True, help="Path to vuln_log.json or vuln_log.json.enc"
    )
    p_rep.add_argument("-o", "--output", default="report.html", help="Output HTML path")
    p_rep.add_argument("--age-identity", help="Path to age identity (for .enc input)")
    p_rep.add_argument(
        "--open", action="store_true", help="Open the report in a browser (interactive runs)"
    )
    p_rep.add_argument("--evidence", help="Create evidence pack ZIP file")
    p_rep.add_argument(
        "--include",
        nargs="+",
        choices=["html", "json", "csv", "sbom", "signatures", "manifest"],
        default=["html"],
        help="Evidence pack contents",
    )

    # show (keep existing functionality)
    p_show = sub.add_parser("show", help="Decrypt and print a file (e.g., data/vuln_log.json.enc)")
    p_show.add_argument("path", help="Path to encrypted file")
    p_show.add_argument("--pretty", action="store_true", help="Pretty-print JSON if applicable")

    # version (detailed version info)
    sub.add_parser("version", help="Show detailed version information")

    # clean (cache and database cleanup)
    p_clean = sub.add_parser("clean", help="Clean cache and database files")
    p_clean.add_argument("--cache", action="store_true", help="Clean PEX cache directory")
    p_clean.add_argument("--db", action="store_true", help="Clean database files")
    p_clean.add_argument("--all", action="store_true", help="Clean everything (cache + db)")

    # db
    db = sub.add_parser("db", help="Database actions")
    db_sub = db.add_subparsers(dest="db_cmd", required=True)

    db_refresh = db_sub.add_parser("refresh", help="Refresh offline DB snapshot")
    db_refresh.add_argument(
        "--mirror",
        action="append",
        help="Preferred mirror(s). Can repeat; file:/// or https://",
        default=[],
    )
    db_refresh.add_argument(
        "--fallback", action="append", help="Fallback mirror(s). Can repeat", default=[]
    )
    db_refresh.add_argument("--tor", help="SOCKS5h host:port (e.g. 127.0.0.1:9050)")
    db_refresh.add_argument("--privacy", default="strict", choices=["strict", "normal"])
    db_refresh.add_argument("--pubkey", help="minisign public key path for manifest verification")

    db_fetch = db_sub.add_parser("fetch", help="Fetch offline DB snapshot from GitHub Releases")
    db_fetch.add_argument("--tag", default=os.environ.get("QUIETPATCH_DB_TAG", "db"), help="Release tag (default: db)")
    db_fetch.add_argument(
        "--filename",
        default=os.environ.get("QUIETPATCH_DB_FILE", "qp_db-latest.tar.zst"),
        help="Artifact filename (default: qp_db-latest.tar.zst)",
    )

    # env (namespace)
    env = sub.add_parser("env", help="Environment utilities")
    env_sub = env.add_subparsers(dest="env_cmd", required=True)
    env_doc = env_sub.add_parser("doctor", help="Print environment diagnostics with fix steps")
    env_doc.add_argument("--db", help="Path to db snapshot (optional)")
    env_doc.add_argument("--out-dir", default="./reports", help="Report output directory")
    env_doc.add_argument("--open-check", action="store_true", help="Check if default browser is available")

    # doctor (legacy alias)
    p_doc = sub.add_parser("doctor", help="Diagnose environment and provide fixes")
    p_doc.add_argument("--db", help="Path to db snapshot (optional)")
    p_doc.add_argument("--out-dir", default="./reports", help="Report output directory")
    p_doc.add_argument("--open-check", action="store_true", help="Check if default browser is available")

    args = p.parse_args()

    if args.cmd == "scan":
        # Import here to avoid loading heavy dependencies at module level
        from src.core.cve_mapper_new import run as run_mapping

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

        # Main mapping flow (host or SBOM mode)
        if args.offline:
            os.environ["QP_OFFLINE"] = "1"

        if getattr(args, "sbom", None):
            try:
                # SBOM mode: parse CycloneDX and map to CVEs
                from quietpatch.sbom.cyclonedx import load_components
                from src.config.config_new import load_config
                from src.core.cve_mapper_new import map_apps_to_cves

                components = load_components(args.sbom)
                seed_apps = [{"app": c.get("name") or "", "version": c.get("version") or ""} for c in components]
                cfg = load_config()
                mapping = map_apps_to_cves(seed_apps, cfg)
                vuln_path = outdir / "vuln_log.json"
                vuln_path.write_text(json.dumps(mapping, indent=2))
                # Provide similar locator structure as run_mapping
                locs = {"apps": str(outdir / "apps.json"), "vulns": str(vuln_path)}
            except Exception as e:
                print(f"SBOM mapping failed: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            locs = run_mapping(str(outdir))

        # Apply actions to the scan results
        try:
            from src.core.actions import decorate_actions, load_actions

            actions_file = Path(os.environ.get("QP_ACTIONS_FILE", "config/actions.yml"))
            actions_map = load_actions(actions_file)

            # Read the vulnerability data and apply actions
            vuln_path = Path(outdir) / "vuln_log.json"
            if vuln_path.exists():
                vuln_data = json.loads(vuln_path.read_text())
                vuln_data_with_actions = decorate_actions(vuln_data, actions_map)
                vuln_path.write_text(json.dumps(vuln_data_with_actions, indent=2))
                print(f"Actions applied to {len(vuln_data_with_actions)} apps")
        except Exception as e:
            print(f"Warning: Could not apply actions: {e}")

        print(json.dumps(locs, indent=2))

        if args.also_report or args.html or getattr(args, "out", None):
            # Import here to avoid loading heavy dependencies at module level
            from quietpatch.report.html import generate_report
            from src.config.encryptor_v3 import decrypt_file

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
            html_out = Path(args.out) if getattr(args, "out", None) else (outdir / "report.html")
            html_out.parent.mkdir(parents=True, exist_ok=True)
            generate_report(str(src_json), str(html_out))
            print(f"Report generated: {html_out}")
            if args.open:
                _open_file(str(html_out))

        # Optional JSON export alongside HTML/plain mapping
        if getattr(args, "json_out", None):
            try:
                from quietpatch.report.jsonout import to_json
                try:
                    from src.core.policy import load_policy
                except Exception:
                    load_policy = None  # type: ignore

                src_json = outdir / "vuln_log.json"
                if src_json.exists():
                    apps_data = json.loads(src_json.read_text())
                else:
                    apps_data = []

                policy_doc = {}
                if load_policy:
                    try:
                        from dataclasses import asdict
                        policy_doc = asdict(load_policy())
                    except Exception:
                        policy_doc = {}
                meta = {"db_snapshot": _get_db_snapshot_date() or ""}

                Path(args.json_out).write_text(to_json(apps_data, policy_doc, meta), encoding="utf-8")
                print(f"JSON report written: {args.json_out}")
            except Exception as e:
                print(f"Warning: Could not write JSON report: {e}")

        # CSV/SARIF exports
        if getattr(args, "csv", None) or getattr(args, "sarif", None):
            try:
                src_json = outdir / "vuln_log.json"
                apps_data = json.loads(src_json.read_text()) if src_json.exists() else []
                if getattr(args, "csv", None):
                    from quietpatch.report.exports import write_csv
                    write_csv(apps_data, args.csv)
                    print(f"CSV report written: {args.csv}")
                if getattr(args, "sarif", None):
                    from quietpatch.report.exports import write_sarif
                    try:
                        tool_ver = metadata.version("quietpatch")
                    except metadata.PackageNotFoundError:
                        tool_ver = "dev"
                    write_sarif(apps_data, args.sarif, tool_name="QuietPatch", tool_version=tool_ver)
                    print(f"SARIF report written: {args.sarif}")
            except Exception as e:
                print(f"Warning: Could not write exports: {e}")

        # Exit-on severity threshold (after outputs are written)
        if getattr(args, "exit_on", None):
            try:
                src_json = outdir / "vuln_log.json"
                apps_data = json.loads(src_json.read_text()) if src_json.exists() else []
                rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                threshold = rank[args.exit_on]
                hit = False
                for app in apps_data or []:
                    vulns = app.get("vulnerabilities") or app.get("cves") or []
                    for v in vulns:
                        sev = str((v or {}).get("severity") or "unknown").lower()
                        if rank.get(sev, 0) >= threshold:
                            hit = True
                            break
                    if hit:
                        break
                sys.exit(2 if hit else 0)
            except Exception:
                # On error evaluating threshold, do not fail the run
                sys.exit(0)
        else:
            sys.exit(0)

    elif args.cmd == "report":
        # Import here to avoid loading heavy dependencies at module level
        from quietpatch.report.html import generate_report
        from src.config.encryptor_v3 import decrypt_file

        inp = Path(args.input)
        html_out = Path(args.output)
        html_out.parent.mkdir(parents=True, exist_ok=True)
        if inp.suffix == ".enc":
            raw = decrypt_file(
                str(inp), age_identity=args.age_identity or os.environ.get("AGE_IDENTITY")
            )
            tmp = html_out.with_suffix(".tmp.json")
            tmp.write_bytes(raw)
            try:
                generate_report(str(tmp), str(html_out))
            finally:
                try:
                    tmp.unlink()
                except Exception:
                    pass
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

    elif args.cmd == "db" and args.db_cmd == "refresh":
        from src.datafeed.updater import refresh_db

        data_dir = os.environ.get("QP_DATA_DIR", str(Path("data").resolve()))
        mirrors = []
        env_mirror = os.environ.get("QP_MIRROR")
        env_fallback = os.environ.get("QP_FALLBACK_MIRROR")
        if env_mirror:
            mirrors.append(env_mirror)
        mirrors.extend(args.mirror or [])
        if env_fallback:
            mirrors.append(env_fallback)
        mirrors.extend(args.fallback or [])
        if not mirrors:
            print(
                "No mirrors provided. Use --mirror or set QP_MIRROR / QP_FALLBACK_MIRROR.",
                file=sys.stderr,
            )
            sys.exit(2)
        info = refresh_db(
            data_dir=data_dir,
            mirrors=mirrors,
            tor_socks=args.tor,
            privacy=args.privacy,
            pubkey_path=args.pubkey,
        )
        print(json.dumps(info, indent=2))
        return

    elif args.cmd == "db" and getattr(args, "db_cmd", None) == "fetch":
        import requests
        from quietpatch.db_loader import _decompress
        from quietpatch.errors import fail

        APP_HOME = Path(os.environ.get("QUIETPATCH_HOME", Path.home() / ".quietpatch"))
        APP_HOME.mkdir(parents=True, exist_ok=True)
        db_dir = APP_HOME / "db"
        db_dir.mkdir(parents=True, exist_ok=True)

        tag = os.environ.get("QUIETPATCH_DB_TAG", "db")
        filename = os.environ.get("QUIETPATCH_DB_FILE", "qp_db-latest.tar.zst")
        url = f"https://github.com/Matt-C-G/QuietPatch/releases/download/{tag}/{filename}"
        dest = db_dir / filename
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            fail(
                "DB-404",
                f"No database at {url}",
                [
                    "Impact: Offline scan unavailable.",
                    "Check tag/file or set QUIETPATCH_DB_FILE=qp_db-YYYYMMDD.tar.zst",
                ],
            )
        dest.write_bytes(r.content)
        print(f"Downloaded: {dest}")
        _decompress(dest)
        print("✅ DB ready.")

    elif args.cmd == "version":
        db_date = _get_db_snapshot_date()
        # Try local development version first, then installed package
        try:
            from quietpatch import __version__
            version = __version__
        except ImportError:
            try:
                version = metadata.version("quietpatch")
            except metadata.PackageNotFoundError:
                version = "dev"
        print(f"QuietPatch {version}")
        if db_date:
            print(f"Database snapshot: {db_date}")
        else:
            print("Database snapshot: Not found")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Platform: {sys.platform}")

    elif args.cmd == "clean":
        cleaned = []

        # Clean cache if requested
        if args.cache or args.all:
            cache_dir = Path(os.environ.get("PEX_ROOT", ""))
            if not cache_dir:
                # Default cache locations
                if sys.platform == "win32":
                    cache_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "quietpatch" / ".pexroot"
                else:
                    cache_dir = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "quietpatch" / ".pexroot"

            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                cleaned.append(f"Cache: {cache_dir}")

        # Clean database if requested
        if args.db or args.all:
            data_dir = Path(os.environ.get("QP_DATA_DIR", "data"))
            db_files = list(data_dir.glob("db-*.tar.*"))
            if db_files:
                for db_file in db_files:
                    db_file.unlink()
                    cleaned.append(f"Database: {db_file.name}")

        if cleaned:
            print("✓ Cleaned:")
            for item in cleaned:
                print(f"  - {item}")
        else:
            print("Nothing to clean. Use --cache, --db, or --all")

        if not (args.cache or args.db or args.all):
            print("Specify what to clean: --cache, --db, or --all")

    elif args.cmd == "show":
        # Import here to avoid loading heavy dependencies at module level
        from src.config.encryptor_v3 import decrypt_file

        raw = decrypt_file(args.path)
        try:
            obj = json.loads(raw.decode())
            if args.pretty:
                print(json.dumps(obj, indent=2))
            else:
                print(raw.decode())
        except Exception:
            sys.stdout.buffer.write(raw)

    elif args.cmd == "env" and getattr(args, "env_cmd", None) == "doctor":
        from quietpatch.commands.doctor import run as doctor_run
        sys.exit(doctor_run(db=getattr(args, "db", None), out_dir=getattr(args, "out_dir", None), open_check=getattr(args, "open_check", False)))

    elif args.cmd == "doctor":
        from quietpatch.commands.doctor import run as doctor_run
        # Create parser lazily (argparse already parsed). To keep structure, we add earlier.
        # Execute
        sys.exit(doctor_run(db=getattr(args, "db", None), out_dir=getattr(args, "out_dir", None), open_check=getattr(args, "open_check", False)))


if __name__ == "__main__":
    main()
