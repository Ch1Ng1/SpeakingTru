# Скрипт за лесно стартиране на KIKI
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       KIKI - AI АСИСТЕНТ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Стартиране на KIKI версия..." -ForegroundColor Yellow
Write-Host ""

# Проверка дали .venv съществува
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[ГРЕШКА] Virtual environment не е намерен!" -ForegroundColor Red
    Write-Host "Моля стартирайте: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Натиснете Enter"
    exit 1
}

# Стартиране на програмата
& ".venv\Scripts\python.exe" kiki.py
