# SCCM/ConfigMgr collections & detection

## Collections (WQL examples)

* **Canary:** static collection `QP-Canary-Win10`.
* **Wave1/Wave2:** query by OU, tag, or device name pattern.

## Application model

* **Detection Method:** Use `scripts/win/detect.ps1` (wrap in a detection script). Return code 0 = Installed.
* **Install program:** `powershell.exe -ExecutionPolicy Bypass -File "scripts\win\apply.ps1"`
* **Uninstall program (Rollback):** `powershell.exe -ExecutionPolicy Bypass -File "scripts\win\rollback.ps1"`
* **User Experience:** Install for system, hidden, no restart.

## Detection Script for SCCM

```powershell
# SCCM Detection Script
$BundleRoot = "$PSScriptRoot\..\.."
$manifest = Get-Content (Join-Path $BundleRoot 'manifest.json') -Raw | ConvertFrom-Json
$target = $manifest.targets | Where-Object { $_.os -eq 'windows' }

# Check if target version is installed
$exe = $target.verify.path
if (!(Test-Path $exe)) { 
    Write-Output "Target not found: $exe"
    exit 1 
}

$installedVersion = (Get-Item $exe).VersionInfo.FileVersion
$targetVersion = $target.verify.version

if ($installedVersion -like "$targetVersion*") {
    Write-Output "Target version $targetVersion is installed"
    exit 0
} else {
    Write-Output "Target version $targetVersion not found. Installed: $installedVersion"
    exit 1
}
```

## Deployment Strategy

1. Create Collections for Canary, Wave1, Wave2
2. Create Application with detection script
3. Deploy to Canary collection first
4. Monitor success rates
5. Deploy to subsequent waves based on success criteria
6. Use uninstall program for rollback scenarios
