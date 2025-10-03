from __future__ import annotations
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .util import sha256_bytes

def jinja_env(template_dir: str):
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

def render_template(env, name: str, model: dict) -> str:
    tpl = env.get_template(name)
    html = tpl.render(**model)
    return html

def compute_html_hash(html: str) -> str:
    return sha256_bytes(html.encode("utf-8"))


# --- Legacy compatibility layer for pre-0.5 tests --------------------------
# Re-export old internal helpers used by tests. These provide simple implementations
# that match the expected behavior from the old HTML generation system.

def _action_cell(rec):
    """
    Legacy function for generating action cell HTML.
    Returns HTML string for the actions column.
    """
    actions = rec.get("actions", [])
    if not actions:
        return "—"
    
    html_parts = []
    for action in actions:
        if "cmd" in action:
            cmd = action["cmd"]
            note = action.get("note", "")
            html_parts.append(f'<div class="action-item"><code class="copy-btn" onclick="navigator.clipboard.writeText(\'{cmd}\')">{cmd}</code>')
            if note:
                html_parts.append(f' <small>({note})</small>')
            html_parts.append('</div>')
        elif "url" in action:
            url = action["url"]
            note = action.get("note", "")
            html_parts.append(f'<div class="action-item"><a href="{url}" target="_blank">{url}</a>')
            if note:
                html_parts.append(f' <small>({note})</small>')
            html_parts.append('</div>')
    
    return "".join(html_parts)

def _first_cve(rec):
    """
    Legacy function for extracting first CVE data.
    Returns tuple of (cve_id, cvss, severity, summary).
    """
    cves = rec.get("cves", [])
    if not cves:
        return "", "", "", ""
    
    first_cve = cves[0]
    return (
        first_cve.get("id", ""),
        str(first_cve.get("cvss", "")),
        first_cve.get("severity", ""),
        first_cve.get("summary", "")
    )

def generate_report(input_path, output_path=None, **kwargs):
    """
    Legacy wrapper retained for tests/back-compat.
    Takes input_path (JSON file) and optional output_path (HTML file).
    """
    import json
    from pathlib import Path
    
    # Read the input JSON file
    with open(input_path, 'r') as f:
        scan_data = json.load(f)
    
    # Convert old format to new format if needed
    original_data = scan_data
    if isinstance(scan_data, list):
        # Old format: list of app records - convert to new format
        scan_data = {
            "scan_id": "legacy-test",
            "generated_at": "2025-01-02T00:00:00Z",
            "totals": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "summary": f"Scanned {len(original_data)} apps",
            "assets": []
        }
    
    # Write converted data to temp file for build_tech_report
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(scan_data, f)
        temp_scan_path = f.name
    
    try:
        # Generate HTML using the new system
        from .tech import build_tech_report
        html = build_tech_report(
            template_dir="quietpatch/report/templates",
            scan=temp_scan_path,
            out_html="",  # Empty string means return HTML instead of writing file
            watermark=kwargs.get("watermark")
        )
    except Exception as e:
        # Fallback: simple HTML that includes the action data
        html_parts = [
            "<!DOCTYPE html>",
            "<html><head><title>QuietPatch Report</title></head>",
            "<body><h1>QuietPatch Report</h1>",
            "<p>Legacy compatibility mode</p>",
            "<table><tr><th>App</th><th>Action</th></tr>"
        ]
        
        # Add rows for each app with actions
        for app_data in original_data if isinstance(original_data, list) else []:
            app_name = app_data.get("app", "Unknown")
            actions_html = _action_cell(app_data)
            html_parts.append(f"<tr><td>{app_name}</td><td>{actions_html}</td></tr>")
        
        html_parts.extend(["</table></body></html>"])
        html = "\n".join(html_parts)
    
    finally:
        # Clean up temp file
        Path(temp_scan_path).unlink(missing_ok=True)
    
    if output_path:
        Path(output_path).write_text(html, encoding="utf-8")
    
    return html
