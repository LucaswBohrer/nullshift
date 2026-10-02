#Requires -Version 5.1
<#
  NULL//SHIFT release build: clean -> test -> validate rooms ->
  PyInstaller -> smoke -> zip. Fails fast on red.
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

Write-Host "[1/6] clean" -ForegroundColor Cyan
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

Write-Host "[2/6] dependencies" -ForegroundColor Cyan
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

Write-Host "[3/6] tests" -ForegroundColor Cyan
$env:PYTHONPATH = "$root\src"
python -m pytest tests -q

Write-Host "[4/6] room validation" -ForegroundColor Cyan
python tools/validate_rooms.py

Write-Host "[5/6] PyInstaller" -ForegroundColor Cyan
python -m PyInstaller build.spec --noconfirm

Write-Host "[6/6] smoke + zip" -ForegroundColor Cyan
$exe = Join-Path $root "dist\NULLSHIFT\NULLSHIFT.exe"
& $exe --smoke
if ($LASTEXITCODE -ne 0) { throw "smoke test failed" }
$ver = python -c "import sys; sys.path.insert(0,'src'); from nullshift.version import __version__; print(__version__)"
Compress-Archive -Path dist\NULLSHIFT -DestinationPath "NULLSHIFT-$ver-win64.zip" -Force
Write-Host "OK: NULLSHIFT-$ver-win64.zip" -ForegroundColor Green
