# Another Eden 통합 런처 실행 스크립트
# PowerShell 버전

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎮 Another Eden 통합 런처 실행" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "📁 현재 디렉토리: $currentDir" -ForegroundColor Green

# Python 설치 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 설치 확인: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "Python을 설치한 후 다시 시도하세요." -ForegroundColor Yellow
    Read-Host "계속하려면 아무 키나 누르세요"
    exit 1
}

# Streamlit 설치 확인
try {
    python -c "import streamlit" 2>$null
    Write-Host "✅ Streamlit 설치 확인 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Streamlit이 설치되지 않았습니다." -ForegroundColor Yellow
    Write-Host "Streamlit을 설치합니다..." -ForegroundColor Cyan
    pip install streamlit pandas
}

# 필요한 파일 확인
if (-not (Test-Path "eden_integrated_launcher.py")) {
    Write-Host "❌ eden_integrated_launcher.py 파일이 없습니다." -ForegroundColor Red
    Read-Host "계속하려면 아무 키나 누르세요"
    exit 1
}

Write-Host "✅ 모든 준비가 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 런처를 시작합니다..." -ForegroundColor Cyan
Write-Host "📱 브라우저에서 http://localhost:8501 로 접속하세요" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 팁:" -ForegroundColor Magenta
Write-Host "  - Ctrl+C로 런처를 종료할 수 있습니다" -ForegroundColor Gray
Write-Host "  - 브라우저가 자동으로 열리지 않으면 위 URL을 직접 입력하세요" -ForegroundColor Gray
Write-Host ""

# 런처 실행
streamlit run eden_integrated_launcher.py --server.port 8501

Read-Host "계속하려면 아무 키나 누르세요" 