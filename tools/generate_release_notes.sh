#!/usr/bin/env bash
set -euo pipefail

NEW_TAG="${1:?usage: $0 vX.Y.Z}"
REPO_URL="${2:-https://github.com/${GITHUB_REPOSITORY:-Matt-C-G/QuietPatch}}"

# previous tag
if PREV_TAG=$(git describe --tags --abbrev=0 --match "v*.*.*" --exclude="$NEW_TAG" 2>/dev/null); then
  RANGE="${PREV_TAG}..${NEW_TAG}"
else
  PREV_TAG="$(git rev-list --max-parents=0 HEAD | tail -n1)"
  RANGE="${PREV_TAG}..${NEW_TAG}"
fi

COMMITS_RAW=$(git log --no-merges --pretty=format:%s "${RANGE}" || true)

# Filter out noisy commit subjects
COMMITS_RAW="$(printf '%s\n' "$COMMITS_RAW" | \
  grep -Ev '^(merge branch|bump version|chore\(release\):|release:|version:)' || true)"

# Fail if no meaningful changes
if [ -z "$COMMITS_RAW" ]; then
  echo "Error: No meaningful changes found since ${PREV_TAG}" >&2
  echo "This usually means the tag range is empty or all commits were filtered out." >&2
  exit 1
fi

# buckets
declare -a feat fix build ci docs refactor perf test chore other
feat=(); fix=(); build=(); ci=(); docs=(); refactor=(); perf=(); test=(); chore=(); other=()

while IFS= read -r line; do
  msg="$line"
  lc="$(printf '%s' "$msg" | tr '[:upper:]' '[:lower:]')"
  case "$lc" in
    feat:*|feature:*)        feat+=("$msg") ;;
    fix:*|bugfix:*|hotfix:*) fix+=("$msg") ;;
    build:*|packag*|release:*) build+=("$msg") ;;
    ci:*|workflow:*|github:*)  ci+=("$msg") ;;
    docs:*|readme:*|doc:*)   docs+=("$msg") ;;
    refactor:*)              refactor+=("$msg") ;;
    perf:*|performance:*)    perf+=("$msg") ;;
    test:*|tests:*|pytest:*) test+=("$msg") ;;
    chore:*|tidy:*|style:*|lint:*) chore+=("$msg") ;;
    *)                       other+=("$msg") ;;
  esac
done <<< "${COMMITS_RAW}"

render_section () {
  title="$1"; shift
  arr=("$@")
  if [ "${#arr[@]}" -gt 0 ]; then
    echo "### ${title}"
    for m in "${arr[@]}"; do
      echo "- ${m}"
    done
    echo
  fi
}

# Compare link
if [[ "$PREV_TAG" =~ ^v ]]; then
  COMP_LINK="${REPO_URL}/compare/${PREV_TAG}...${NEW_TAG}"
else
  COMP_LINK="${REPO_URL}/commits/${NEW_TAG}"
fi

# Generate dynamic highlights from Features and Fixes (max 5)
HIGHLIGHTS=()
for item in "${feat[@]}" "${fix[@]}"; do
  if [ ${#HIGHLIGHTS[@]} -lt 5 ]; then
    # Clean up the commit message for highlights
    clean_item=$(echo "$item" | sed 's/^[^:]*: *//' | sed 's/^[a-z]*: *//')
    HIGHLIGHTS+=("$clean_item")
  fi
done

cat > NOTES.md <<EOF
# QuietPatch ${NEW_TAG}

Cross-platform, offline-first vulnerability scanner with deterministic HTML reports and per-app remediation.

## ✨ Highlights
EOF

# Add dynamic highlights
for highlight in "${HIGHLIGHTS[@]}"; do
  echo "- ${highlight}" >> NOTES.md
done

# Add static highlights if we have room
if [ ${#HIGHLIGHTS[@]} -lt 3 ]; then
  cat >> NOTES.md <<'EOF'
- Cross-platform single-file runners (Windows, Linux, macOS)
- Wheel-first PEX builds; reproducible artifacts
- Offline DB snapshot (`db-latest.tar.*`); no network required
EOF
fi

cat >> NOTES.md <<'EOF'

## 🔄 Changes since ${PREV_TAG}
(Compare: ${COMP_LINK})

EOF

# Render sections only if they have content
if [ ${#feat[@]} -gt 0 ]; then render_section "Features" "${feat[@]}" >> NOTES.md; fi
if [ ${#fix[@]} -gt 0 ]; then render_section "Fixes" "${fix[@]}" >> NOTES.md; fi
if [ ${#build[@]} -gt 0 ]; then render_section "Build / Packaging" "${build[@]}" >> NOTES.md; fi
if [ ${#ci[@]} -gt 0 ]; then render_section "CI" "${ci[@]}" >> NOTES.md; fi
if [ ${#docs[@]} -gt 0 ]; then render_section "Docs" "${docs[@]}" >> NOTES.md; fi
if [ ${#refactor[@]} -gt 0 ]; then render_section "Refactors" "${refactor[@]}" >> NOTES.md; fi
if [ ${#perf[@]} -gt 0 ]; then render_section "Performance" "${perf[@]}" >> NOTES.md; fi
if [ ${#test[@]} -gt 0 ]; then render_section "Tests" "${test[@]}" >> NOTES.md; fi
if [ ${#chore[@]} -gt 0 ]; then render_section "Chore / Misc" "${chore[@]}" >> NOTES.md; fi
if [ ${#other[@]} -gt 0 ]; then render_section "Other" "${other[@]}" >> NOTES.md; fi

cat >> NOTES.md <<'EOF'
## 📦 Assets
- Windows: `quietpatch-windows-x64.zip`
- Linux x86_64: `quietpatch-linux-x86_64.zip`
- macOS arm64: `quietpatch-macos-arm64.zip`
- Offline DB: `db-latest.tar.*`
- Verification: `SHA256SUMS`

## ⚡ Quickstart
See the README. Example (Linux):
```bash
curl -LO https://github.com/Matt-C-G/QuietPatch/releases/latest/download/quietpatch-linux-x86_64.zip
unzip quietpatch-linux-x86_64.zip
./run_quietpatch.sh scan --db db-latest.tar.zst --also-report --open
```

## 🔒 Security & Privacy

Read-only; remediation commands are suggestions. Deterministic reports; SBOM + third-party notices included.

## 🙏 Acknowledgments

NVD • CISA KEV • FIRST EPSS
EOF

echo "Generated NOTES.md for ${NEW_TAG}"