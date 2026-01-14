# Скрипт за лесно стартиране на Гурко
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       ГУРКО - AI АСИСТЕНТ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Стартиране на Гурко Супер версия..." -ForegroundColor Yellow
Write-Host ""

# Проверка дали Ollama е стартиран
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ Ollama е стартиран" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama НЕ е стартиран!" -ForegroundColor Red
    Write-Host "Моля стартирайте Ollama с: ollama serve" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Натиснете Enter за да продължите или Ctrl+C за да спрете"
}

# Стартиране на програмата
& "C:/xampp/htdocs/SpeakingTru/.venv/Scripts/python.exe" ai_friend_super.py
