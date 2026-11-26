@echo off
setlocal
cd /d "%~dp0"

rem If VoltPulse is already running, open it without starting another server.
powershell -NoProfile -Command "try { $r = Invoke-WebRequest 'http://127.0.0.1:3000/' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200 -and $r.Content -match 'VoltPulse') { exit 0 } } catch {}; exit 1"
if not errorlevel 1 (
    start "" "http://localhost:3000/"
    exit /b 0
)

echo Starting VoltPulse at http://localhost:3000/
echo Keep this window open while using the project.
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe src\web\server.py
) else (
    python src\web\server.py
)
if errorlevel 1 (
    echo Server could not start. Check that Node.js or Python is installed and port 3000 is free.
    pause
    exit /b 1
)
