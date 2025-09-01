# report/html.py — enhanced HTML report with safety features, filters, and details
from __future__ import annotations

import html
import json
from pathlib import Path

# Decryptor import (v3 first, fallback to v2 if present)
try:
    from src.config.encryptor_v3 import decrypt_file  # type: ignore
except Exception:  # pragma: no cover
    from src.config.encryptor_v2 import decrypt_file  # type: ignore


def _load_items(input_path: str):
    """Return list[dict] records from plaintext JSON or encrypted .enc."""
    p = Path(input_path)
    raw = p.read_bytes()
    # plaintext JSON starts with '{' or '['; otherwise try decrypt
    if raw[:1] not in (b"{", b"["):
        raw = decrypt_file(str(p))
    try:
        obj = json.loads(raw.decode("utf-8", "ignore"))
    except Exception:
        # if the decryptor already returned bytes of JSON, attempt direct load
        obj = json.loads(raw)

    # Normalize to list of app records
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        if "apps" in obj and isinstance(obj["apps"], list):
            return obj["apps"]
        return [obj]
    return []


def _first_action(rec: dict) -> str:
    """Pull a short human-readable action from rec['actions']."""
    acts = rec.get("actions") or []
    if not acts:
        return ""
    a = acts[0]
    if isinstance(a, dict):
        text = a.get("cmd") or a.get("url") or a.get("note") or ""
    else:
        text = str(a)
    text = text.strip()
    return (text[:120] + "…") if len(text) > 120 else text


def _first_cve(rec: dict) -> tuple[str, str, str, str]:
    """(cve_id, cvss, sev, summary) — empty strings if none."""
    # Support both old 'cves' and new 'vulnerabilities' structure
    vulns = rec.get("vulnerabilities") or rec.get("cves") or []
    if not vulns:
        return ("", "", "", "")
    c = vulns[0]
    # Support both old 'id' and new 'cve_id' structure
    cve = c.get("cve_id") or c.get("id") or ""
    cvss = str(c.get("cvss") or "")
    sev = str(c.get("severity") or "")
    summary = c.get("summary") or ""
    return (cve, cvss, sev, summary)


def _sev_badge(sev: str) -> str:
    s = (sev or "").lower()
    cls = {
        "critical": "badge-crit",
        "high": "badge-high",
        "medium": "badge-med",
        "low": "badge-low",
        "none": "badge-none",
        "unknown": "badge-unk",
    }.get(s, "badge-unk")
    label = sev.capitalize() if sev else "Unknown"
    return f'<span class="badge {cls}">{html.escape(label)}</span>'


def _action_cell(rec: dict) -> str:
    """Generate action cell with copy button and safety warning."""
    acts = rec.get("actions") or []
    if not acts:
        return '<td class="action-cell">—</td>'

    a = acts[0]
    if isinstance(a, dict):
        cmd = a.get("cmd") or ""
        url = a.get("url") or ""
        note = a.get("note") or ""

        if cmd:
            # Command with copy button
            return f"""<td class="action-cell">
                <div class="action-content">
                    <code class="command">{html.escape(cmd)}</code>
                    <button class="copy-btn" onclick="copyToClipboard(this, '{html.escape(cmd)}')" title="Copy command">
                        📋
                    </button>
                </div>
                {f'<div class="action-note">{html.escape(note)}</div>' if note else ""}
            </td>"""
        elif url:
            # URL with copy button
            return f'''<td class="action-cell">
                <div class="action-content">
                    <a href="{html.escape(url)}" target="_blank" class="action-url">{html.escape(url)}</a>
                    <button class="copy-btn" onclick="copyToClipboard(this, '{html.escape(url)}')" title="Copy URL">
                        📋
                    </button>
                </div>
                {f'<div class="action-note">{html.escape(note)}</div>' if note else ""}
            </td>'''
        else:
            # Note only
            return (
                f'<td class="action-cell"><div class="action-note">{html.escape(note)}</div></td>'
            )

    # Fallback for string actions
    text = str(a)
    return f"""<td class="action-cell">
        <div class="action-content">
            <span>{html.escape(text)}</span>
            <button class="copy-btn" onclick="copyToClipboard(this, '{html.escape(text)}')" title="Copy text">
                📋
            </button>
        </div>
    </td>"""


