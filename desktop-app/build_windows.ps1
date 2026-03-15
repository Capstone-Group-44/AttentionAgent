# build_windows.ps1 - Build Screen Gaze for Windows
# ──────────────────────────────────────────────────────────────────────
# Usage:
#   .\build_windows.ps1
# ──────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Building Screen Gaze for Windows" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# ── 1. Ensure we are in the right directory ──────────────────────────
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# ── 2. Ensure virtual environment ──────────────────────────────────
$VENV_DIR = Join-Path (Split-Path $SCRIPT_DIR -Parent) ".venv_win"
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "→ Creating virtual environment at $VENV_DIR using Python 3.10..." -ForegroundColor Yellow
    py -3.10 -m venv $VENV_DIR
}

Write-Host "→ Activating virtual environment..." -ForegroundColor Yellow
$VENV_ACTIVATE = Join-Path $VENV_DIR "Scripts\Activate.ps1"
& $VENV_ACTIVATE

# ── 3. Install/Upgrade requirements ───────────────────────────────
Write-Host "→ Ensuring dependencies are installed..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# ── 4. Clean previous builds ────────────────────────────────────────
Write-Host "→ Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# ── 5. Run PyInstaller ──────────────────────────────────────────────
Write-Host "→ Running PyInstaller..." -ForegroundColor Yellow
pyinstaller ScreenGaze.spec --noconfirm

# ── 6. Verify output ────────────────────────────────────────────────
$EXE_PATH = "dist\ScreenGaze\ScreenGaze.exe"
if (Test-Path $EXE_PATH) {
    $size = (Get-Item $EXE_PATH).Length / 1MB
    Write-Host ""
    Write-Host "✅ Build succeeded!" -ForegroundColor Green
    Write-Host "   Executable: $EXE_PATH"
    Write-Host "   Size: $('{0:N2}' -f $size) MB"
} else {
    Write-Host "❌ Build failed - Executable not found at $EXE_PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Done! To test, run:  .\$EXE_PATH" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
