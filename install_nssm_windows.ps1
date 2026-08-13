# ============================================================
# NSSM fuer Destiny OS (Windows)
# Laedt NSSM nach tools\nssm und registriert Dienste optional.
# Aufruf:
#   .\install_nssm_windows.ps1
#   .\install_nssm_windows.ps1 -RegisterServices
# ============================================================

param(
    [switch]$RegisterServices
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $PROJECT_DIR) {
    $PROJECT_DIR = "I:\Offline Survival System Emulator\DESTINY-OS_PROD"
}

$NSSM_URL = "https://nssm.cc/release/nssm-2.24.zip"
$NSSM_DIR = Join-Path $PROJECT_DIR "tools\nssm"
$PYTHON = Join-Path $PROJECT_DIR ".venv\Scripts\python.exe"
if (-not (Test-Path $PYTHON)) {
    $PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source
}

Write-Host "NSSM-Ziel: $NSSM_DIR"

New-Item -ItemType Directory -Path $NSSM_DIR -Force | Out-Null
$nssmExe = Join-Path $NSSM_DIR "nssm.exe"

if (-not (Test-Path $nssmExe)) {
    $temp = Join-Path $env:TEMP "destiny-nssm.zip"
    Write-Host "Lade NSSM..."
    Invoke-WebRequest -Uri $NSSM_URL -OutFile $temp
    $extract = Join-Path $env:TEMP "destiny-nssm"
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive -Path $temp -DestinationPath $extract -Force
    $found = Get-ChildItem $extract -Recurse -Filter nssm.exe | Where-Object { $_.FullName -match "win64" } | Select-Object -First 1
    if (-not $found) {
        throw "nssm.exe (win64) nicht im Archiv gefunden"
    }
    Copy-Item $found.FullName -Destination $nssmExe -Force
}

Write-Host "NSSM bereit: $nssmExe"

$catalog = @(
    @{ Name = "core";     Args = @("$PROJECT_DIR\src\destiny_manager.py") },
    @{ Name = "monitor";  Args = @("$PROJECT_DIR\src\destiny_monitor.py") },
    @{ Name = "backup";   Args = @("$PROJECT_DIR\src\destiny_backup_agent.py") },
    @{ Name = "listener"; Args = @("$PROJECT_DIR\src\destiny_session_listener.py") },
    @{ Name = "gui";      Args = @("-m", "streamlit", "run", "$PROJECT_DIR\src\destiny_gui.py", "--server.headless", "true") }
)

if (-not $RegisterServices) {
    Write-Host "Kein -RegisterServices: es werden keine Windows-Dienste angelegt."
    Write-Host "Beispiel: & `"$nssmExe`" install Destiny_core `"$PYTHON`" `"$PROJECT_DIR\src\destiny_manager.py`""
    exit 0
}

if (-not $PYTHON) {
    throw "Python nicht gefunden. Lege zuerst .venv an."
}

foreach ($svc in $catalog) {
    $display = "Destiny_$($svc.Name)"
    Write-Host "Installiere $display"
    & $nssmExe stop $display 2>$null
    & $nssmExe remove $display confirm 2>$null
    & $nssmExe install $display $PYTHON @($svc.Args)
    & $nssmExe set $display AppDirectory $PROJECT_DIR
    & $nssmExe set $display Start SERVICE_AUTO_START
    & $nssmExe start $display
}

Write-Host "Dienste registriert. Verwaltung: $nssmExe edit Destiny_core"
