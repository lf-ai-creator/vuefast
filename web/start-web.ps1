param(
    [ValidateRange(1, 65535)]
    [int]$Port = 0
)

$ErrorActionPreference = 'Stop'
if (-not $PSBoundParameters.ContainsKey('Port')) {
    $portSetting = Select-String -LiteralPath (Join-Path $PSScriptRoot '.env.development') -Pattern '^VITE_APP_PORT\s*=\s*(\d+)\s*$'
    if (-not $portSetting) { throw 'Set VITE_APP_PORT or pass -Port.' }
    $Port = [int]$portSetting.Matches[0].Groups[1].Value
    if ($Port -lt 1 -or $Port -gt 65535) { throw 'Invalid VITE_APP_PORT.' }
}
$runtimePath = Join-Path $PSScriptRoot '.runtime'
$statePath = Join-Path $runtimePath 'web.json'
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $existing = Get-Process -Id $state.ProcessId -ErrorAction SilentlyContinue
    if ($existing -and $existing.StartTime.ToUniversalTime().Ticks.ToString() -eq $state.StartTicks) {
        Write-Host "Web is already running: http://127.0.0.1:$($state.Port)"
        return
    }
    Remove-Item -LiteralPath $statePath
}
if (-not (Get-Command pnpm.cmd -ErrorAction SilentlyContinue)) {
    throw 'pnpm is not installed or is not on PATH.'
}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'node_modules'))) {
    throw 'Run pnpm install in the web directory first.'
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $Port is already in use."
}
New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
$stderrPath = Join-Path $runtimePath 'stderr.log'
$webProcess = Start-Process -FilePath $env:ComSpec `
    -ArgumentList @('/d', '/c', "pnpm.cmd dev --host 127.0.0.1 --port $Port --strictPort") `
    -WorkingDirectory $PSScriptRoot -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $runtimePath 'stdout.log') `
    -RedirectStandardError $stderrPath -PassThru
@{
    ProcessId = $webProcess.Id
    StartTicks = $webProcess.StartTime.ToUniversalTime().Ticks.ToString()
    Port = $Port
} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    $webProcess.Refresh()
    if ($webProcess.HasExited) { throw "Web exited. Check $stderrPath; run stop-web.ps1 before retrying." }
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -eq 200) {
            Write-Host "Web started: http://127.0.0.1:$Port"
            Write-Host "Logs: $runtimePath"
            return
        }
    } catch {
        # Wait for Vite to become ready.
    }
    Start-Sleep -Milliseconds 500
}
throw "Startup was not confirmed. Check $stderrPath; use stop-web.ps1 to stop the process."
