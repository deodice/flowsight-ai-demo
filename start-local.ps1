$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimeDir = Join-Path $Root "work\runtime"
$PidFile = Join-Path $RuntimeDir "pids.json"
$ApiLog = Join-Path $RuntimeDir "api.log"
$WebLog = Join-Path $RuntimeDir "web.log"
New-Item -ItemType Directory -Force $RuntimeDir | Out-Null

function Find-CommandPath {
    param([string[]]$Names)
    foreach ($Name in $Names) {
        $Command = Get-Command $Name -ErrorAction SilentlyContinue
        if ($Command) { return $Command.Source }
    }
    return $null
}

function Start-HiddenProcess {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$LogPath,
        [string]$Name
    )
    $CommandFile = Join-Path $RuntimeDir "$Name.cmd"
    $QuotedArguments = ($Arguments | ForEach-Object {
        '"' + ($_ -replace '"', '""') + '"'
    }) -join " "
    @(
        "@echo off"
        "cd /d `"$WorkingDirectory`""
        "`"$FilePath`" $QuotedArguments >> `"$LogPath`" 2>&1"
    ) | Set-Content -LiteralPath $CommandFile -Encoding ASCII

    Set-Content -LiteralPath $LogPath -Value ""
    $Info = New-Object System.Diagnostics.ProcessStartInfo
    $Info.FileName = $env:ComSpec
    $Info.Arguments = "/d /s /c `"`"$CommandFile`"`""
    $Info.WorkingDirectory = $RuntimeDir
    $Info.UseShellExecute = $false
    $Info.CreateNoWindow = $true
    $Info.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    return [System.Diagnostics.Process]::Start($Info)
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) {
    $SystemPython = Find-CommandPath @("py", "python", "python3")
    if (-not $SystemPython) {
        throw "Python 3.12+ was not found. Install Python from https://www.python.org/downloads/ and run this script again."
    }
    Write-Host "Creating the local Python environment..."
    if ([IO.Path]::GetFileNameWithoutExtension($SystemPython) -eq "py") {
        & $SystemPython -3.12 -m venv (Join-Path $Root ".venv")
    } else {
        & $SystemPython -m venv (Join-Path $Root ".venv")
    }
}

$Pnpm = Find-CommandPath @("pnpm.cmd", "pnpm")
if (-not $Pnpm) {
    $CodexPnpm = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\bin\pnpm.cmd"
    if (Test-Path -LiteralPath $CodexPnpm) { $Pnpm = $CodexPnpm }
}
if (-not $Pnpm) {
    throw "pnpm was not found. Install Node.js, then run: corepack enable"
}

if (-not (Test-Path -LiteralPath (Join-Path $Root "node_modules"))) {
    Write-Host "Installing the web dependencies..."
    & $Pnpm install
}

$FastApiCheck = & $Python -c "import fastapi; print('ready')" 2>$null
if ($FastApiCheck -ne "ready") {
    Write-Host "Installing the API dependencies..."
    & $Python -m pip install -r (Join-Path $Root "apps\api\requirements.txt")
}

$BuildId = Join-Path $Root "apps\web\.next\BUILD_ID"
$NeedsWebBuild = -not (Test-Path -LiteralPath $BuildId)
if (-not $NeedsWebBuild) {
    $LatestWebSource = Get-ChildItem `
        (Join-Path $Root "apps\web\app"), `
        (Join-Path $Root "apps\web\components"), `
        (Join-Path $Root "apps\web\lib") `
        -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -in @(".ts", ".tsx", ".css", ".json") } |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    $NeedsWebBuild = $LatestWebSource -and $LatestWebSource.LastWriteTimeUtc -gt (Get-Item -LiteralPath $BuildId).LastWriteTimeUtc
}
if ($NeedsWebBuild) {
    Write-Host "Building the web application..."
    & $Pnpm --filter "@flowsight/web" build
}

$env:PYTHONPATH = Join-Path $Root "apps\api"
$env:DATABASE_URL = "sqlite:///$((Join-Path $Root 'flowsight.db').Replace('\', '/'))"
$env:JWT_SECRET = "local-development-secret-change-before-production"
$env:APP_URL = "http://localhost:3000"

Write-Host "Updating the local database schema..."
& $Python -m app.local_migrate
if ($LASTEXITCODE -ne 0) { throw "The local database migration failed." }

Write-Host "Preparing the three demo workspaces and procurement data..."
& $Python -m app.seed
if ($LASTEXITCODE -ne 0) { throw "The demo workspace seed failed." }

if (Test-Path -LiteralPath $PidFile) {
    & (Join-Path $Root "stop-local.ps1") -Quiet
}

$Api = Start-HiddenProcess `
    -FilePath $Python `
    -Arguments @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory (Join-Path $Root "apps\api") `
    -LogPath $ApiLog `
    -Name "api"

$Node = Find-CommandPath @("node", "node.exe")
if (-not $Node) {
    $CodexNode = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
    if (Test-Path -LiteralPath $CodexNode) { $Node = $CodexNode }
}
if (-not $Node) { throw "Node.js was not found." }

$Next = Join-Path $Root "apps\web\node_modules\next\dist\bin\next"
$Web = Start-HiddenProcess `
    -FilePath $Node `
    -Arguments @($Next, "start", "-p", "3000") `
    -WorkingDirectory (Join-Path $Root "apps\web") `
    -LogPath $WebLog `
    -Name "web"

@{ api = $Api.Id; web = $Web.Id } | ConvertTo-Json | Set-Content -LiteralPath $PidFile

Start-Sleep -Seconds 2
if ($Api.HasExited) {
    throw "The API did not start.`n$(Get-Content -Raw -LiteralPath $ApiLog)"
}
if ($Web.HasExited) {
    throw "The web app did not start.`n$(Get-Content -Raw -LiteralPath $WebLog)"
}
Write-Host ""
Write-Host "FlowSight AI is running." -ForegroundColor Green
Write-Host "App:      http://localhost:3000"
Write-Host "Freight:  http://localhost:3000/app/freight"
Write-Host "API docs: http://localhost:8000/docs"
Write-Host "Demo:     maya@demo.flowsight.ai / FlowSightDemo!"
Write-Host ""
Write-Host "To stop it, run: .\stop-local.ps1"
Write-Host "Logs: work\runtime\api.log and work\runtime\web.log"

Start-Process "http://localhost:3000"
