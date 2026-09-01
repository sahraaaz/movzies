@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [Movzies] Virtual environment not found.
    echo Creating .venv...
    python -m venv .venv
    if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"

if not exist ".venv\.deps_installed" (
    echo [Movzies] Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 goto :error
    type nul > ".venv\.deps_installed"
)

echo [Movzies] Starting bot...
python -m app.bot

if errorlevel 1 goto :error
exit /b 0

:error
echo.
echo [Movzies] Startup failed. See the error above.
pause
exit /b 1
