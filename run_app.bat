@echo off
setlocal

echo =====================================================================
echo   AI-Based Intelligent Troubleshooting Expert System
echo   Launching Streamlit Application...
echo =====================================================================

REM Detect Python
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
echo Please ensure Python is installed and added to your system PATH.
pause
exit /b 1

:RUN
echo Using Python at: %PYTHON_EXE%
"%PYTHON_EXE%" -m streamlit run app.py
pause
