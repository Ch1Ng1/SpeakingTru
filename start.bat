@echo off
chcp 65001 >nul
echo ========================================
echo       KIKI - AI АСИСТЕНТ
echo ========================================
echo.
echo Стартиране на KIKI версия...
echo.

REM Проверка дали .venv съществува
if not exist ".venv\Scripts\python.exe" (
    echo [ГРЕШКА] Virtual environment не е намерен!
    echo Моля стартирайте: python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Стартиране на програмата
".venv\Scripts\python.exe" kiki.py

pause
