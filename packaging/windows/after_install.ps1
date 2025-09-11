# QuietPatch Windows post-install script
# Creates scheduled task for daily vulnerability scanning

$TaskName = "QuietPatch Daily Scan"
$TaskPath = "C:\Program Files\QuietPatch\quietpatch.pyz"

# Create the scheduled task XML
$TaskXML = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T03:30:00</StartBoundary>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"$TaskPath" --scheduled-run</Arguments>
      <WorkingDirectory>C:\Program Files\QuietPatch</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

# Remove existing task if it exists
schtasks /Delete /TN "$TaskName" /F 2>$null

# Create the new scheduled task
$TaskXML | Out-File -FilePath "$env:TEMP\quietpatch_task.xml" -Encoding UTF8
schtasks /Create /TN "$TaskName" /XML "$env:TEMP\quietpatch_task.xml" /F

# Cleanup
Remove-Item "$env:TEMP\quietpatch_task.xml" -Force

Write-Host "QuietPatch scheduled task created successfully"










