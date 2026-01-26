@echo off
chcp 65001 >nul
echo ========================================
echo       ГУРКО - AI АСИСТЕНТ
echo ========================================
echo.
echo Стартиране на Гурко Супер версия...
echo.

REM Проверка дали .venv съществува
if not exist ".venv\Scripts\python.exe" (
    echo [ГРЕШКА] Virtual environment не е намерен!
    echo Моля стартирайте: python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Проверка дали Ollama е стартиран
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Ollama НЕ е стартиран!
    echo Моля стартирайте Ollama с: ollama serve
    echo.
    pause
)

REM Стартиране на програмата с абсолютен път
".venv\Scripts\python.exe" ai_friend_super.py

pause
