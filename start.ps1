$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { throw "Python was not found on PATH." }
$pidFile = Join-Path $dir "bot.pid"

if (Test-Path $pidFile) {
    $old = (Get-Content $pidFile -Raw).Trim()
    if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
        Write-Output "Bot is already running (PID=$old)"
        exit 0
    }
    Remove-Item $pidFile -ErrorAction SilentlyContinue
}

Start-Process -FilePath $python -ArgumentList @("`"$dir\bot.py`"") -WorkingDirectory $dir -WindowStyle Hidden
Start-Sleep -Seconds 2

if (Test-Path $pidFile) {
    Write-Output "Started (PID=$((Get-Content $pidFile -Raw).Trim()))"
} else {
    Write-Output "Startup command ran, but bot.pid was not created. Check logs/errors.log."
}
