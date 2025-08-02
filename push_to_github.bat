@echo off
echo 🚀 Pushing Another Eden Quiz project to GitHub...
echo.
echo Repository: https://github.com/GGobugiTheSquirtle/another-eden-quiz
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 Successfully pushed to GitHub!
    echo 📊 Repository URL: https://github.com/GGobugiTheSquirtle/another-eden-quiz
    echo.
    echo 🚀 Next steps:
    echo 1. Visit your repository on GitHub
    echo 2. Deploy to Streamlit Community Cloud: https://share.streamlit.io/
    echo 3. Select main file: eden_integrated_launcher.py
) else (
    echo.
    echo ❌ Push failed! Please check:
    echo 1. Repository exists on GitHub
    echo 2. Repository name is exactly: another-eden-quiz
    echo 3. You have push permissions
)

pause