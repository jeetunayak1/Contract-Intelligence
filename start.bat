@echo off
REM Contract Intelligence System - Startup Script for Windows
REM This script starts both backend and frontend services

echo Starting Contract Intelligence System...
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo Warning: backend\.env file not found
    echo Creating .env from .env.example...
    copy backend\.env.example backend\.env
    echo Please update backend\.env with your IBM Cloud credentials
    echo.
)

REM Check prerequisites
echo Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed
    exit /b 1
)

echo All prerequisites met
echo.

REM Setup Backend
echo Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo Backend setup complete
echo.

REM Setup Frontend
echo Setting up Frontend...
cd ..\frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
) else (
    echo Node modules already installed
)

echo Frontend setup complete
echo.

REM Create logs directory
cd ..
if not exist "logs" mkdir logs

REM Start services
echo Starting services...
echo.

REM Start backend
echo Starting Backend API on http://localhost:8000...
cd backend
start /B cmd /c "venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ..\logs\backend.log 2>&1"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting Frontend on http://localhost:3000...
cd ..\frontend
start /B cmd /c "npm run dev > ..\logs\frontend.log 2>&1"

cd ..

echo.
echo Application started successfully!
echo.
echo Access points:
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo Logs:
echo    Backend:   logs\backend.log
echo    Frontend:  logs\frontend.log
echo.
echo To stop the application, run: stop.bat
echo.
echo Press any key to exit (services will continue running)...
pause >nul

@REM Made with Bob
