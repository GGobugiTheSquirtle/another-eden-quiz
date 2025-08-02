@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🎰 Another Eden 룰렛 앱 실행
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

REM Streamlit 설치 확인
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Streamlit이 설치되지 않았습니다.
    echo Streamlit을 설치합니다...
    pip install streamlit pandas
)

REM 필요한 파일 확인
if not exist "streamlit_eden_restructure.py" (
    echo ❌ streamlit_eden_restructure.py 파일이 없습니다.
    pause
    exit /b 1
)

echo ✅ 모든 준비가 완료되었습니다!
echo.
echo 🎰 룰렛 앱을 시작합니다...
echo 📱 브라우저에서 http://localhost:8503 로 접속하세요
echo.
echo 💡 팁:
echo   - Ctrl+C로 앱을 종료할 수 있습니다
echo   - 브라우저가 자동으로 열리지 않으면 위 URL을 직접 입력하세요
echo.

REM 룰렛 앱 실행
streamlit run streamlit_eden_restructure.py --server.port 8503

pause 