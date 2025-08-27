import json, re, sys
from pathlib import Path
db = json.load(open("data/db/cpe_to_cves.json"))
apps = json.load(open("data/apps.json"))
prods_by_vendor = {}
for k in db.keys():
    parts = k.split(":")
    if len(parts) >= 5:
        prods_by_vendor.setdefault(parts[3], set()).add(parts[4])

def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

miss = [a for a in apps if not a.get("cpe")]
for a in miss:
    name = a["app"]
    n = norm(name)
    cands = []
    for v, prods in prods_by_vendor.items():
        for p in prods:
            score = 0
            if n in p:
                score += 3
            if p in n:
                score += 2
            if n.split("_")[:1] == [p.split("_")[0]]:
                score += 1
            if score >= 3:
                cands.append((score, v, p))
    cands.sort(reverse=True)
    if cands[:3]:
        print(f"{name}:")
        for s,v,p in cands[:3]:
            print(f"  vendor: {v}, product: {p}")
