$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

function Invoke-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Verification command failed with exit code $LASTEXITCODE."
    }
}

Push-Location $projectRoot
try {
    Invoke-Checked { & $pythonPath -m pytest }
    Invoke-Checked { & $pythonPath -m ruff check . }
    Invoke-Checked { & $pythonPath -m ruff format --check . }
    Push-Location (Join-Path $projectRoot "web")
    try {
        Invoke-Checked { npm run lint }
        Invoke-Checked { npm run build }
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
