@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 📤 GitHub 업로드 도구
echo ========================================
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"
echo 📁 현재 디렉토리: %CD%

REM Git 설치 확인
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git이 설치되지 않았습니다.
    echo Git을 설치한 후 다시 시도하세요.
    echo https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Git 저장소 확인
if not exist ".git" (
    echo ❌ Git 저장소가 초기화되지 않았습니다.
    echo setup_git_repo.py를 먼저 실행하세요.
    pause
    exit /b 1
)

echo ✅ Git 저장소 확인 완료
echo.

REM 변경사항 확인
echo 📊 변경사항 확인 중...
git status --porcelain
echo.

REM 사용자에게 커밋 메시지 입력받기
set /p commit_msg="💬 커밋 메시지를 입력하세요 (기본: 업데이트): "
if "%commit_msg%"=="" set commit_msg="업데이트"

echo.
echo 📝 커밋 메시지: %commit_msg%
echo.

REM 모든 변경사항 스테이징
echo 📦 변경사항을 스테이징합니다...
git add .

REM 커밋
echo 💾 커밋 중...
git commit -m "%commit_msg%"

REM 원격 저장소 확인
echo 🔍 원격 저장소 확인 중...
git remote -v

REM 푸시
echo 📤 GitHub에 업로드 중...
git push origin main

if errorlevel 1 (
    echo ❌ 업로드 실패! 원격 저장소를 확인하세요.
    echo.
    echo 💡 해결 방법:
    echo   1. GitHub에서 저장소가 생성되었는지 확인
    echo   2. 원격 URL이 올바른지 확인: git remote -v
    echo   3. 인증 정보 확인
) else (
    echo ✅ 업로드 완료!
    echo 🌐 https://github.com/GGobugiTheSquirtle/another-eden-quiz
)

echo.
pause 