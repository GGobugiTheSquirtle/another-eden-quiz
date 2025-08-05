@echo off
chcp 65001 >nul
title Another Eden 프로젝트 - 빠른 시작

:menu
cls
echo.
echo ========================================
echo 🎮 Another Eden 프로젝트 - 빠른 시작
echo ========================================
echo.
echo 📋 사용 가능한 옵션:
echo.
echo 1. 🚀 통합 런처 실행 (추천)
echo    - 퀴즈쇼 + 룰렛 모두 포함
echo    - http://localhost:8501
echo.
echo 2. 🎯 퀴즈쇼 앱만 실행
echo    - 독립적인 퀴즈 게임
echo    - http://localhost:8502
echo.
echo 3. 🎰 룰렛 앱만 실행
echo    - 독립적인 룰렛 게임
echo    - http://localhost:8503
echo.
echo 4. 🔧 데이터 스크래퍼 실행
echo    - 캐릭터 데이터 수집
echo    - GUI 모드로 실행
echo.
echo 5. 📤 GitHub 업로드
echo    - 변경사항을 GitHub에 업로드
echo.
echo 6. 📖 도움말 보기
echo.
echo 0. ❌ 종료
echo.
echo ========================================
echo.

set /p choice="🎯 원하는 옵션을 선택하세요 (0-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 통합 런처를 시작합니다...
    call run_launcher.bat
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 🎯 퀴즈쇼 앱을 시작합니다...
    call run_quiz_app.bat
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo 🎰 룰렛 앱을 시작합니다...
    call run_roulette_app.bat
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo 🔧 데이터 스크래퍼를 시작합니다...
    call run_scraper.bat
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo 📤 GitHub 업로드를 시작합니다...
    call github_upload.bat
    goto menu
)

if "%choice%"=="6" (
    echo.
    echo 📖 도움말
    echo ========================================
    echo.
    echo 🎮 게임 관련:
    echo   - 통합 런처: 모든 게임을 한 곳에서 플레이
    echo   - 퀴즈쇼: 5가지 모드의 캐릭터 퀴즈
    echo   - 룰렛: 캐릭터 필터링 및 랜덤 뽑기
    echo.
    echo 🔧 개발 도구:
    echo   - 스크래퍼: Another Eden 위키에서 데이터 수집
    echo   - GitHub 업로드: 변경사항을 클라우드에 저장
    echo.
    echo 📱 배포:
    echo   - Streamlit Community Cloud 배포 가능
    echo   - GitHub: https://github.com/GGobugiTheSquirtle/another-eden-quiz
    echo.
    echo 💡 팁:
    echo   - 처음 사용자는 '1. 통합 런처'를 추천합니다
    echo   - 데이터가 없으면 '4. 스크래퍼'를 먼저 실행하세요
    echo   - 변경사항은 '5. GitHub 업로드'로 저장하세요
    echo.
    pause
    goto menu
)

if "%choice%"=="0" (
    echo.
    echo 👋 안녕히 가세요!
    exit /b 0
)

echo.
echo ❌ 잘못된 선택입니다. 0-6 중에서 선택하세요.
pause
goto menu 