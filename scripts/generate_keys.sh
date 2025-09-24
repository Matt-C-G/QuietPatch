#!/bin/bash
# Generate minisign key pair for signing releases

set -e

echo "Generating minisign key pair for QuietPatch releases..."

# Check if minisign is installed
if ! command -v minisign &> /dev/null; then
    echo "Error: minisign not found. Please install it first:"
    echo "  macOS: brew install minisign"
    echo "  Ubuntu: sudo apt install minisign"
    echo "  Windows: choco install minisign"
    exit 1
fi

# Create keys directory
mkdir -p keys

# Generate key pair
echo "Generating key pair..."
minisign -G -p keys/quietpatch.pub -s keys/quietpatch.key

# Convert private key to base64 for GitHub secrets
echo "Converting private key to base64 for GitHub secrets..."
if command -v base64 &> /dev/null; then
    base64 -w0 keys/quietpatch.key > keys/quietpatch.key.b64
else
    # Fallback for systems without base64 -w0
    base64 keys/quietpatch.key | tr -d '\n' > keys/quietpatch.key.b64
fi

echo ""
echo "✓ Key pair generated successfully!"
echo ""
echo "Files created:"
echo "  Private key: keys/quietpatch.key"
echo "  Public key:  keys/quietpatch.pub"
echo "  Base64 key:  keys/quietpatch.key.b64"
echo ""
echo "Next steps:"
echo "1. Add the base64 key to GitHub secrets as MINISIGN_SECRET_KEY_B64"
echo "2. Update VERIFY.md with the public key content"
echo "3. Keep the private key secure and never commit it to git"
echo ""
echo "Public key content (copy to VERIFY.md):"
echo "----------------------------------------"
cat keys/quietpatch.pub
echo "----------------------------------------"
echo ""
echo "Base64 private key (copy to GitHub secrets):"
echo "----------------------------------------"
cat keys/quietpatch.key.b64
echo "----------------------------------------"
echo ""
echo "Windows PowerShell alternative:"
echo "certutil -encode keys/quietpatch.key temp.b64"
echo "# Then copy the content between the BEGIN/END lines"
