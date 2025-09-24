#!/usr/bin/env bash
# Complete release script for QuietPatch v0.4.0

set -euo pipefail

VERSION="0.4.0"
TAG="v$VERSION"

echo "🚀 QuietPatch $VERSION Release Script"
echo "======================================"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: There are uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$TAG$"; then
    echo "❌ Error: Tag $TAG already exists"
    exit 1
fi

echo "📋 Pre-release checklist:"
echo "1. ✅ Minisign keys generated and added to GitHub secrets"
echo "2. ✅ VERIFY.md updated with public key"
echo "3. ✅ GitHub Pages configured"
echo "4. ✅ Repository URLs updated in docs"
echo ""
read -p "Have you completed all pre-release steps? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please complete the pre-release checklist first. See RELEASE_CHECKLIST.md"
    exit 1
fi

echo "🏷️  Creating and pushing tag $TAG..."

# Add all changes
git add -A

# Commit changes
git commit -m "$TAG: download-ready release kit" || echo "No changes to commit"

# Create and push tag
git tag "$TAG"
git push origin main --tags

echo "✅ Tag $TAG created and pushed successfully!"
echo ""
echo "🔄 GitHub Actions will now:"
echo "  • Build PyInstaller binaries for all platforms"
echo "  • Create Windows installer, macOS DMG, Linux AppImage"
echo "  • Generate SHA256 checksums"
echo "  • Sign with minisign"
echo "  • Upload all artifacts to GitHub Release"
echo ""
echo "📊 Monitor the build progress:"
echo "  https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
echo ""
echo "🧪 After the build completes, run the smoke tests:"
echo "  • Download each OS artifact from the GitHub Release"
echo "  • Test installation and first run"
echo "  • Verify checksums and signatures"
echo "  • Check that landing page links work"
echo ""
echo "📖 See RELEASE_CHECKLIST.md for detailed testing instructions"
echo ""
echo "🎉 Release process initiated! Check GitHub Actions for progress."