def _generate_cve_details(rec: dict, row_id: str) -> str:
    """Generate detailed CVE information for the drawer."""
    # Support both old 'cves' and new 'vulnerabilities' structure
    vulns = rec.get("vulnerabilities") or rec.get("cves") or []
    if not vulns:
        return '<div class="cve-details">No CVEs found</div>'

    details = []
    for i, vuln in enumerate(vulns):
        # Support both old 'id' and new 'cve_id' structure
        cve_id = vuln.get("cve_id") or vuln.get("id", "")
        cvss = vuln.get("cvss", "")
        severity = vuln.get("severity", "unknown")
        # Support both old 'kev' and new 'is_kev' structure
        kev = "✓" if vuln.get("is_kev") or vuln.get("kev") else ""
        epss = vuln.get("epss_score") or vuln.get("epss", "")
        summary = vuln.get("summary", "")

        details.append(f"""
            <div class="cve-item">
                <div class="cve-header">
                    <span class="cve-id">{html.escape(cve_id)}</span>
                    <span class="cve-meta">
                        {f'<span class="cvss">CVSS: {html.escape(str(cvss))}</span>' if cvss else ""}
                        {_sev_badge(severity)}
                        {'<span class="kev-badge">KEV</span>' if kev else ""}
                        {f'<span class="epss">EPSS: {html.escape(str(epss))}</span>' if epss else ""}
                    </span>
                </div>
                {f'<div class="cve-summary">{html.escape(summary)}</div>' if summary else ""}
            </div>
        """)

    return f"""
        <div class="cve-details" id="cve-details-{row_id}">
            <h4>All CVEs ({len(vulns)})</h4>
            {"".join(details)}
        </div>
    """


