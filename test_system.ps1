# Test System for KIKI AI Assistant
# encoding: utf-8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  KIKI SYSTEM TEST" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = & "C:/xampp/htdocs/SpeakingTru/.venv/Scripts/python.exe" --version
    Write-Host "   OK: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# 2. Check Libraries
Write-Host "`n2. Checking Python libraries..." -ForegroundColor Yellow
$libs = @("speech_recognition", "gtts", "pygame", "wikipedia", "requests", "bs4")
foreach ($lib in $libs) {
    $import = $lib
    if ($lib -eq "speech_recognition") { $import = "speech_recognition" }
    if ($lib -eq "bs4") { $import = "bs4" }
    
    $result = & "C:/xampp/htdocs/SpeakingTru/.venv/Scripts/python.exe" -c "import $import; print('OK')" 2>&1
    if ($result -like "*OK*") {
        Write-Host "   OK: $lib" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: $lib missing!" -ForegroundColor Red
    }
}

# 3. Check Files
Write-Host "`n3. Checking files..." -ForegroundColor Yellow
$files = @("ai_friend_super.py", "requirements.txt", "start.bat", "start.ps1")
foreach ($file in $files) {
    if (Test-Path "c:\xampp\htdocs\SpeakingTru\$file") {
        Write-Host "   OK: $file" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: $file missing!" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start KIKI:" -ForegroundColor Yellow
Write-Host "   Run: .\start.ps1 or start.bat" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Ollama is NOT required - KIKI uses built-in functions!" -ForegroundColor Cyan
Write-Host ""
