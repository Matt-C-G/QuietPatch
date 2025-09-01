#!/usr/bin/env bash
set -euo pipefail
systemctl disable --now quietpatch.timer || true
rm -f /etc/systemd/system/quietpatch.timer /etc/systemd/system/quietpatch.service
systemctl daemon-reload || true
echo "[prerm] QuietPatch service removed. Data remains in /var/lib/quietpatch"


