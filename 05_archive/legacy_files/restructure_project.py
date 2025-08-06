#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로젝트 구조 모듈화 및 정리 스크립트
스크래핑/런쳐/앱알맹이로 깔끔하게 구조화
"""

import os
import shutil
from pathlib import Path

def create_modular_structure():
    """모듈화된 프로젝트 구조 생성"""
    print("🏗️ 프로젝트 구조 모듈화 시작")
    print("=" * 50)
    
    base_dir = Path.cwd()
    
    # 새로운 폴더 구조 생성
    folders_to_create = [
        "01_scraping",           # 스크래핑 관련
        "02_launcher",           # 런쳐 관련
        "03_apps",               # 앱 알맹이
        "03_apps/quiz",          # 퀴즈 앱
        "03_apps/roulette",      # 룰렛 앱
        "03_apps/shared",        # 공통 모듈
        "04_data",               # 데이터 파일들
        "04_data/csv",           # CSV 데이터
        "04_data/images",        # 이미지 데이터
        "05_archive",            # 아카이브 (기존 archive 내용 + 불필요 파일)
        "05_archive/old_scripts", # 구버전 스크립트들
        "05_archive/backup",     # 백업 파일들
        "05_archive/temp",       # 임시 파일들
    ]
    
    for folder in folders_to_create:
        folder_path = base_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 폴더 생성: {folder}")
    
    return base_dir

def organize_scraping_files(base_dir):
    """스크래핑 관련 파일 정리"""
    print("\n📡 스크래핑 파일 정리")
    print("-" * 30)
    
    scraping_files = [
        "eden_personality_scraper.py",
        "scrape_with_korean_names.py", 
        "enhanced_scraper.py",
        "extract_character_personalities.py",
        "scraper_config.ini",
    ]
    
    scraping_dir = base_dir / "01_scraping"
    
    for file in scraping_files:
        src = base_dir / file
        if src.exists():
            dst = scraping_dir / file
            shutil.move(str(src), str(dst))
            print(f"📦 이동: {file} → 01_scraping/")

def organize_launcher_files(base_dir):
    """런쳐 관련 파일 정리"""
    print("\n🚀 런쳐 파일 정리")
    print("-" * 30)
    
    launcher_files = [
        "eden_integrated_launcher.py",
        "run_launcher.bat",
        "run_launcher.ps1",
        "quick_start.bat",
    ]
    
    launcher_dir = base_dir / "02_launcher"
    
    for file in launcher_files:
        src = base_dir / file
        if src.exists():
            dst = launcher_dir / file
            shutil.move(str(src), str(dst))
            print(f"🚀 이동: {file} → 02_launcher/")

def organize_app_files(base_dir):
    """앱 관련 파일 정리"""
    print("\n🎮 앱 파일 정리")
    print("-" * 30)
    
    # 퀴즈 앱 파일
    quiz_files = [
        "eden_quiz_app.py",
    ]
    
    # 룰렛 앱 파일  
    roulette_files = [
        "streamlit_eden_restructure.py",
    ]
    
    # 공통 모듈 파일
    shared_files = [
        "fix_image_character_matching.py",
        "unified_image_matching.py",
        "batch_rename_images.py",
        "rename_images_to_korean.py",
    ]
    
    # 퀴즈 앱 이동
    quiz_dir = base_dir / "03_apps" / "quiz"
    for file in quiz_files:
        src = base_dir / file
        if src.exists():
            dst = quiz_dir / file
            shutil.move(str(src), str(dst))
            print(f"🎯 이동: {file} → 03_apps/quiz/")
    
    # 룰렛 앱 이동
    roulette_dir = base_dir / "03_apps" / "roulette"
    for file in roulette_files:
        src = base_dir / file
        if src.exists():
            dst = roulette_dir / file
            shutil.move(str(src), str(dst))
            print(f"🎰 이동: {file} → 03_apps/roulette/")
    
    # 공통 모듈 이동
    shared_dir = base_dir / "03_apps" / "shared"
    for file in shared_files:
        src = base_dir / file
        if src.exists():
            dst = shared_dir / file
            shutil.move(str(src), str(dst))
            print(f"🔧 이동: {file} → 03_apps/shared/")

def organize_data_files(base_dir):
    """데이터 파일 정리"""
    print("\n📊 데이터 파일 정리")
    print("-" * 30)
    
    # CSV 데이터 파일
    csv_files = [
        "eden_quiz_data.csv",
        "eden_quiz_data_fixed.csv",
        "eden_roulette_data.csv", 
        "eden_roulette_data_with_personalities.csv",
        "character_personalities.csv",
        "personality_matching.csv",
        "Matching_names.csv",
    ]
    
    csv_dir = base_dir / "04_data" / "csv"
    for file in csv_files:
        src = base_dir / file
        if src.exists():
            dst = csv_dir / file
            shutil.move(str(src), str(dst))
            print(f"📋 이동: {file} → 04_data/csv/")
    
    # 이미지 폴더 이동
    images_src = base_dir / "character_art"
    images_dst = base_dir / "04_data" / "images" / "character_art"
    if images_src.exists():
        if images_dst.exists():
            shutil.rmtree(images_dst)
        shutil.move(str(images_src), str(images_dst))
        print(f"🖼️ 이동: character_art/ → 04_data/images/")

def organize_archive_files(base_dir):
    """아카이브 파일 정리"""
    print("\n📦 아카이브 파일 정리")
    print("-" * 30)
    
    # 분석/개발용 스크립트들 (아카이브)
    analysis_files = [
        "analyze_matching_issue.py",
        "app_improvement_plan.py",
        "quiz_app_benchmarking.py",
        "pipeline_analysis_report.py",
        "final_validation.py",
    ]
    
    # 정리/설정 스크립트들 (아카이브)
    cleanup_files = [
        "project_cleanup.py",
        "project_cleanup_final.py", 
        "execute_cleanup.py",
        "setup_git_repo.py",
    ]
    
    # 백업/임시 파일들
    backup_files = [
        "another_eden_characters_detailed.xlsx",
        "another_eden_characters_detailed (1).xlsx",
    ]
    
    # Git 업로드 스크립트들
    git_files = [
        "github_upload.bat",
        "github_upload.ps1",
    ]
    
    archive_dir = base_dir / "05_archive"
    
    # 분석 스크립트들
    old_scripts_dir = archive_dir / "old_scripts"
    for file in analysis_files + cleanup_files + git_files:
        src = base_dir / file
        if src.exists():
            dst = old_scripts_dir / file
            shutil.move(str(src), str(dst))
            print(f"📜 이동: {file} → 05_archive/old_scripts/")
    
    # 백업 파일들
    backup_dir = archive_dir / "backup"
    for file in backup_files:
        src = base_dir / file
        if src.exists():
            dst = backup_dir / file
            shutil.move(str(src), str(dst))
            print(f"💾 이동: {file} → 05_archive/backup/")
    
    # 기존 백업 폴더들 이동
    existing_backup_dirs = ["backup_20250803", "generated_data"]
    for dir_name in existing_backup_dirs:
        src = base_dir / dir_name
        if src.exists():
            dst = backup_dir / dir_name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(src), str(dst))
            print(f"📁 이동: {dir_name}/ → 05_archive/backup/")
    
    # 기존 archive 폴더 내용 병합
    existing_archive = base_dir / "archive"
    if existing_archive.exists():
        for item in existing_archive.iterdir():
            dst = archive_dir / item.name
            if dst.exists():
                if item.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            shutil.move(str(item), str(dst))
            print(f"📦 병합: archive/{item.name} → 05_archive/")
        existing_archive.rmdir()

def create_main_launcher(base_dir):
    """메인 런쳐 파일 생성"""
    print("\n🎯 메인 런쳐 생성")
    print("-" * 30)
    
    launcher_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Another Eden 퀴즈 & 룰렛 메인 런쳐
모듈화된 프로젝트 구조의 통합 실행기
"""

