<# 
qp-report.ps1: PowerShell wrapper for QuietPatch reports

Examples:
  .\qp-report.ps1 tech --scan scan.json --policy policy.json --out tech.html --pdf tech.pdf
  .\qp-report.ps1 exec --scan scan.json --kpi kpi.json --out exec.html --pdf exec.pdf
#>

param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Rest
)

function Invoke-QP {
  param([string[]]$Args)

  $qp = Get-Command quietpatch -ErrorAction SilentlyContinue
  if ($qp) {
    $cmd = @("quietpatch") + $Args
  } else {
    # Prefer py launcher; fallback to python
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
      $cmd = @("py", "-m", "quietpatch") + $Args
    } else {
      $cmd = @("python", "-m", "quietpatch") + $Args
    }
  }
  Write-Host ("PS> " + ($cmd -join " "))
  & $cmd
  exit $LASTEXITCODE
}

if (-not $Rest -or $Rest[0] -in @("-h", "--help")) {
  Write-Host "Usage:"
  Write-Host "  .\qp-report.ps1 tech [quietpatch-report-options]"
  Write-Host "  .\qp-report.ps1 exec [quietpatch-report-options]"
  Write-Host ""
  Write-Host "Examples:"
  Write-Host "  .\qp-report.ps1 tech --scan scan.json --policy policy.json --out tech.html --pdf tech.pdf"
  Write-Host "  .\qp-report.ps1 exec --scan scan.json --kpi kpi.json --out exec.html --pdf exec.pdf"
  exit 0
}

$sub = $Rest[0]
$forward = $Rest[1..($Rest.Length-1)]

if ($sub -notin @("tech","exec")) {
  Write-Host "First argument must be 'tech' or 'exec'."
  exit 2
}

Invoke-QP @("report", $sub) + $forward
