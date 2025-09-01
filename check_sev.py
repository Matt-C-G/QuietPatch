import json

data = json.load(open("data/vuln_log.json"))
print("Severity distribution:")
sev_counts = {}

for app in data:
    sev = str(app.get("severity", "unknown"))
    sev_counts[sev] = sev_counts.get(sev, 0) + 1

for sev, count in sorted(sev_counts.items()):
    print(f"  {sev}: {count}")

print(f"\nTotal apps: {len(data)}")