import sys
import os
from pathlib import Path
import subprocess

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def run_quiz_app():
    """퀴즈 앱 실행"""
    quiz_path = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
    if quiz_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(quiz_path)])
    else:
        print("❌ 퀴즈 앱을 찾을 수 없습니다.")

def run_roulette_app():
    """룰렛 앱 실행"""
    roulette_path = PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    if roulette_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(roulette_path)])
    else:
        print("❌ 룰렛 앱을 찾을 수 없습니다.")

def run_scraper():
    """스크래퍼 실행"""
    scraper_path = PROJECT_ROOT / "01_scraping" / "eden_personality_scraper.py"
    if scraper_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, str(scraper_path)])
    else:
        print("❌ 스크래퍼를 찾을 수 없습니다.")

def main():
    """메인 메뉴"""
    print("🎮 Another Eden 퀴즈 & 룰렛")
    print("=" * 40)
    print("1. 🎯 퀴즈 앱 실행")
    print("2. 🎰 룰렛 앱 실행") 
    print("3. 📡 데이터 스크래퍼 실행")
    print("4. 🚪 종료")
    print("-" * 40)
    
    while True:
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == "1":
            print("🎯 퀴즈 앱을 시작합니다...")
            run_quiz_app()
            break
        elif choice == "2":
            print("🎰 룰렛 앱을 시작합니다...")
            run_roulette_app()
            break
        elif choice == "3":
            print("📡 스크래퍼를 시작합니다...")
            run_scraper()
            break
        elif choice == "4":
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-4 중에서 선택해주세요.")

