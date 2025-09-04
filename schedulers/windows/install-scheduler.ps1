# QuietPatch Windows Task Scheduler Installation
# Run as Administrator

$taskName = "QuietPatch Catalog Update"
$action = New-ScheduledTaskAction -Execute "quietpatch.exe" -Argument "catalog-update"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Environment variables
$envVars = @{
    "QP_OFFLINE" = "1"
}

$action.Arguments = "catalog-update"
$action.WorkingDirectory = "C:\Program Files\QuietPatch"

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily QuietPatch catalog update" -Force

Write-Host "✅ Task '$taskName' registered successfully"
Write-Host "📅 Runs daily at 3:00 AM"
Write-Host "🔧 To modify: Task Scheduler > Task Scheduler Library > $taskName"
