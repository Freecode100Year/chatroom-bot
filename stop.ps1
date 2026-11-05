$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pidFile = Join-Path $dir "bot.pid"

if (-not (Test-Path $pidFile)) {
    Write-Output "没有找到 bot.pid，机器人可能未在运行"
    exit 0
}

$botPid = (Get-Content $pidFile -Raw).Trim()
if ($botPid -and (Get-Process -Id $botPid -ErrorAction SilentlyContinue)) {
    & taskkill /PID $botPid /T /F | Out-Null
    Write-Output "已停止 PID=$botPid"
} else {
    Write-Output "PID=$botPid 进程不存在"
}
Remove-Item $pidFile -ErrorAction SilentlyContinue
