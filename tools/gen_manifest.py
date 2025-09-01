import json
import pathlib
import re
import time

root = pathlib.Path("release")
files = [p for p in root.iterdir() if p.is_file()]
sha_map = {}
with open(root / "SHA256SUMS", encoding="utf-8") as f:
    for line in f:
        h, name = line.strip().split() if " " in line else (None, None)
        if h and name:
            sha_map[name] = h


def guess_platform(fname: str):
    f = fname.lower()
    if f.endswith(".pyz"):
        return ["macos", "linux", "windows"]
    if f.endswith(".cmd"):
        return ["windows"]
    if fname == "quietpatch":
        return ["macos", "linux"]
    return []


artifacts = []
for p in files:
    if p.name in ("SHA256SUMS", "SHA256SUMS.minisig", "minisign.pub"):
        continue
    artifacts.append(
        {
            "file": p.name,
            "size": p.stat().st_size,
            "sha256": sha_map.get(p.name, ""),
            "platforms": guess_platform(p.name),
        }
    )
version = "0.2.0"
try:
    s = pathlib.Path("VERSION").read_text()
    m = re.search(r"(\d+\.\d+\.\d+)", s)
    if m:
        version = m.group(1)
except Exception:
    pass
manifest = {
    "name": "QuietPatch",
    "version": version,
    "released": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "publisher_pubkey": "minisign.pub",
    "sha256sums": "SHA256SUMS",
    "sha256sums_sig": "SHA256SUMS.minisig",
    "artifacts": artifacts,
}
(pathlib.Path("release") / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("Wrote release/manifest.json")
