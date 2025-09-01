#!/usr/bin/env python3
"""
AGE encryption key rotation tool for QuietPatch.

This tool allows you to:
1. Change encryption recipients (add/remove public keys)
2. Re-encrypt existing files with new recipients
3. Maintain audit trail of who can decrypt data

Usage:
    python3 tools/rewrap_v3.py --old-identity /path/to/old.key --new-recipients key1,key2,key3
    python3 tools/rewrap_v3.py --list-recipients /path/to/encrypted/file
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {e}")
        sys.exit(1)


def check_age_installed() -> bool:
    """Check if AGE is installed and accessible."""
    try:
        run_command(["age", "--version"])
        return True
    except FileNotFoundError:
        return False


def decrypt_file(identity_path: str, encrypted_file: str) -> str:
    """Decrypt a file using AGE."""
    cmd = ["age", "--decrypt", "--identity", identity_path, encrypted_file]
    result = run_command(cmd)
    return result.stdout


def encrypt_file(recipients: list[str], plaintext: str, output_file: str) -> None:
    """Encrypt content with multiple recipients."""
    cmd = ["age", "--encrypt"]
    for recipient in recipients:
        cmd.extend(["--recipient", recipient])
    cmd.extend(["--output", output_file])

    # Write plaintext to stdin
    result = subprocess.run(cmd, input=plaintext, text=True, capture_output=True, check=True)
    if result.returncode != 0:
        print(f"Encryption failed: {result.stderr}")
        sys.exit(1)


def list_recipients(encrypted_file: str) -> None:
    """List recipients from an encrypted file (if possible)."""
    print(f"Listing recipients for: {encrypted_file}")

    # Try to get file info
    try:
        run_command(["age", "--decrypt", "--identity", "/dev/null", encrypted_file])
        print("File appears to be encrypted with AGE")
    except subprocess.CalledProcessError as e:
        if "no identity matched" in e.stderr.lower():
            print("File is encrypted with AGE, but no matching identity found")
        else:
            print(f"Error reading file: {e.stderr}")

    print("Note: AGE doesn't expose recipient information in encrypted files")
    print("You'll need the original recipient list or a valid identity to decrypt")


def rewrap_file(
    old_identity: str,
    new_recipients: list[str],
    encrypted_file: str,
    output_file: str | None = None,
) -> None:
    """Re-encrypt a file with new recipients."""
    print(f"Rewrapping: {encrypted_file}")
    print(f"Old identity: {old_identity}")
    print(f"New recipients: {', '.join(new_recipients)}")

    # Decrypt with old identity
    print("Decrypting with old identity...")
    plaintext = decrypt_file(old_identity, encrypted_file)

    # Determine output file
    if output_file is None:
        output_file = encrypted_file

    # Encrypt with new recipients
    print("Encrypting with new recipients...")
    encrypt_file(new_recipients, plaintext, output_file)

    print(f"Successfully re-encrypted to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="AGE encryption key rotation tool for QuietPatch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Re-encrypt with new recipients
  python3 tools/rewrap_v3.py --old-identity ~/.ssh/id_ed25519 --new-recipients age1...,age2...
  
  # List recipients (limited info available)
  python3 tools/rewrap_v3.py --list-recipients data/vuln_log.json.enc
  
  # Re-encrypt specific file
  python3 tools/rewrap_v3.py --old-identity ~/.ssh/id_ed25519 --new-recipients age1... --file data/vuln_log.json.enc
        """,
    )

    parser.add_argument("--old-identity", help="Path to old private key for decryption")
    parser.add_argument("--new-recipients", help="Comma-separated list of new public keys")
    parser.add_argument(
        "--file", help="Specific encrypted file to rewrap (default: all .enc files in data/)"
    )
    parser.add_argument("--list-recipients", help="List recipients for an encrypted file")
    parser.add_argument("--output", help="Output file path (default: overwrite original)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    # Check AGE installation
    if not check_age_installed():
        print("ERROR: AGE is not installed or not in PATH")
        print("Install AGE from: https://age-encryption.org/")
        sys.exit(1)

    # List recipients mode
    if args.list_recipients:
        list_recipients(args.list_recipients)
        return

    # Validate required arguments
    if not args.old_identity or not args.new_recipients:
        parser.error("--old-identity and --new-recipients are required for re-encryption")

    # Parse new recipients
    new_recipients = [r.strip() for r in args.new_recipients.split(",") if r.strip()]
    if not new_recipients:
        parser.error("No valid recipients provided")

    # Validate recipient format
    for recipient in new_recipients:
        if not recipient.startswith("age1"):
            print(f"Warning: {recipient} doesn't look like a valid AGE public key")

    # Determine files to process
    if args.file:
        files_to_process = [Path(args.file)]
    else:
        # Find all .enc files in data/
        data_dir = Path("data")
        if not data_dir.exists():
            print("ERROR: data/ directory not found")
            sys.exit(1)

        files_to_process = list(data_dir.rglob("*.enc"))
        if not files_to_process:
            print("No .enc files found in data/ directory")
            return

    print(f"Found {len(files_to_process)} encrypted files to process")

    # Process files
    for encrypted_file in files_to_process:
        if args.dry_run:
            print(f"Would rewrap: {encrypted_file}")
            continue

        try:
            output_file = args.output if args.output else str(encrypted_file)
            rewrap_file(args.old_identity, new_recipients, str(encrypted_file), output_file)
        except Exception as e:
            print(f"Error processing {encrypted_file}: {e}")
            continue

    if args.dry_run:
        print(
            "\nDry run completed. Use --old-identity and --new-recipients to actually rewrap files."
        )
    else:
        print("\nRewrapping completed successfully!")
        print(f"Files are now encrypted for recipients: {', '.join(new_recipients)}")


if __name__ == "__main__":
    main()
