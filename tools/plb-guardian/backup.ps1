param(
  [string]$ProjectPath = (Get-Location).Path,
  [string]$Branch = "main"
)
$ErrorActionPreference = "Stop"
$ProjectPath = (Resolve-Path $ProjectPath).Path
Set-Location $ProjectPath
if (-not (Test-Path ".git")) { throw "Not a Git repository: $ProjectPath" }

git fetch origin $Branch --quiet
$status = git status --porcelain
if (-not $status) { Write-Host "No local changes. Remote is current." -ForegroundColor Green; exit 0 }

$secretPatterns = @("\.env$","\ .env\.","id_rsa$","id_ed25519$","credentials\.json$","service-account.*\.json$") -replace '^ ',''
$changedFiles = git status --porcelain | ForEach-Object { $_.Substring(3).Trim('"') }
foreach ($file in $changedFiles) {
  foreach ($pattern in $secretPatterns) {
    if ($file -match $pattern) { throw "GUARDIAN STOPPED: possible secret file detected: $file" }
  }
}

git add -A
git commit -m "guardian: automatic project snapshot $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin $Branch
Write-Host "PROJECT SNAPSHOT PUSHED TO GITHUB" -ForegroundColor Green
Write-Host "Recovery point: $(git rev-parse HEAD)" -ForegroundColor Green