def generate_report(input_path: str, output_path: str) -> str:
    items = _load_items(input_path)

    # Build table rows (one row per app, show first CVE + action preview)
    rows = []
    for i, rec in enumerate(items):
        app = rec.get("app") or rec.get("name") or ""
        ver = rec.get("version") or ""
        cve, cvss, sev, summary = _first_cve(rec)
        # Support both old 'cves' and new 'vulnerabilities' structure
        vulns = rec.get("vulnerabilities") or rec.get("cves") or []
        kev = "✓" if any((v or {}).get("is_kev") or (v or {}).get("kev") for v in vulns) else ""
        epss = ""
        for v in vulns:
            epss_val = v.get("epss_score") or v.get("epss")
            if epss_val:
                epss = str(epss_val)
                break

        row_id = f"row-{i}"
        has_cves = bool(vulns)

        cells = [
            f'<td class="app-cell">{html.escape(str(app))}</td>',
            f'<td class="version-cell">{html.escape(str(ver))}</td>',
            _action_cell(rec),  # <-- Action column with copy buttons
            f'<td class="cve-cell">{html.escape(str(cve or "—"))}</td>',
            f'<td class="cvss-cell">{html.escape(str(cvss or "—"))}</td>',
            f'<td class="severity-cell">{_sev_badge(sev or (rec.get("severity_label") or ""))}</td>',
            f'<td class="kev-cell">{html.escape(kev or "—")}</td>',
            f'<td class="epss-cell">{html.escape(epss or "—")}</td>',
            f'<td class="summary-cell">{html.escape(summary or "")}</td>',
        ]

        # Add expand/collapse button if there are CVEs
        if has_cves:
            cells.append(f"""
                <td class="expand-cell">
                    <button class="expand-btn" onclick="toggleDetails('{row_id}')" title="Show all CVEs">
                        📋
                    </button>
                </td>
            """)
        else:
            cells.append('<td class="expand-cell">—</td>')

        cells_html = "".join(cells)
        row_html = (
            f'<tr id="{row_id}" class="data-row" '
            f'data-severity="{sev or "unknown"}" '
            f'data-kev="{str(bool(kev)).lower()}">{cells_html}</tr>'
        )
        rows.append(row_html)

        # Add details row
        if has_cves:
            rows.append(f"""
                <tr class="details-row" id="details-{row_id}" style="display: none;">
                    <td colspan="10" class="details-cell">
                        {_generate_cve_details(rec, row_id)}
                    </td>
                </tr>
            """)

    html_out = f"""\
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>QuietPatch – Vulnerability Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            margin: 24px;
            line-height: 1.5;
        }}
        h1 {{ margin-bottom: 12px; }}
        
        .safety-banner {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            color: #92400e;
        }}
        .safety-banner strong {{
            color: #78350f;
        }}
        
        .toolbar {{
            display: flex;
            gap: 12px;
            align-items: center;
            margin: 12px 0 18px;
            flex-wrap: wrap;
        }}
        input[type="search"] {{
            padding: 6px 10px;
            min-width: 320px;
        }}
        
        .filter-pills {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .filter-pill {{
            padding: 6px 12px;
            border: 1px solid #d1d5db;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .filter-pill:hover {{
            background: #f3f4f6;
        }}
        .filter-pill.active {{
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 16px;
        }}
        th, td {{
            border-bottom: 1px solid #eee;
            padding: 8px 10px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            position: sticky;
            top: 0;
            background: #fafafa;
            font-weight: 600;
        }}
        
        .action-cell {{
            max-width: 300px;
        }}
        .action-content {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }}
        .command {{
            background: #f3f4f6;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 12px;
            flex: 1;
            word-break: break-all;
        }}
        .action-url {{
            color: #2563eb;
            text-decoration: none;
            flex: 1;
            word-break: break-all;
        }}
        .action-url:hover {{
            text-decoration: underline;
        }}
        .action-note {{
            font-size: 12px;
            color: #6b7280;
            font-style: italic;
        }}
        .copy-btn {{
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 12px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .copy-btn:hover {{
            background: #2563eb;
        }}
        .copy-btn:active {{
            background: #1d4ed8;
        }}
        
        .expand-btn {{
            background: #10b981;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 12px;
        }}
        .expand-btn:hover {{
            background: #059669;
        }}
        
        .details-row {{
            background: #f9fafb;
        }}
        .details-cell {{
            padding: 16px !important;
        }}
        .cve-details h4 {{
            margin: 0 0 12px 0;
            color: #374151;
        }}
        .cve-item {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
        }}
        .cve-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .cve-id {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-weight: 600;
            color: #1f2937;
        }}
        .cve-meta {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .cvss, .epss {{
            font-size: 12px;
            color: #6b7280;
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .kev-badge {{
            background: #dc2626;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .cve-summary {{
            color: #4b5563;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .badge {{
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 500;
        }}
        .badge-crit {{ background:#7f1d1d; color:#fff; }}
        .badge-high {{ background:#b91c1c; color:#fff; }}
        .badge-med {{ background:#f59e0b; color:#111; }}
        .badge-low {{ background:#10b981; color:#111; }}
        .badge-none {{ background:#e5e7eb; color:#111; }}
        .badge-unk {{ background:#e2e8f0; color:#111; }}
        
        .muted {{ color:#6b7280; }}
        
        .copy-success {{
            background: #10b981 !important;
        }}
        
        .hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <h1>QuietPatch – Vulnerability Report</h1>
    
    <div class="safety-banner">
        <strong>⚠️ Safety Notice:</strong> Commands are suggestions. Review before running. 
        Never execute commands without understanding what they do.
    </div>
    
    <div class="toolbar">
        <input id="q" type="search" placeholder="Search app or CVE or summary">
        <div class="filter-pills">
            <button class="filter-pill active" data-filter="all">All</button>
            <button class="filter-pill" data-filter="low">Low</button>
            <button class="filter-pill" data-filter="medium">Medium</button>
            <button class="filter-pill" data-filter="high">High</button>
            <button class="filter-pill" data-filter="critical">Critical</button>
            <button class="filter-pill" data-filter="kev">KEV</button>
        </div>
    </div>
    
    <table id="tbl">
        <thead>
            <tr>
                <th>App</th>
                <th>Version</th>
                <th>Action</th>
                <th>CVE</th>
                <th>CVSS</th>
                <th>Severity</th>
                <th>KEV</th>
                <th>EPSS</th>
                <th>Summary</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows) if rows else '<tr><td colspan="10" class="muted">No data</td></tr>'}
        </tbody>
    </table>

<script>
    const q = document.getElementById('q');
    const filterPills = document.querySelectorAll('.filter-pill');
    const tbody = document.querySelector('#tbl tbody');
    
    let currentFilter = 'all';
    
    function matches(txt, needle) {{
        return txt.toLowerCase().indexOf(needle) !== -1;
    }}
    
    function matchesFilter(row, filter) {{
        if (filter === 'all') return true;
        
        const severity = row.dataset.severity;
        const hasKev = row.dataset.kev === 'true';
        
        if (filter === 'kev') return hasKev;
        return severity === filter;
    }}
    
    function refilter() {{
        const needle = q.value.trim().toLowerCase();
        
        for (const row of tbody.querySelectorAll('.data-row')) {{
            const hay = (row.querySelector('.app-cell').innerText + " " + 
                        row.querySelector('.action-cell').innerText + " " + 
                        row.querySelector('.cve-cell').innerText + " " + 
                        row.querySelector('.summary-cell').innerText).toLowerCase();
            
            const matchesSearch = !needle || matches(hay, needle);
            const matchesFilterType = matchesFilter(row, currentFilter);
            
            const show = matchesSearch && matchesFilterType;
            row.style.display = show ? "" : "none";
            
            // Hide details row if main row is hidden
            const detailsRow = document.getElementById(`details-${{row.id}}`);
            if (detailsRow) {{
                detailsRow.style.display = show ? "none" : "none";
            }}
        }}
    }}
    
    function toggleDetails(rowId) {{
        const detailsRow = document.getElementById(`details-${{rowId}}`);
        const expandBtn = document.querySelector(`#${{rowId}} .expand-btn`);
        
        if (detailsRow.style.display === 'none') {{
            detailsRow.style.display = '';
            expandBtn.textContent = '📋';
            expandBtn.title = 'Hide CVEs';
        }} else {{
            detailsRow.style.display = 'none';
            expandBtn.textContent = '📋';
            expandBtn.title = 'Show all CVEs';
        }}
    }}
    
    function setActiveFilter(filter) {{
        currentFilter = filter;
        
        // Update pill states
        filterPills.forEach(pill => {{
            pill.classList.toggle('active', pill.dataset.filter === filter);
        }});
        
        refilter();
    }}
    
    function copyToClipboard(button, text) {{
        navigator.clipboard.writeText(text).then(() => {{
            // Visual feedback
            const originalText = button.textContent;
            button.textContent = "✓";
            button.classList.add('copy-success');
            
            setTimeout(() => {{
                button.textContent = originalText;
                button.classList.remove('copy-success');
            }}, 1500);
        }}).catch(err => {{
            console.error('Failed to copy: ', err);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            // Visual feedback
            const originalText = button.textContent;
            button.textContent = "✓";
            button.classList.add('copy-success');
            
            setTimeout(() => {{
                button.textContent = originalText;
                button.classList.remove('copy-success');
            }}, 1500);
        }});
    }}
    
    // Event listeners
    q.addEventListener('input', refilter);
    
    filterPills.forEach(pill => {{
        pill.addEventListener('click', () => {{
            setActiveFilter(pill.dataset.filter);
        }});
    }});
</script>
</body>
</html>
"""

    out = Path(output_path)
    out.write_text(html_out, encoding="utf-8")
    return str(out)
