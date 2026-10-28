<#
  可选：用本地 HTTP 服务打开资料库（适用于浏览器禁止 file:// 本地脚本的情况）
  用法：powershell -ExecutionPolicy Bypass -File scripts\start_server.ps1
#>
param([int]$Port = 8765)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "资料库地址：http://localhost:$Port" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务"
Start-Process "http://localhost:$Port"
python -m http.server $Port
