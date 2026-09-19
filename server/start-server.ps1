param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8000,

    [bool]$HotReload = $true
)

$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$runtimePath = Join-Path $PSScriptRoot '.runtime'
$statePath = Join-Path $runtimePath 'server.json'

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Missing .venv. Create the virtual environment and install dependencies first.'
}
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $existing = Get-Process -Id $state.ProcessId -ErrorAction SilentlyContinue
    if ($existing -and $existing.StartTime.ToUniversalTime().Ticks.ToString() -eq $state.StartTicks) {
        Write-Host "Server is already running (PID $($state.ProcessId), port $($state.Port))."
        return
    }
    Remove-Item -LiteralPath $statePath
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $Port is already in use."
}

New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
$stdoutPath = Join-Path $runtimePath 'stdout.log'
$stderrPath = Join-Path $runtimePath 'stderr.log'
$uvicornArguments = @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', $Port)
if ($HotReload) {
    $uvicornArguments += '--reload'
}
$serverProcess = Start-Process -FilePath $pythonPath `
    -ArgumentList $uvicornArguments `
    -WorkingDirectory $PSScriptRoot -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru

@{
    ProcessId = $serverProcess.Id
    StartTicks = $serverProcess.StartTime.ToUniversalTime().Ticks.ToString()
    Port = $Port
    HotReload = $HotReload
} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    $serverProcess.Refresh()
    if ($serverProcess.HasExited) {
        throw "Server exited. Check $stderrPath; run stop-server.ps1 before retrying."
    }
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/docs" -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -eq 200) {
            Write-Host "Server started: http://127.0.0.1:$Port/docs"
            Write-Host "Hot reload: $HotReload"
            Write-Host "Logs: $runtimePath"
            return
        }
    } catch {
        # The worker may still be importing modules.
    }
    Start-Sleep -Milliseconds 500
}
throw "Startup was not confirmed. Check $stderrPath; use stop-server.ps1 to stop the process."
