@echo off
setlocal

echo =====================================================================
echo   AI-Based Intelligent Troubleshooting Expert System
echo   Running Comprehensive Automated Test Suite (Pytest)...
echo =====================================================================

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=python
    goto RUN
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_EXE=py
    goto RUN
)

if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    goto RUN
)

echo ERROR: Python executable could not be automatically located.
pause
exit /b 1

:RUN
echo Using Python at: %PYTHON_EXE%
"%PYTHON_EXE%" -m pytest tests/ -v
pause
