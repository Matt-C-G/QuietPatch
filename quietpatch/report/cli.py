from __future__ import annotations
import argparse, sys, os
from .tech import build_tech_report
from .exec import build_exec_report

def add_report_subparser(sub: argparse._SubParsersAction, template_dir: str):
    p = sub.add_parser("report", help="Generate offline reports")
    sp = p.add_subparsers(dest="report_cmd", required=True)

    t = sp.add_parser("tech", help="Technical (engineer) report")
    t.add_argument("--scan", required=True)
    t.add_argument("--out", required=True, help="HTML output path")
    t.add_argument("--pdf", default=None, help="Optional PDF output")
    t.add_argument("--policy", default=None)
    t.add_argument("--bundle", default=None)
    t.add_argument("--prev", default=None)
    t.add_argument("--watermark", default=None, help="Optional watermark banner text")
    t.add_argument("--approval", default=None, help="Path to approval.json")
    t.add_argument("--sign", action="store_true", help="Sign output(s) with minisign")
    t.add_argument("--sign-key", default=None, help="Path to minisign secret key")
    t.set_defaults(func=lambda args: build_tech_report(
        template_dir, scan=args.scan, out_html=args.out, policy=args.policy,
        bundle=args.bundle, prev_scan=args.prev, out_pdf=args.pdf, watermark=args.watermark,
        approval=args.approval, sign=args.sign, sign_key=args.sign_key))

    e = sp.add_parser("exec", help="Executive (CIO/CISO/Board) report")
    e.add_argument("--scan", required=True)
    e.add_argument("--out", required=True, help="PDF output path")
    e.add_argument("--html", default=None, help="Optional HTML output")
    e.add_argument("--kpi", default=None)
    e.add_argument("--trend-dir", default=None)
    e.add_argument("--watermark", default=None, help="Optional watermark banner text")
    e.add_argument("--approval", default=None, help="Path to approval.json")
    e.add_argument("--sign", action="store_true", help="Sign output(s) with minisign")
    e.add_argument("--sign-key", default=None, help="Path to minisign secret key")
    e.set_defaults(func=lambda args: build_exec_report(
        template_dir, scan=args.scan, out_pdf=args.out, kpi=args.kpi,
        trend_dir=args.trend_dir, out_html=args.html, watermark=args.watermark,
        approval=args.approval, sign=args.sign, sign_key=args.sign_key))

def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog="quietpatch-report")
    sub = parser.add_subparsers(dest="cmd", required=True)
    # Resolve template dir inside package (adjust if you install data_files)
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    add_report_subparser(sub, template_dir)
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
