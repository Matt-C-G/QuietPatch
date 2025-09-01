# Getting Started

Scan now (manual):
/usr/local/quietpatch/run_quietpatch.sh --once

Decrypt (if you used AGE recipients):
age-plugin-se -d -i /path/to/age_identity.txt -o vuln_log.json /var/lib/quietpatch/vuln_log.json.enc

Open the report:
/var/lib/quietpatch/report.html

Policy (defaults):
min_severity: low | treat_unknown_as: low | only_with_cves: true
Edit config/policy.yml and re-run.


