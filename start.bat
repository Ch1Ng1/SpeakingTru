@echo off
echo ========================================
echo       KIKI - AI АСИСТЕНТ
echo ========================================
echo.
echo Стартиране на KIKI...
echo.

REM Активиране на virtual environment
call .venv\Scripts\activate.bat

REM Стартиране на програмата
python ai_friend_super.py

pause
