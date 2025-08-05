@echo off
chcp 65001 >nul
title Another Eden 앱 실행기

echo.
echo 🎮 Another Eden 앱 실행기
echo ==============================
echo 1. 퀴즈 앱
echo 2. 룰렛 앱
echo 3. 종료
echo ------------------------------
echo.

:menu
set /p choice="선택하세요 (1-3): "

if "%choice%"=="1" goto quiz
if "%choice%"=="2" goto roulette
if "%choice%"=="3" goto exit
echo ❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.
echo.
goto menu

:quiz
echo 🎯 퀴즈 앱을 시작합니다...
echo 🌐 브라우저에서 http://localhost:8501 을 열어주세요
echo.
python -m streamlit run "03_apps\quiz\eden_quiz_app.py"
goto exit

:roulette
echo 🎰 룰렛 앱을 시작합니다...
echo 🌐 브라우저에서 http://localhost:8501 을 열어주세요
echo.
python -m streamlit run "03_apps\roulette\streamlit_eden_restructure.py"
goto exit

:exit
echo.
echo �� 프로그램을 종료합니다.
pause 