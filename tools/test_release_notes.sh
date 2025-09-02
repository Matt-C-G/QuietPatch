#!/usr/bin/env bash
set -euo pipefail

# Unit test for release notes generator
# Tests edge cases like missing previous tags, empty ranges, etc.

echo "🧪 Testing release notes generator..."

# Create a temporary test repository
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# Initialize git repo
git init
git config user.name "Test User"
git config user.email "test@example.com"

# Create initial commit
echo "# Test Project" > README.md
git add README.md
git commit -m "feat: initial commit"

# Test 1: Generate notes for first tag (no previous tag)
echo "Test 1: First tag (no previous tag)"
bash "$OLDPWD/tools/generate_release_notes.sh" "v0.0.1" "https://github.com/test/repo"
if [ -f NOTES.md ]; then
    echo "✅ First tag test passed"
    grep -q "v0.0.1" NOTES.md || (echo "❌ Tag not found in notes" && exit 1)
else
    echo "❌ NOTES.md not generated"
    exit 1
fi

# Test 2: Add more commits and test filtering
echo "Test 2: Commit filtering"
git commit --allow-empty -m "feat: add new feature"
git commit --allow-empty -m "fix: resolve bug"
git commit --allow-empty -m "chore(release): bump version"
git commit --allow-empty -m "merge branch 'feature'"
git commit --allow-empty -m "bump version to 1.0.0"

bash "$OLDPWD/tools/generate_release_notes.sh" "v0.0.2" "https://github.com/test/repo"
if [ -f NOTES.md ]; then
    echo "✅ Filtering test passed"
    # Should not contain filtered commits
    if grep -q "chore(release)" NOTES.md || grep -q "merge branch" NOTES.md || grep -q "bump version" NOTES.md; then
        echo "❌ Filtered commits found in notes"
        exit 1
    fi
    # Should contain meaningful commits
    grep -q "feat:" NOTES.md || (echo "❌ Features not found" && exit 1)
    grep -q "fix:" NOTES.md || (echo "❌ Fixes not found" && exit 1)
else
    echo "❌ NOTES.md not generated"
    exit 1
fi

# Test 3: Empty range (should fail)
echo "Test 3: Empty range (should fail)"
if bash "$OLDPWD/tools/generate_release_notes.sh" "v0.0.1" "https://github.com/test/repo" 2>/dev/null; then
    echo "❌ Empty range should have failed"
    exit 1
else
    echo "✅ Empty range correctly failed"
fi

# Test 4: BREAKING CHANGE detection
echo "Test 4: BREAKING CHANGE detection"
git commit --allow-empty -m "feat: major change

BREAKING CHANGE: This is a breaking change"

# This should work (major version)
bash "$OLDPWD/tools/generate_release_notes.sh" "v1.0.0" "https://github.com/test/repo"
echo "✅ BREAKING CHANGE with major version passed"

# Cleanup
cd "$OLDPWD"
rm -rf "$TEST_DIR"

echo "🎉 All release notes tests passed!"
