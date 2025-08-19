# Sample Reports
Generate from your machine (redact host/user if you publish screenshots).
1) Scan (hardware-first encryption):
   python3 quietpatch.pyz scan -o data --age-recipient <AGE_PUBKEY>
2) Report:
   python3 quietpatch.pyz report -i data/vuln_log.json.enc -o report.html
3) Export:
   - Save report.html here as Ops.html
   - Produce a one-page Board.pdf with roll-up + hash/footer.
