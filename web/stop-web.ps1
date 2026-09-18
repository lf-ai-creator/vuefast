$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot '.runtime\web.json'
if (-not (Test-Path -LiteralPath $statePath)) {
    Write-Host 'No tracked web server. For a manually started server, press Ctrl+C in its terminal.'
    return
}
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$webProcess = Get-Process -Id $state.ProcessId -ErrorAction SilentlyContinue
if ($webProcess -and $webProcess.StartTime.ToUniversalTime().Ticks.ToString() -eq $state.StartTicks) {
    # Only terminate the tracked process tree, including pnpm and Vite.
    & taskkill.exe /PID $state.ProcessId /T /F
    if ($LASTEXITCODE -ne 0) { throw 'Failed to stop web. Process information retained for retry.' }
    $webProcess.WaitForExit(5000) | Out-Null
}
Remove-Item -LiteralPath $statePath
Write-Host 'Tracked web server stopped.'
