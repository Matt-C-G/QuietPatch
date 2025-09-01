#!/usr/bin/env bash
set -euo pipefail

install -d -m 0755 /usr/local/quietpatch
install -d -m 0755 /var/lib/quietpatch/logs
install -d -m 0755 /var/lib/quietpatch/db

# Lay down binaries/config if not already present
[ -f /usr/local/quietpatch/quietpatch.pex ] || install -m 0755 dist/quietpatch.pex /usr/local/quietpatch/quietpatch.pex
[ -f /etc/quietpatch/policy.yml ] || install -Dm 0644 config/policy.yml /etc/quietpatch/policy.yml

# Optional: unpack DB snapshot if provided alongside package
if compgen -G "dist/db-*.tar.zst" >/dev/null; then
  echo "[postinst] Installing DB snapshot into /var/lib/quietpatch/db …"
  tar --use-compress-program zstd -xf dist/db-*.tar.zst -C /var/lib/quietpatch/db || \
  tar -xzf dist/db-*.tar.gz -C /var/lib/quietpatch/db
fi

install -Dm 0644 packaging/linux/quietpatch.service /etc/systemd/system/quietpatch.service
install -Dm 0644 packaging/linux/quietpatch.timer /etc/systemd/system/quietpatch.timer

systemctl daemon-reload
systemctl enable --now quietpatch.timer || true
echo "[postinst] QuietPatch installed. First run will occur at next timer tick (03:00) or:"
echo "  sudo systemctl start quietpatch.service"


