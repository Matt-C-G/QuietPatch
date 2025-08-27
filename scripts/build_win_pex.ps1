# scripts/build_win_pex.ps1
# Runs on Windows, builds a Windows-targeted PEX for Python 3.11

$ErrorActionPreference = "Stop"

# 1) Fresh venv (optional but clean)
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip wheel setuptools pex

# 2) Install your package (editable or build first if you prefer)
.\.venv\Scripts\python -m pip install -e .

# 3) Build PEX (console script "quietpatch")
mkdir dist 2>$null
.\.venv\Scripts\python -m pex `
	quietpatch `
	-c quietpatch `
	-o dist/quietpatch-win-py311.pex `
	--validate-entry-point `
	--no-build `
	--venv prepend `
	--strip-pex-env

Write-Host "Built dist/quietpatch-win-py311.pex"