$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$webPath = Join-Path $projectRoot "web"
$apiUrl = "http://127.0.0.1:8000"
$apiStartedHere = $false

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Virtual environment not found. Create .venv and install requirements.txt first."
}

function Get-PortOwnerId {
    param([int]$Port)
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $listener) {
        return $null
    }
    return [int]$listener.OwningProcess
}

function Test-CurrentApi {
    try {
        $health = Invoke-RestMethod "$apiUrl/health" -TimeoutSec 2
        $status = Invoke-RestMethod "$apiUrl/project-status" -TimeoutSec 2
        return (
            $health.status -eq "ok" -and
            $health.version -eq "2.0.0" -and
            $health.phases -eq 2 -and
            $status.phase1.status -eq "complete" -and
            $status.phase2.status -eq "complete"
        )
    }
    catch {
        return $false
    }
}

function Stop-ProjectApiOnPort {
    param([int]$Port)
    $ownerId = Get-PortOwnerId -Port $Port
    if ($null -eq $ownerId) {
        return
    }

    $projectProcessIds = [System.Collections.Generic.List[int]]::new()
    $currentId = $ownerId
    while ($currentId -gt 0) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $currentId" -ErrorAction SilentlyContinue
        if ($null -eq $process) {
            break
        }
        $commandLine = [string]$process.CommandLine
        if ($commandLine.IndexOf($projectRoot, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
            break
        }
        $projectProcessIds.Add([int]$process.ProcessId)
        $currentId = [int]$process.ParentProcessId
    }

    if ($projectProcessIds.Count -eq 0) {
        throw "Port $Port is used by another application. Close it or change the API port before starting the project."
    }

    foreach ($processId in $projectProcessIds) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }

    for ($attempt = 0; $attempt -lt 30; $attempt += 1) {
        if ($null -eq (Get-PortOwnerId -Port $Port)) {
            return
        }
        Start-Sleep -Milliseconds 100
    }
    throw "The obsolete project API on port $Port could not be stopped."
}

if (-not (Test-CurrentApi)) {
    if ($null -ne (Get-PortOwnerId -Port 8000)) {
        Write-Host "Replacing an incompatible Warehouse Intelligence API..." -ForegroundColor Yellow
        Stop-ProjectApiOnPort -Port 8000
    }

    $logPrefix = Join-Path $env:TEMP "csai301-api-$PID"
    $apiProcess = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput "$logPrefix.out.log" `
        -RedirectStandardError "$logPrefix.err.log" `
        -PassThru
    $apiStartedHere = $true

    for ($attempt = 0; $attempt -lt 80; $attempt += 1) {
        if (Test-CurrentApi) {
            break
        }
        if ($apiProcess.HasExited) {
            $details = Get-Content "$logPrefix.err.log" -Raw -ErrorAction SilentlyContinue
            throw "The API failed to start. $details"
        }
        Start-Sleep -Milliseconds 125
    }

    if (-not (Test-CurrentApi)) {
        Stop-ProjectApiOnPort -Port 8000
        throw "The API started but did not pass its compatibility check."
    }
}

Write-Host "Warehouse API ready. Starting the web laboratory..." -ForegroundColor Green
try {
    Push-Location $webPath
    $env:VITE_API_URL = $apiUrl
    npm run dev
}
finally {
    Pop-Location
    if ($apiStartedHere) {
        Stop-ProjectApiOnPort -Port 8000
    }
}
