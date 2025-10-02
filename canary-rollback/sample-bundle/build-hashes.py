from pathlib import Path
import hashlib, json

root = Path(__file__).parent
manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))

for t in manifest.get("targets", []):
    p = root / t["artifact"]
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    t["sha256"] = h

(root/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("Updated manifest SHA256s.")
