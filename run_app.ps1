# PowerShell launcher for AI Troubleshooting Expert System
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  AI-Based Intelligent Troubleshooting Expert System" -ForegroundColor Green
Write-Host "  Starting Streamlit Application..." -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan

$pythonExe = $null

if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
} elseif (Test-Path "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe") {
    $pythonExe = "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
}

if (-not $pythonExe) {
    Write-Error "Python executable not found. Please install Python 3.10+ and add it to PATH."
    Exit 1
}

Write-Host "Using Python at: $pythonExe" -ForegroundColor Gray
& $pythonExe -m streamlit run app.py
