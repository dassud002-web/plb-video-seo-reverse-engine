param(
  [string]$ProjectPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
  [int]$Minutes = 30
)

$ErrorActionPreference = "Stop"

try {
  $ProjectPath = (Resolve-Path $ProjectPath).Path
  $BackupScript = Join-Path $ProjectPath "tools\plb-guardian\backup.ps1"
  $TaskName = "PLB-Project-Guardian"

  if (-not (Test-Path $BackupScript)) {
    throw "Guardian backup script not found: $BackupScript"
  }

  $ps = (Get-Command powershell.exe).Source
  $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $BackupScript + '" -ProjectPath "' + $ProjectPath + '"'

  $action = New-ScheduledTaskAction -Execute $ps -Argument $arguments

  # Windows PowerShell uses the enum value "Limited", not "LeastPrivilege".
  $trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $Minutes)

  $principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

  Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Force | Out-Null

  Write-Host ""
  Write-Host "========================================" -ForegroundColor Green
  Write-Host " PLB PROJECT GUARDIAN INSTALLED" -ForegroundColor Green
  Write-Host "========================================" -ForegroundColor Green
  Write-Host "Project:  $ProjectPath"
  Write-Host "Interval: every $Minutes minutes"
  Write-Host "Task:     $TaskName"
  Write-Host ""
  Write-Host "First automatic backup: within about 1 minute." -ForegroundColor Cyan
  exit 0
}
catch {
  Write-Host ""
  Write-Host "========================================" -ForegroundColor Red
  Write-Host " GUARDIAN INSTALLATION FAILED" -ForegroundColor Red
  Write-Host "========================================" -ForegroundColor Red
  Write-Host $_.Exception.Message -ForegroundColor Yellow
  exit 1
}
