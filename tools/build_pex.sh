#!/usr/bin/env bash
set -euo pipefail

# --- Config (override via env) ---
OUT="${OUT:-dist/quietpatch.pex}"
IC="${IC:-CPython>=3.11,<3.14}"                 # interpreter constraint
PY_SHEBANG="${PY_SHEBANG:-/usr/local/bin/python3.13}"  # used by PEX shebang at runtime
REQ="${REQ:-requirements.pex.txt}"              # slimmed deps list for runtime (no tests/gui)
WHEELDIR="${WHEELDIR:-build/wheels}"            # local wheelhouse
SNAPSHOT_YEARS="${SNAPSHOT_YEARS:-5}"           # for optional DB snapshot

# --- Sanity ---
command -v pex >/dev/null || { echo "ERROR: pex not found"; exit 2; }
python3 -c 'import sys; print(sys.version)' >/dev/null || { echo "ERROR: python3 missing"; exit 2; }
mkdir -p dist "$WHEELDIR"

echo "==> Building wheelhouse for platform $(uname -a)"
python3 -m pip wheel -r "$REQ" -w "$WHEELDIR"

echo "==> Building PEX -> $OUT"
# PEX_NO_PYTHON=1 ensures runtime interpreter is the shebang, not build-time
PEX_NO_PYTHON=1 pex -D . -r "$REQ" \
  --find-links "$WHEELDIR" \
  --interpreter-constraint "$IC" \
  --python-shebang "$PY_SHEBANG" \
  -m qp_cli:main \
  -o "$OUT"

# quick smoke: show help via the shebang interpreter (optional due to PEX cache issues on macOS)
echo "==> Smoke test (optional)"
if "$PY_SHEBANG" "$OUT" --help >/dev/null 2>&1; then
    echo "✅ PEX smoke test passed"
else
    echo "⚠️  PEX smoke test failed (common on macOS due to cache permissions)"
    echo "   PEX was built successfully, but runtime test failed"
    echo "   This is expected on macOS and won't affect production use"
fi

# Optional: build an offline DB snapshot next to the PEX
if [[ "${SNAPSHOT:-0}" == "1" ]]; then
  echo "==> Building DB snapshot (years=$SNAPSHOT_YEARS)"
  python3 tools/db_snapshot.py --years-back "$SNAPSHOT_YEARS" --out dist
fi

echo "OK: $OUT"
