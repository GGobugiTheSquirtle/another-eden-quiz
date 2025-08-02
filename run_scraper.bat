@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🔧 Another Eden 데이터 스크래퍼 실행
echo ========================================
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"
echo 📁 현재 디렉토리: %CD%

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python을 설치한 후 다시 시도하세요.
    pause
    exit /b 1
)

REM 필요한 라이브러리 설치 확인
python -c "import requests, beautifulsoup4, pandas" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 필요한 라이브러리가 설치되지 않았습니다.
    echo 라이브러리를 설치합니다...
    pip install requests beautifulsoup4 pandas openpyxl
)

REM 필요한 파일 확인
if not exist "eden_personality_scraper.py" (
    echo ❌ eden_personality_scraper.py 파일이 없습니다.
    pause
    exit /b 1
)

echo ✅ 모든 준비가 완료되었습니다!
echo.
echo 🔧 스크래퍼를 시작합니다...
echo.
echo 💡 옵션:
echo   1. GUI 모드 (기본): python eden_personality_scraper.py
echo   2. 통합 모드: python eden_personality_scraper.py --integrated
echo.
echo 📝 데이터 수집이 완료되면 generated_data 폴더에 결과가 저장됩니다.
echo.

REM 스크래퍼 실행 (GUI 모드)
python eden_personality_scraper.py

pause 