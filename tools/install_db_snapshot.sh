#!/usr/bin/env bash
# Unpack any dist/db-*.tar.{zst,gz} into /var/lib/quietpatch/db if empty
set -euo pipefail
DB="/var/lib/quietpatch/db"
mkdir -p "$DB"
if [ -z "$(ls -A "$DB" 2>/dev/null)" ]; then
  SNAP=$(ls dist/db-*.tar.* 2>/dev/null | head -n1 || true)
  if [ -n "$SNAP" ]; then
    echo "[db] installing $SNAP -> $DB"
    case "$SNAP" in
      *.zst) tar --use-compress-program zstd -xf "$SNAP" -C "$DB" || exit 1 ;;
      *.gz)  tar -xzf "$SNAP" -C "$DB" || exit 1 ;;
      *)     echo "Unknown compression for $SNAP"; exit 1 ;;
    esac
  else
    echo "[db] no snapshot found in dist/; skipping"
  fi
fi


