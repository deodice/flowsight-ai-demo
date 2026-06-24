param([switch]$Quiet)

$ErrorActionPreference = "SilentlyContinue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $Root "work\runtime\pids.json"

if (-not (Test-Path -LiteralPath $PidFile)) {
    if (-not $Quiet) { Write-Host "FlowSight AI is not running." }
    exit 0
}

$Pids = Get-Content -Raw -LiteralPath $PidFile | ConvertFrom-Json
foreach ($ProcessId in @($Pids.api, $Pids.web)) {
    if ($ProcessId) {
        & taskkill.exe /PID $ProcessId /T /F *> $null
        if ($LASTEXITCODE -ne 0) { Stop-Process -Id $ProcessId -Force }
    }
}

Remove-Item -LiteralPath $PidFile -Force
if (-not $Quiet) { Write-Host "FlowSight AI stopped." -ForegroundColor Green }
