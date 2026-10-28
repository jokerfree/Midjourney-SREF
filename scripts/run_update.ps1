<#
  定期更新入口（供 Windows 计划任务调用）
  手动运行：powershell -ExecutionPolicy Bypass -File scripts\run_update.ps1
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("update-" + (Get-Date -Format "yyyyMMdd-HHmm") + ".log")

Write-Host "SREF 资料库更新开始：$(Get-Date -Format 'yyyy-MM-dd HH:mm')" -ForegroundColor Cyan
& python (Join-Path $PSScriptRoot "update_srefs.py") *>&1 | Tee-Object -FilePath $log
$code = $LASTEXITCODE
Write-Host "日志：$log"
exit $code
