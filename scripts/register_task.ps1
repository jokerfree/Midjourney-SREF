<#
  注册 / 更新 Windows 计划任务（默认每周日 20:00 增量更新）
  用法：
    powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1
    powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1 -Time 09:30 -Schedule DAILY
    powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1 -Remove
#>
param(
  [string]$Time = "20:00",
  [ValidateSet("WEEKLY", "DAILY", "MONTHLY")] [string]$Schedule = "WEEKLY",
  [switch]$Remove
)

$taskName = "MJ-SREF-Library-Update"
$root = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $PSScriptRoot "run_update.ps1"

if ($Remove) {
  schtasks /Delete /TN $taskName /F
  Write-Host "已删除计划任务：$taskName"
  exit $LASTEXITCODE
}

if (-not (Test-Path $runner)) { throw "找不到 $runner" }
$action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$runner`""

$cliArgs = @("/Create", "/TN", $taskName, "/SC", $Schedule, "/ST", $Time, "/TR", $action, "/F")
if ($Schedule -eq "WEEKLY") { $cliArgs += @("/D", "SUN") }
if ($Schedule -eq "MONTHLY") { $cliArgs += @("/D", "1") }

& schtasks @cliArgs
if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "已注册计划任务：$taskName（$Schedule $Time）" -ForegroundColor Green
  Write-Host "立即测试：schtasks /Run /TN $taskName"
  Write-Host "查看状态：schtasks /Query /TN $taskName /V /FO LIST"
} else {
  Write-Host "注册失败，请用「以管理员身份运行」的 PowerShell 重试，或手动执行上面的 schtasks 命令。" -ForegroundColor Yellow
}
