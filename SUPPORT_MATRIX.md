# QuietPatch Support Matrix

## Supported Platforms

| OS | Architecture | Status | Notes |
|---|---|---|---|
| macOS 13+ | arm64 (Apple Silicon) | ✅ Fully supported | Native performance |
| macOS 13+ | x64 (Intel) | ✅ Fully supported | Via Rosetta 2 |
| Windows 10/11 | x64 | ✅ Fully supported | Native performance |
| Ubuntu 22.04 LTS | x64 | ✅ Fully supported | Native performance |
| Ubuntu 24.04 LTS | x64 | ✅ Fully supported | Native performance |
| Other Linux | x64 | ⚠️ Community support | May work, not tested |

## Python Requirements

| Python Version | Status | Support Level |
|---|---|---|
| 3.11.x | ✅ Fully supported | Primary support |
| 3.12.x | ✅ Fully supported | Primary support |
| 3.13.x | ❌ Not supported | Not yet supported |
| 3.10.x and below | ❌ Not supported | Unsupported |
| 3.14.x and above | ❌ Not supported | Unsupported |

**Version Policy:**
- We support **exactly two** CPython minor versions (currently 3.11 and 3.12)
- New versions are added only after thorough testing with wheels + constraints
- Old versions are deprecated when new ones are added
- Python 3.13 support will be added in a future release

## Network Requirements

| Mode | Network Required | Notes |
|---|---|---|
| Online | ✅ Yes | Downloads latest CVE data from NVD |
| Offline | ❌ No | Uses local database snapshot |
| CI/CD | ❌ No | Always runs offline for security |

**Offline Mode:**
- Fully supported with local database snapshots
- Database updated via `quietpatch db fetch`
- No network calls when `QP_OFFLINE=1` is set

## Database Format

| Format | Status | Dependencies | Notes |
|---|---|---|---|
| `.tar.zst` | ✅ Primary | `zstandard` Python package | Best compression |
| `.tar.gz` | ✅ Supported | Built-in `gzip` | Fallback format |
| `.tar.bz2` | ✅ Supported | Built-in `bz2` | Alternative format |

**Requirements:**
- No external `zstd` binary required
- Uses Python `zstandard` package (included in constraints)
- Database files are typically 50-200MB compressed

## Installation Methods

| Method | Python Required | Platform | Status |
|---|---|---|---|
| `pip install` | ✅ Yes | All | ✅ Recommended |
| One-command installers | ❌ No | All | ✅ Convenient |
| Homebrew | ❌ No | macOS | ✅ Native |
| Scoop | ❌ No | Windows | ✅ Native |
| Standalone executables | ❌ No | All | ✅ No dependencies |

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| "Requires Python ≥3.11" | Wrong Python version | Install Python 3.12 |
| "zstandard not found" | Missing dependency | `pip install zstandard` |
| "DB not found (offline)" | No database | `quietpatch db fetch` |
| Gatekeeper blocks (macOS) | Unsigned binary | `xattr -dr com.apple.quarantine` |
| SARIF empty in CI | Wrong path | Use `--sarif out.sarif` |

## Security Considerations

| Aspect | Status | Notes |
|---|---|---|
| Code signing | ✅ Windows/macOS | Authenticode/Notarization |
| Checksums | ✅ All platforms | SHA256SUMS provided |
| Minisign | ✅ Required | All catalogs cryptographically verified |
| Path traversal protection | ✅ All platforms | Prevents `../` attacks in archives |
| Downgrade protection | ✅ All platforms | Blocks rollback attacks via epoch |
| Offline operation | ✅ Default | No data leaves your machine |
| Telemetry | ❌ None | No tracking or analytics |
| Alpine/musl | ❌ Not supported | Use Docker image instead |

## Performance Expectations

| Operation | Typical Time | Notes |
|---|---|---|
| Installation | 10-30 seconds | Depends on network speed |
| Database fetch | 1-5 minutes | 50-200MB download |
| Scan (offline) | 30-120 seconds | Depends on system size |
| Report generation | 1-5 seconds | HTML/JSON/SARIF output |

## Getting Help

1. **Check environment**: `quietpatch env doctor`
2. **View logs**: Check console output for error codes
3. **Report issues**: Use GitHub issue template with environment details
4. **Documentation**: See README.md for detailed usage

## Version Support Lifecycle

- **Current**: Python 3.11, 3.12
- **Next**: Python 3.12, 3.13 (when 3.13 support is added)
- **Deprecated**: None currently
- **End of life**: Python 3.10 and below, 3.14 and above