if __name__ == "__main__":
    main()
'''
    
    launcher_file = base_dir / "main_launcher.py"
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print(f"✅ 메인 런쳐 생성: main_launcher.py")

def create_readme_update(base_dir):
    """README 업데이트"""
    print("\n📖 README 업데이트")
    print("-" * 30)
    
    readme_content = '''# 🎮 Another Eden 퀴즈 & 룰렛

캐릭터 데이터를 활용한 인터랙티브 퀴즈 및 룰렛 게임

## 📁 프로젝트 구조

```
📦 Another Eden Quiz & Roulette
├── 📂 01_scraping/              # 데이터 스크래핑
│   ├── eden_personality_scraper.py
│   ├── scrape_with_korean_names.py
│   └── scraper_config.ini
├── 📂 02_launcher/              # 실행 런쳐
│   ├── eden_integrated_launcher.py
│   ├── run_launcher.bat
│   └── run_launcher.ps1
├── 📂 03_apps/                  # 앱 알맹이
│   ├── 📂 quiz/                 # 퀴즈 앱
│   │   └── eden_quiz_app.py
│   ├── 📂 roulette/             # 룰렛 앱
│   │   └── streamlit_eden_restructure.py
│   └── 📂 shared/               # 공통 모듈
│       ├── fix_image_character_matching.py
│       └── unified_image_matching.py
├── 📂 04_data/                  # 데이터
│   ├── 📂 csv/                  # CSV 데이터
│   │   ├── eden_quiz_data_fixed.csv
│   │   └── Matching_names.csv
│   └── 📂 images/               # 이미지 데이터
│       └── character_art/
├── 📂 05_archive/               # 아카이브
│   ├── 📂 old_scripts/          # 구버전 스크립트
│   ├── 📂 backup/               # 백업 파일
│   └── 📂 temp/                 # 임시 파일
├── main_launcher.py             # 🎯 메인 실행기
├── requirements.txt
└── README.md
```

## 🚀 빠른 시작

### 방법 1: 메인 런쳐 사용 (권장)
```bash
python main_launcher.py
```

### 방법 2: 직접 실행
```bash
# 퀴즈 앱
streamlit run 03_apps/quiz/eden_quiz_app.py

# 룰렛 앱  
streamlit run 03_apps/roulette/streamlit_eden_restructure.py

# 스크래퍼
python 01_scraping/eden_personality_scraper.py
```

## 🎯 주요 기능

### 퀴즈 앱
- 5가지 퀴즈 모드 (이름, 희귀도, 속성, 무기, 실루엣)
- 실시간 점수 추적
- 한글 캐릭터명 지원
- 이미지 힌트 제공

### 룰렛 앱
- 캐릭터 필터링 기능
- 카드 형태 결과 표시
- 다양한 속성별 분류
- 깔끔한 UI 디자인

### 스크래퍼
- Another Eden Wiki 데이터 수집
- 이미지 자동 다운로드
- 한글 이름 매핑
- 엑셀/CSV 자동 생성

## 📋 요구사항

```bash
pip install -r requirements.txt
```

## 🔧 개발자 정보

- 데이터 출처: [Another Eden Wiki](https://anothereden.wiki/)
- 모든 캐릭터 이미지 저작권: © WFS
'''
    
    readme_file = base_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ README 업데이트 완료")

def main():
    """메인 실행 함수"""
    print("🏗️ Another Eden 프로젝트 구조 모듈화")
    print("=" * 60)
    
    try:
        base_dir = create_modular_structure()
        organize_scraping_files(base_dir)
        organize_launcher_files(base_dir)
        organize_app_files(base_dir)
        organize_data_files(base_dir)
        organize_archive_files(base_dir)
        create_main_launcher(base_dir)
        create_readme_update(base_dir)
        
        print("\n🎉 프로젝트 구조 모듈화 완료!")
        print("=" * 60)
        print("📁 새로운 구조:")
        print("  01_scraping/    - 스크래핑 관련")
        print("  02_launcher/    - 런쳐 관련") 
        print("  03_apps/        - 앱 알맹이")
        print("  04_data/        - 데이터 파일")
        print("  05_archive/     - 아카이브")
        print("  main_launcher.py - 메인 실행기")
        print("\n🚀 사용법: python main_launcher.py")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 모든 작업이 완료되었습니다!")
    else:
        print("\n❌ 작업 중 오류가 발생했습니다.")
