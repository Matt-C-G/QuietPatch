from __future__ import annotations
import shutil, subprocess, tempfile, os

def html_to_pdf(html: str, out_path: str):
    """
    Offline HTML->PDF using wkhtmltopdf if present; fallback-less (deterministic).
    Ship docs recommending users install wkhtmltopdf or patch to WeasyPrint.
    """
    wk = shutil.which("wkhtmltopdf")
    if not wk:
        raise RuntimeError("wkhtmltopdf not found on PATH. Install it or skip PDF.")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        f.write(html.encode("utf-8"))
        f.flush()
        cmd = [wk, "--quiet", f.name, out_path]
        subprocess.run(cmd, check=True)
    os.unlink(f.name)
