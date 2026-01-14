# Test System for Gurko AI Assistant
# encoding: utf-8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  GURKO SYSTEM TEST" -ForegroundColor Green
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

# 3. Check Ollama
Write-Host "`n3. Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   OK: Ollama is running" -ForegroundColor Green
    
    $tags = ($response.Content | ConvertFrom-Json).models
    $hasGemma = $false
    foreach ($tag in $tags) {
        if ($tag.name -like "*gemma:2b*") {
            $hasGemma = $true
            break
        }
    }
    
    if ($hasGemma) {
        Write-Host "   OK: Model gemma:2b is available" -ForegroundColor Green
    } else {
        Write-Host "   WARNING: Model gemma:2b not found" -ForegroundColor Yellow
        Write-Host "   Run: ollama pull gemma:2b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ERROR: Ollama is NOT running!" -ForegroundColor Red
    Write-Host "   Run: ollama serve" -ForegroundColor Yellow
}

# 4. Check Files
Write-Host "`n4. Checking files..." -ForegroundColor Yellow
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
Write-Host "To start Gurko:" -ForegroundColor Yellow
Write-Host "   1. Make sure Ollama is running: ollama serve" -ForegroundColor White
Write-Host "   2. Run: .\start.ps1 or start.bat" -ForegroundColor White
Write-Host ""
