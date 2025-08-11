# QuietPatch – CVE Vulnerability Tracker (fixed-up runnable scaffold)

## What I added
- **Complete, runnable modules** alongside your originals:
  - `src/config/encryptor_new.py` – key mgmt at `~/.quietpatch/key.key`, AES-128 (Fernet) file encryption.
  - `src/core/scanner_new.py` – cross‑platform app inventory (macOS, Windows, Linux).
  - `src/core/cve_mapper_new.py` – NVD 2.0 API mapping with optional `NVD_API_KEY`.
  - `qp_cli.py` – one-command CLI to scan, map, and encrypt outputs.
- Keeps your original files intact.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional (higher NVD rate limits):
```bash
export NVD_API_KEY=your_key_here    # PowerShell: $env:NVD_API_KEY="..."
```

## Usage
```bash
# From repo root:
python qp_cli.py scan -o data
# Decrypt and view:
python qp_cli.py show data/vuln_log.json.enc --pretty
```

## Outputs
- `data/apps.json.enc` – encrypted software inventory
- `data/vuln_log.json.enc` – encrypted CVE mapping
- Keys live at `~/.quietpatch/key.key` (override via `QUIETPATCH_KEY_PATH`).

## Notes
- Windows inventory uses registry; Linux supports dpkg/rpm. macOS uses `mdls` on `.app` bundles.
- Mapping is heuristic; tune `_normalize()` or add allow/deny lists to reduce false positives.
- For CI, pin dependencies and add `pytest` around scanner normalization + mapper parsing.
