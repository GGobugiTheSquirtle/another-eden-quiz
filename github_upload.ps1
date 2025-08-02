# GitHub 업로드 도구 (PowerShell 버전)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📤 GitHub 업로드 도구" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 확인
$currentDir = Get-Location
Write-Host "📁 현재 디렉토리: $currentDir" -ForegroundColor Green

# Git 설치 확인
try {
    $gitVersion = git --version 2>&1
    Write-Host "✅ Git 설치 확인: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git이 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "Git을 설치한 후 다시 시도하세요." -ForegroundColor Yellow
    Write-Host "https://git-scm.com/downloads" -ForegroundColor Cyan
    Read-Host "계속하려면 아무 키나 누르세요"
    exit 1
}

# Git 저장소 확인
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git 저장소가 초기화되지 않았습니다." -ForegroundColor Red
    Write-Host "setup_git_repo.py를 먼저 실행하세요." -ForegroundColor Yellow
    Read-Host "계속하려면 아무 키나 누르세요"
    exit 1
}

Write-Host "✅ Git 저장소 확인 완료" -ForegroundColor Green
Write-Host ""

# 변경사항 확인
Write-Host "📊 변경사항 확인 중..." -ForegroundColor Cyan
git status --porcelain
Write-Host ""

# 사용자에게 커밋 메시지 입력받기
$commitMsg = Read-Host "💬 커밋 메시지를 입력하세요 (기본: 업데이트)"
if ([string]::IsNullOrEmpty($commitMsg)) {
    $commitMsg = "업데이트"
}

Write-Host ""
Write-Host "📝 커밋 메시지: $commitMsg" -ForegroundColor Yellow
Write-Host ""

# 모든 변경사항 스테이징
Write-Host "📦 변경사항을 스테이징합니다..." -ForegroundColor Cyan
git add .

# 커밋
Write-Host "💾 커밋 중..." -ForegroundColor Cyan
git commit -m $commitMsg

# 원격 저장소 확인
Write-Host "🔍 원격 저장소 확인 중..." -ForegroundColor Cyan
git remote -v

# 푸시
Write-Host "📤 GitHub에 업로드 중..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 업로드 실패! 원격 저장소를 확인하세요." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 해결 방법:" -ForegroundColor Yellow
    Write-Host "  1. GitHub에서 저장소가 생성되었는지 확인" -ForegroundColor Gray
    Write-Host "  2. 원격 URL이 올바른지 확인: git remote -v" -ForegroundColor Gray
    Write-Host "  3. 인증 정보 확인" -ForegroundColor Gray
} else {
    Write-Host "✅ 업로드 완료!" -ForegroundColor Green
    Write-Host "🌐 https://github.com/GGobugiTheSquirtle/another-eden-quiz" -ForegroundColor Cyan
}

Write-Host ""
Read-Host "계속하려면 아무 키나 누르세요" 