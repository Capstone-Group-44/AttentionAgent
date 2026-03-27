Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot

Write-Host "==============================================="
Write-Host " Building ScreenGaze for Windows"
Write-Host "==============================================="

function Resolve-Command($name) {
  $cmd = Get-Command $name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) { return $null }
  return $cmd.Path
}

# 1) Choose Python interpreter
# You can override with an explicit interpreter path:
#   $env:SCREENGAZE_PYTHON = "C:\\path\\to\\python.exe"
$python = $env:SCREENGAZE_PYTHON

if ([string]::IsNullOrWhiteSpace($python)) {
  $repoRoot = Resolve-Path ".."

  # Qt/PySide6 breaks when installed under paths that contain commas (",").
  # If the repo is under a comma path, the repo-root venv will also be under a comma path.
  if ($repoRoot.Path -like "*,*") {
    throw "This project path contains a comma: '$($repoRoot.Path)'. PySide6/Qt may fail to build from a venv located under a comma path. Move the repo to a path without commas, or set `$env:SCREENGAZE_PYTHON to a Python interpreter from a venv installed in a comma-free path."
  }

  # Optional venv activation
  $candidateVenvs = @(
    (Join-Path $repoRoot "venv"),
    (Join-Path $repoRoot ".venv311")
  )

  foreach ($venvDir in $candidateVenvs) {
    $activate = Join-Path $venvDir "Scripts\\Activate.ps1"
    if (Test-Path $activate) {
      Write-Host "-> Activating venv at $venvDir"
      . $activate
      break
    }
  }

  $python = "python"
}

$pythonExe = & $python -c "import sys; print(sys.executable)"
$pythonVer = & $python -c "import sys; print(sys.version.split()[0])"
Write-Host "-> Python: $pythonExe"
Write-Host "-> Version: $pythonVer"

# 2) Ensure deps
Write-Host "-> Ensuring build dependencies are installed..."
& $python -m pip --version
& $python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host "-> Installing PyInstaller..."
  & $python -m pip install pyinstaller
}

Write-Host "-> Installing desktop-app requirements..."
& $python -m pip install -r requirements.txt

# 3) Clean
Write-Host "-> Cleaning previous build artifacts..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# 4) Build
Write-Host "-> Running PyInstaller..."
& $python -m PyInstaller "ScreenGaze.win.spec" --noconfirm

$exePath = Join-Path "dist\\ScreenGaze" "ScreenGaze.exe"
if (-not (Test-Path $exePath)) {
  throw "Build failed: expected $exePath"
}

Write-Host ""
Write-Host "OK: Built one-folder app at dist\\ScreenGaze\\"
Write-Host "    EXE: $exePath"

# 5) Optional installer (Inno Setup)
Write-Host ""
$iscc = Resolve-Command "iscc"
if ($null -ne $iscc -and (Test-Path "installer\\ScreenGaze.iss")) {
  Write-Host "-> Found Inno Setup (iscc). Building installer..."
  & $iscc "installer\\ScreenGaze.iss" | Write-Host
  Write-Host "OK: Installer build finished (check installer\\Output\\)"
} else {
  Write-Host "Note: To produce a Windows installer (.exe), install Inno Setup and rerun this script."
  Write-Host "      It will auto-detect 'iscc' and build from installer\\ScreenGaze.iss"
}

Pop-Location
