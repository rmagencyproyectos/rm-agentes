# Instala precapcut en Windows. Uso (PowerShell): powershell -ExecutionPolicy Bypass -File instalar-windows.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Host "Falta Node 18+: https://nodejs.org"; exit 1 }
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { Write-Host "Falta Python 3: https://python.org (marca 'Add to PATH')"; exit 1 }
if (-not (Get-Command capcut -ErrorAction SilentlyContinue)) { npm i -g capcut-cli@0.31.1 }
py -m pip install --user -q -r requirements.txt
py -c "from faster_whisper import WhisperModel; WhisperModel('medium', compute_type='int8')"
# fuentes de las marcas (estilos/), solo para este usuario
$fuentes = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
New-Item -ItemType Directory -Force $fuentes | Out-Null
foreach ($f in Get-ChildItem fuentes\*.ttf) {
    Copy-Item $f.FullName $fuentes -Force
    New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts" -Name "$($f.BaseName) (TrueType)" -Value "$fuentes\$($f.Name)" -PropertyType String -Force | Out-Null
}
if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) { Write-Host "Falta ffprobe: winget install Gyan.FFmpeg (sin él no se pueden alargar los clips en CapCut)" }
py sonidos\descargar.py  # efectos de sonido (Mixkit): solo descarga los que falten
capcut doctor -H
Write-Host "IMPORTANTE: probado con CapCut 9.5. NO actualices a la 10 (rechaza estos proyectos)."
