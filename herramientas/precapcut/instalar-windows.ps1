# Instala precapcut en Windows. Uso (PowerShell): powershell -ExecutionPolicy Bypass -File instalar-windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Host "Falta Node 18+: https://nodejs.org"; exit 1 }
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { Write-Host "Falta Python 3: https://python.org (marca 'Add to PATH')"; exit 1 }
if (-not (Get-Command capcut -ErrorAction SilentlyContinue)) { npm i -g capcut-cli@0.31.1 }
py -m pip install --user -q -r requirements.txt
py -c "from faster_whisper import WhisperModel; WhisperModel('medium', compute_type='int8')"
capcut doctor -H
Write-Host "IMPORTANTE: probado con CapCut 9.5. NO actualices a la 10 (rechaza estos proyectos)."
