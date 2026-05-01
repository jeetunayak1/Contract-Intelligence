@echo off
REM Contract Intelligence System - Stop Script for Windows
REM This script stops both backend and frontend services

echo Stopping Contract Intelligence System...
echo.

REM Kill uvicorn processes (backend)
echo Stopping Backend...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Backend stopped
) else (
    echo No backend process found
)

REM Kill node processes (frontend)
echo Stopping Frontend...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Frontend stopped
) else (
    echo No frontend process found
)

REM Alternative: Kill all node and python processes (more aggressive)
REM Uncomment if the above doesn't work
REM taskkill /F /IM node.exe >nul 2>&1
REM taskkill /F /IM python.exe >nul 2>&1

echo.
echo Application stopped successfully
pause

@REM Made with Bob
