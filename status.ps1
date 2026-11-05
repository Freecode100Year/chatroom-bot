$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$status = Join-Path $dir "status.json"
if (Test-Path $status) {
    Get-Content $status -Raw -Encoding UTF8
} else {
    Write-Output "尚无 status.json（机器人可能还没完成第一次轮询）"
}
Write-Output "`n--- 最近 15 条日志 ---"
$log = Join-Path $dir "logs\bot.log"
if (Test-Path $log) { Get-Content $log -Tail 15 -Encoding UTF8 }
Write-Output "`n--- 最近 5 条错误 ---"
$err = Join-Path $dir "logs\errors.log"
if (Test-Path $err) { Get-Content $err -Tail 5 -Encoding UTF8 }
