@echo off
REM =====================================================================
REM Rooted - one-click local start (Windows)
REM
REM Usage:  run.bat  (double-click it, or run from cmd/PowerShell)
REM
REM First-time setup you still must do yourself before this works fully:
REM   - Create a Supabase project and run database\schema.sql in its SQL editor
REM   - Put your Supabase connection string into backend\.env (DATABASE_URL)
REM =====================================================================

echo Rooted - starting up...
echo.

cd /d "%~dp0backend"

if not exist .env (
    copy .env.example .env >nul
    echo Created backend\.env from .env.example.
    echo Edit backend\.env and set DATABASE_URL to your Supabase connection string,
    echo then re-run run.bat.
    echo.
)

if not exist venv (
    echo Creating Python virtual environment ^(first run only^)...
    python -m venv venv
)

call venv\Scripts\activate.bat
echo Checking backend dependencies...
pip install -q -r requirements.txt

echo Starting backend on http://localhost:8001 ...
start "Rooted Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"

cd /d "%~dp0frontend"

if not exist .env (
    copy .env.example .env >nul
)

if not exist node_modules (
    echo Installing frontend dependencies ^(first run only, this can take a minute^)...
    call npm install
)

echo Starting frontend on http://localhost:5173 ...
start "Rooted Frontend" cmd /k "npm run dev"

echo.
echo ------------------------------------------------
echo Rooted is running:
echo    App:      http://localhost:5173
echo    API docs: http://localhost:8001/api/docs
echo.
echo    First login (seeded super admin): ADMIN001
echo ------------------------------------------------
echo.
echo Two new windows opened for the backend and frontend.
echo Close those windows to stop Rooted.
pause
