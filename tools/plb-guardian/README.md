# PLB PROJECT GUARDIAN

Automatic local project recovery layer.

## Install

Double-click `INSTALL-PLB-GUARDIAN.bat`.

The Guardian installs a Windows Scheduled Task that runs every 30 minutes.

## Manual backup

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\plb-guardian\backup.ps1
```

## Restore

Double-click `RESTORE-PLB-PROJECT.bat`, or run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\plb-guardian\restore.ps1 -Destination "C:\PLB\RecoveredProject"
```

Only files committed and pushed at least once can be recovered.
Do not commit secrets. Use Git LFS for large binary assets.
