# Jamf Pro (macOS) smart groups & policies

## Extension Attribute (Version capture)

```bash
#!/bin/bash
APP="/Applications/iTerm.app"
if [ -d "$APP" ]; then
  /usr/bin/defaults read "$APP/Contents/Info.plist" CFBundleShortVersionString
else
  echo "Not Installed"
fi
```

## Smart Groups

* `QP iTerm2 Target Needed`: EA value != `3.5.12`.

## Policies

* **Canary Policy:** scope to a static group `QP-Canary-Mac`. Run `scripts/mac/apply.sh` from the bundle (hosted on internal share or Jamf Distribution). Post-install, run `scripts/mac/verify.sh`. If policy fails, trigger **Rollback Policy** smart group `QP iTerm2 Rollback Needed` (use a failed flag file or EA mismatch).
* **Rollback Policy:** runs `scripts/mac/rollback.sh`.

## Setup Steps

1. Create Extension Attribute for version detection
2. Create Smart Groups based on version requirements
3. Upload bundle to Jamf Distribution Points
4. Create Canary Policy with apply script
5. Create Rollback Policy with rollback script
6. Set up policy scoping for canary groups
7. Configure failure handling and automatic rollback triggers
