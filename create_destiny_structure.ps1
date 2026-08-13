# ============================================================
# DESTINY OS - PROJEKTSTRUKTUR KOMPLETT ERSTELLEN
# Autor: Christian Schmitt
# Datum: 13. August 2026
# ============================================================
# Erzeugt/aktualisiert DESTINY-OS_PROD auf I:, kopiert Quellen
# vom GoldGabel-Stick und aus dem Emulator-Ordner.
# Aendert KEIN git-global-Config und pusht NICHT.
# ============================================================

$ErrorActionPreference = "Continue"

$PROJECT_DIR = "I:\Offline Survival System Emulator\DESTINY-OS_PROD"
$SOURCE_EMU  = "I:\Offline Survival System Emulator"
$SOURCE_CODE = "I:\NOVA USB DEMO STICK\system\nova\goldgabel\destiny"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DESTINY OS - PROJEKTSTRUKTUR INSTALLER         " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Ziel: $PROJECT_DIR"
Write-Host ""

if (-not (Test-Path "I:\")) {
    Write-Host "FEHLER: Laufwerk I: ist nicht erreichbar." -ForegroundColor Red
    exit 1
}

# 1. Ordner erstellen
New-Item -ItemType Directory -Path $PROJECT_DIR -Force | Out-Null
@("iso", "src", "docs", "tools", "logs", "web", "web\src") | ForEach-Object {
    New-Item -ItemType Directory -Path (Join-Path $PROJECT_DIR $_) -Force | Out-Null
    Write-Host "  OK: $_" -ForegroundColor Green
}

# 2. Dateien kopieren (nur wenn Quelle existiert)
if (Test-Path $SOURCE_CODE) {
    Copy-Item "$SOURCE_CODE\*.py"   -Destination "$PROJECT_DIR\src\" -Force
    Copy-Item "$SOURCE_CODE\*.json" -Destination "$PROJECT_DIR\src\" -Force
    Copy-Item "$SOURCE_CODE\*.sh"   -Destination "$PROJECT_DIR\"     -Force
    if (Test-Path "$SOURCE_CODE\destiny_memory.sqlite") {
        Copy-Item "$SOURCE_CODE\destiny_memory.sqlite" -Destination "$PROJECT_DIR\src\" -Force
    }
    Write-Host "  OK: Quellen vom GoldGabel-Stick" -ForegroundColor Green
} else {
    Write-Host "  WARNUNG: $SOURCE_CODE nicht gefunden" -ForegroundColor Yellow
}

if (Test-Path "$SOURCE_EMU\*.py") {
    Copy-Item "$SOURCE_EMU\*.py" -Destination "$PROJECT_DIR\src\" -Force
}
Get-ChildItem $SOURCE_EMU -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -match '\.(sh|md|txt|ps1)$' -and $_.DirectoryName -eq $SOURCE_EMU
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $PROJECT_DIR -Force -ErrorAction SilentlyContinue
}

# 3. Git lokal initialisieren (kein global config, kein Push)
Set-Location $PROJECT_DIR
if (-not (Test-Path (Join-Path $PROJECT_DIR ".git"))) {
    git init
}

git config --local user.name "Christian Schmitt"
if (-not (git config --local user.email)) {
    git config --local user.email "christian@localhost"
}
git rev-parse --is-inside-work-tree > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    git add .
    $pending = git status --porcelain
    if ($pending) {
        git commit -m "Destiny OS v1.0.0"
    } else {
        Write-Host "  Git: nichts zu committen" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "FERTIG. Destiny OS liegt unter:" -ForegroundColor Green
Write-Host "  $PROJECT_DIR"
Write-Host "Naechster Schritt:  python tools\live_check.py"
Write-Host "GitHub-Remote erst setzen, wenn der echte Account feststeht."
Write-Host ""
