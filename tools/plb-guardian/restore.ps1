param(
  [string]$RepositoryUrl = "https://github.com/dassud002-web/plb-video-seo-reverse-engine.git",
  [Parameter(Mandatory=$true)][string]$Destination,
  [string]$Ref = "main"
)
$ErrorActionPreference = "Stop"
if (Test-Path $Destination) {
  if ((Get-ChildItem -Force $Destination).Count -gt 0) { throw "Destination is not empty: $Destination" }
} else { New-Item -ItemType Directory -Path $Destination | Out-Null }
git clone --branch $Ref $RepositoryUrl $Destination
Write-Host "PROJECT RESTORED: $Destination" -ForegroundColor Green
