# QuietPatch QuickStart (v0.4.0)

**Private, offline patch advisor.** Scan your apps, map known CVEs, and get a deterministic report. No telemetry. Ever.

## 1) Download
Choose your OS from the releases page:
- **Windows:** QuietPatch-Setup-v0.4.0.exe
- **macOS:** QuietPatch-v0.4.0.dmg
- **Linux:** QuietPatch-v0.4.0-x86_64.AppImage

## 2) Verify (recommended)
See **VERIFY.md** in the release to check SHA256 and signature.

## 3) Install / Run
**Windows**
1. Double‑click the installer. If SmartScreen warns, click *More info → Run anyway* (we use open signing with published checks).
2. Launch **QuietPatch** from the Start Menu.

**macOS**
1. Open the DMG and drag **QuietPatch** into Applications.
2. First launch: right‑click the app → **Open** → **Open**.

**Linux**
1. Mark the AppImage executable: `chmod +x QuietPatch-v0.4.0-x86_64.AppImage`
2. Run it: `./QuietPatch-v0.4.0-x86_64.AppImage`

## 4) First run (3 steps)
1. Click **Start Scan** (default is **Read‑only**; no changes made).
2. Wait for the scan to complete; then click **View Report**.
3. (Optional) Review recommendations. Apply fixes only if you're comfortable, or contact your IT admin.

## 5) What we collect
Nothing. QuietPatch runs **100% offline** by default. No telemetry.

## 6) Troubleshooting (plain‑English)
- **Windows SmartScreen warning?** Click "More info" then "Run anyway". We use open signing (minisign + checksums) instead of paid certs. Verify first if you prefer.
- **macOS "unidentified developer"?** Right-click the app → "Open" → "Open" once. Future launches open normally.
- **Verification failed?** Don't run the file. Re‑download from the official release.
- **App won't open?** Reboot and try again, or run the CLI version included in the release.

## 7) Support
File an issue on the GitHub repo. Include the short error message and your OS.
