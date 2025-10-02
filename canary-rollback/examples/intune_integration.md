# Microsoft Intune (Win32 app) packaging

## Win32 package commands

* **Install command:**
  `powershell.exe -ExecutionPolicy Bypass -File ".\scripts\win\apply.ps1"`
* **Uninstall (used as rollback):**
  `powershell.exe -ExecutionPolicy Bypass -File ".\scripts\win\rollback.ps1"`
* **Detection rule:** use a **PowerShell detection script** returning 0 if target installed, else non-zero.

## Intune Detection Script

```powershell
# Exit 0 if target version present
$BundleRoot = "$PSScriptRoot\..\.."  # when wrapped by .intunewin, adjust relative path as needed
$manifest = Get-Content (Join-Path $BundleRoot 'manifest.json') -Raw | ConvertFrom-Json
$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }
$exe = $target.verify.path
if (!(Test-Path $exe)) { exit 1 }
$v = (Get-Item $exe).VersionInfo.FileVersion
if ($v -like "$($target.verify.version)*") { exit 0 } else { exit 1 }
```

## Assignment model

* Create Azure AD dynamic groups:

  * `QuietPatch-Canary`: devices with `deviceCategory -eq "QP-Canary"` or a tag.
  * `QuietPatch-Wave1`, `QuietPatch-Wave2`: same idea.
* Assign the Win32 app to Canary first (**Required**), monitor success ≥98%, then assign to Wave1, then Wave2.

## Packaging Steps

1. Create a folder with your bundle contents
2. Use Microsoft Win32 Content Prep Tool to create `.intunewin` file
3. Upload to Intune as Win32 app
4. Configure detection rules using the PowerShell script above
5. Set up assignment groups for canary deployment
