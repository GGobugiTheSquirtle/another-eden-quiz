@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🎮 Another Eden 통합 런처 실행
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
if not exist "eden_integrated_launcher.py" (
    echo ❌ eden_integrated_launcher.py 파일이 없습니다.
    pause
    exit /b 1
)

echo ✅ 모든 준비가 완료되었습니다!
echo.
echo 🚀 런처를 시작합니다...
echo 📱 브라우저에서 http://localhost:8501 로 접속하세요
echo.
echo 💡 팁:
echo   - Ctrl+C로 런처를 종료할 수 있습니다
echo   - 브라우저가 자동으로 열리지 않으면 위 URL을 직접 입력하세요
echo.

REM 런처 실행
streamlit run eden_integrated_launcher.py --server.port 8501

pause 