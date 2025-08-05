"""
🔧 Git 리포지토리 설정 도구
프로젝트를 깃헙에 업로드하기 위한 모든 설정을 자동으로 수행합니다.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """명령어 실행 및 결과 반환"""
    try:
        print(f"🔧 {description}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False

def check_git_installed():
    """Git이 설치되어 있는지 확인"""
    return run_command("git --version", "Checking Git installation")

def initialize_git_repo():
    """Git 리포지토리 초기화"""
    if os.path.exists('.git'):
        print("📁 Git repository already exists")
        return True
    return run_command("git init", "Initializing Git repository")

def create_initial_commit():
    """초기 커밋 생성"""
    commands = [
        ("git add .", "Adding all files to staging"),
        ("git commit -m \"Initial commit: Another Eden Quiz & Roulette System\"", "Creating initial commit")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def create_github_repo_instructions():
    """GitHub 리포지토리 생성 안내"""
    instructions = """
🐙 GitHub 리포지토리 생성 안내
================================

1. GitHub에서 새 리포지토리 생성:
   - 리포지토리 이름: another-eden-quiz
   - 설명: Interactive quiz games and character roulette for Another Eden
   - Public/Private: 원하는 설정 선택
   - README, .gitignore, license: 생성하지 않음 (이미 존재)

2. 생성 후 다음 명령어로 연결:
   
   git remote add origin https://github.com/[사용자명]/another-eden-quiz.git
   git branch -M main
   git push -u origin main

3. Streamlit Community Cloud 배포:
   - https://share.streamlit.io/ 방문
   - GitHub 리포지토리 연결
   - 앱 파일 선택:
     * eden_integrated_launcher.py (메인 런처)
     * eden_quiz_app.py (퀴즈 앱)
     * streamlit_eden_restructure.py (룰렛 앱)

4. 필요한 경우 다음 파일들을 리포지토리에 추가:
   - Matching_names.csv (캐릭터명 매핑)
   - character_art/ 폴더 (이미지 파일들)
   - audio/ 폴더 (사운드 파일들)

⚠️  주의사항:
- 큰 이미지/오디오 파일들은 Git LFS 사용 고려
- 민감한 데이터가 있는지 .gitignore 확인
- 첫 번째 배포 시 데이터 파일 부족으로 에러 날 수 있음
"""
    
    print(instructions)
    
    # 파일로도 저장
    with open('GITHUB_SETUP.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    print("✅ GitHub setup instructions saved to GITHUB_SETUP.md")

def create_streamlit_config():
    """Streamlit 설정 파일 생성"""
    config_dir = Path('.streamlit')
    config_dir.mkdir(exist_ok=True)
    
    config_content = """[general]
dataFrameSerialization = "legacy"

[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    with open(config_dir / 'config.toml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ Created Streamlit configuration")

def check_project_files():
    """프로젝트 필수 파일들이 있는지 확인"""
    required_files = [
        'eden_integrated_launcher.py',
        'eden_quiz_app.py', 
        'eden_personality_scraper.py',
        'streamlit_eden_restructure.py',
        'README.md',
        'requirements.txt',
        '.gitignore'
    ]
    
    print("📋 Checking required files...")
    missing_files = []
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} (missing)")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files!")
        return False
    
    print("\n🎉 All required files present!")
    return True

def create_deployment_guide():
    """배포 가이드 생성"""
    guide_content = """# 🚀 Deployment Guide

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Applications
```bash
# Main launcher (port 8501)
streamlit run eden_integrated_launcher.py

# Quiz app (port 8502) 
streamlit run eden_quiz_app.py --server.port 8502

# Roulette app (port 8503)
streamlit run streamlit_eden_restructure.py --server.port 8503
```

## Streamlit Community Cloud

### 1. Prerequisites
- GitHub repository with all files
- Streamlit Community Cloud account
- Required data files uploaded

### 2. Deployment Steps
1. Visit https://share.streamlit.io/
2. Connect your GitHub account
3. Select repository: `another-eden-quiz`
4. Choose main file: `eden_integrated_launcher.py`
5. Deploy!

### 3. Multiple App Deployment
Deploy each app separately:
- **Main Launcher**: `eden_integrated_launcher.py`
- **Quiz Game**: `eden_quiz_app.py` 
- **Roulette**: `streamlit_eden_restructure.py`

## Data Requirements

### Essential Files
- `Matching_names.csv` - Character name mappings
- `character_art/icons/` - Character images
- `character_art/elements_equipment/` - Equipment icons

### Optional Files  
- `audio/` - Sound effects for quiz
- `eden_roulette_data.csv` - Pre-processed data

## Troubleshooting

### Common Issues
1. **Missing CSV files**: Run the scraper first
2. **Image not loading**: Check file paths and extensions
3. **Port conflicts**: Use different port numbers
4. **Memory issues**: Reduce image sizes or use Git LFS

### Performance Optimization
- Compress images before upload
- Use @st.cache_data for data loading
- Minimize file sizes where possible
"""
    
    with open('DEPLOYMENT.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print("✅ Created deployment guide")

def main():
    """메인 Git 설정 작업"""
    print("🔧 Setting up Git repository for Another Eden project...")
    print("=" * 60)
    
    # 1. Git 확인
    if not check_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        return
    
    # 2. 프로젝트 파일 확인
    if not check_project_files():
        print("❌ Please ensure all required files are present.")
        return
    
    # 3. Streamlit 설정
    create_streamlit_config()
    
    # 4. 배포 가이드 생성
    create_deployment_guide()
    
    # 5. Git 리포지토리 초기화
    if initialize_git_repo():
        print("✅ Git repository initialized")
    
    # 6. 초기 커밋
    if create_initial_commit():
        print("✅ Initial commit created")
    
    # 7. GitHub 안내
    create_github_repo_instructions()
    
    print("\n🎉 Git repository setup completed!")
    print("📖 Check GITHUB_SETUP.md for next steps")

if __name__ == "__main__":
    main()