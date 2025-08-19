# QuietPatch vX.Y.Z
**Highlights**
- Policy engine with KEV/EPSS sort; actions per app
- Offline DB (NVD feeds, version-range aware)
- Deterministic HTML report (+hash)

**Verify**
See VERIFY.md — SHA256SUMS + minisign.

**Usage**
python3 quietpatch.pyz scan -o data --age-recipient <AGE_PUBKEY>
python3 quietpatch.pyz report -i data/vuln_log.json.enc -o report.html
