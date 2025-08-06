"""
🗂️ Another Eden 프로젝트 정리 도구
불필요한 파일들을 아카이브로 이동하고 깔끔한 리포지토리 구조를 만듭니다.
"""

import os
import shutil
import json
from pathlib import Path
import time

def create_directory_structure():
    """필요한 디렉토리 구조 생성"""
    directories = [
        "archive",
        "archive/legacy_scrapers",
        "archive/old_versions", 
        "archive/temp_files",
        "docs",
        ".github/workflows"
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def get_file_categories():
    """파일 카테고리 정의"""
    return {
        "keep_main": [
            "eden_integrated_launcher.py",
            "eden_quiz_app.py", 
            "eden_personality_scraper.py",
            "streamlit_eden_restructure.py",
            "README.md",
            "LICENSE",
            ".gitignore"
        ],
        "keep_data": [
            "Matching_names.csv",
            "eden_roulette_data.csv",
            "another_eden_characters_detailed.xlsx"
        ],
        "keep_directories": [
            "character_art",
            "audio"
        ],
        "archive_legacy": [
            "another_eden_gui_scraper copy.py",
            "another_eden_gui_scraper copy 2.py",
            "eden_data_preprocess_gui_with personality.py",
            "통합적용.PY",
            "hexagon_maker.py"
        ],
        "archive_temp": [
            "Matching_names copy.csv",
            "structure_analysis.csv",
            "scraper_config.ini",
            "git.txt",
            "files-to-keep.txt",
            "run_process.bat",
            "run_streamlit.bat",
            "settings.json",
            "GEMINI.md",
            "plan.md"
        ],
        "archive_cache": [
            "__pycache__",
            ".cursor",
            ".devcontainer",
            "icons_for_tierlist_250723"
        ]
    }

def move_files_to_archive():
    """파일들을 적절한 아카이브 폴더로 이동"""
    categories = get_file_categories()
    moved_files = []
    
    # Legacy scrapers
    for file_name in categories["archive_legacy"]:
        if os.path.exists(file_name):
            dest = f"archive/legacy_scrapers/{file_name}"
            shutil.move(file_name, dest)
            moved_files.append(f"{file_name} → {dest}")
            print(f"📦 Moved to legacy: {file_name}")
    
    # Temporary files
    for file_name in categories["archive_temp"]:
        if os.path.exists(file_name):
            dest = f"archive/temp_files/{file_name}"
            shutil.move(file_name, dest)
            moved_files.append(f"{file_name} → {dest}")
            print(f"📁 Moved to temp: {file_name}")
    
    # Cache directories
    for dir_name in categories["archive_cache"]:
        if os.path.exists(dir_name):
            dest = f"archive/old_versions/{dir_name}"
            shutil.move(dir_name, dest)
            moved_files.append(f"{dir_name}/ → {dest}/")
            print(f"🗂️ Moved directory: {dir_name}")
    
    return moved_files

def create_gitignore():
    """Git 무시 파일 생성/업데이트"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
scraper_config.ini
*.xlsx
*.csv
character_art/
audio/
archive/

# Streamlit
.streamlit/

# Logs
*.log
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ Created/Updated .gitignore")

def create_github_workflow():
    """GitHub Actions 워크플로우 생성"""
    workflow_content = """name: Deploy to Streamlit Community Cloud

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v3
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install streamlit pandas openpyxl requests beautifulsoup4
        
    - name: Test Streamlit apps
      run: |
        # Test if apps can be imported without errors
        python -c "import eden_integrated_launcher"
        python -c "import eden_quiz_app"
        echo "✅ All apps imported successfully"
"""
    
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/deploy.yml', 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    print("✅ Created GitHub Actions workflow")

def create_requirements_txt():
    """requirements.txt 파일 생성"""
    requirements = """streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_project_summary():
    """프로젝트 요약 문서 생성"""
    summary = {
        "project_name": "Another Eden Quiz & Roulette System",
        "description": "Interactive quiz games and character roulette for Another Eden",
        "version": "2.0.0",
        "created_date": time.strftime("%Y-%m-%d"),
        "main_apps": {
            "eden_integrated_launcher.py": "Main control center and dashboard",
            "eden_quiz_app.py": "Interactive quiz game with 5 modes",
            "eden_personality_scraper.py": "Enhanced data scraper with personalities",
            "streamlit_eden_restructure.py": "Original roulette and filtering system"
        },
        "data_files": {
            "Matching_names.csv": "English ↔ Korean character name mappings",
            "eden_roulette_data.csv": "Processed character data for apps",
            "character_art/": "Character images and icons"
        },
        "deployment": {
            "local": "streamlit run [app_name].py",
            "cloud": "Upload to Streamlit Community Cloud",
            "ports": {
                "launcher": 8501,
                "quiz": 8502, 
                "roulette": 8503
            }
        }
    }
    
    with open('docs/project_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("✅ Created project summary")

def main():
    """메인 정리 작업 실행"""
    print("🚀 Starting Another Eden project cleanup...")
    print("=" * 50)
    
    # 1. 디렉토리 구조 생성
    create_directory_structure()
    print()
    
    # 2. 파일 이동
    print("📦 Moving files to archive...")
    moved_files = move_files_to_archive()
    print(f"✅ Moved {len(moved_files)} files/directories")
    print()
    
    # 3. Git 관련 파일 생성
    print("🔧 Creating Git repository files...")
    create_gitignore()
    create_github_workflow()
    create_requirements_txt()
    print()
    
    # 4. 문서 생성
    print("📚 Creating documentation...")
    create_project_summary()
    print()
    
    # 5. 최종 구조 표시
    print("📁 Final project structure:")
    print("=" * 30)
    
    current_files = []
    for item in os.listdir('.'):
        if not item.startswith('.') and item != 'archive':
            current_files.append(item)
    
    for item in sorted(current_files):
        if os.path.isdir(item):
            print(f"📁 {item}/")
        else:
            print(f"📄 {item}")
    
    print("\n🎉 Project cleanup completed!")
    print(f"📦 Archived items are in the 'archive/' folder")
    print(f"🚀 Ready for Git repository creation!")

if __name__ == "__main__":
    main()