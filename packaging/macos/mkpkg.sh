#!/usr/bin/env bash
set -euo pipefail
APP_ID="com.quietpatch.agent"
VERSION="${1:-0.2.1}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ensure payload present
if [ ! -f "$ROOT/payload/usr/local/quietpatch/quietpatch" ]; then
  echo "Missing payload quietpatch in payload/usr/local/quietpatch/" >&2
  exit 1
fi

# permissions Apple expects
sudo chown -R root:wheel "$ROOT/payload/Library/LaunchDaemons"
sudo chmod 644 "$ROOT/payload/Library/LaunchDaemons/"*.plist
sudo chmod 755 "$ROOT/payload/usr/local/quietpatch/quietpatch" || true

pkgbuild \
  --root "$ROOT/payload" \
  --identifier "$APP_ID" \
  --version "$VERSION" \
  --scripts "$ROOT/scripts" \
  --install-location / \
  "quietpatch-${VERSION}.pkg"

echo "Built quietpatch-${VERSION}.pkg"

