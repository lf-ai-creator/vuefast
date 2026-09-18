$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot '.runtime\server.json'

if (-not (Test-Path -LiteralPath $statePath)) {
    Write-Host 'No tracked server. For a server started manually, press Ctrl+C in its terminal.'
    return
}
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$serverProcess = Get-Process -Id $state.ProcessId -ErrorAction SilentlyContinue
if ($serverProcess -and $serverProcess.StartTime.ToUniversalTime().Ticks.ToString() -eq $state.StartTicks) {
    # Stop the tracked reloader and its worker; never stop processes by port alone.
    & taskkill.exe /PID $state.ProcessId /T /F
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to stop the server. Process information has been retained for retry.'
    }
    $serverProcess.WaitForExit(5000) | Out-Null
}
Remove-Item -LiteralPath $statePath
Write-Host 'Tracked server stopped.'
