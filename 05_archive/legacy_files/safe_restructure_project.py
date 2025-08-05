#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 프로젝트 구조 모듈화 스크립트
파일 이동 대신 복사로 안전하게 구조화
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
        "05_archive",            # 아카이브
        "05_archive/old_scripts", # 구버전 스크립트들
        "05_archive/backup",     # 백업 파일들
    ]
    
    for folder in folders_to_create:
        folder_path = base_dir / folder
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 폴더 생성: {folder}")
        except Exception as e:
            print(f"⚠️ 폴더 생성 실패: {folder} - {e}")
    
    return base_dir

def safe_copy_files(file_mapping, base_dir):
    """파일들을 안전하게 복사"""
    for src_file, dst_folder in file_mapping.items():
        try:
            src_path = base_dir / src_file
            dst_dir = base_dir / dst_folder
            dst_path = dst_dir / src_file
            
            if src_path.exists() and not dst_path.exists():
                shutil.copy2(str(src_path), str(dst_path))
                print(f"📋 복사: {src_file} → {dst_folder}/")
            elif dst_path.exists():
                print(f"⚠️ 이미 존재: {dst_folder}/{src_file}")
            else:
                print(f"❌ 파일 없음: {src_file}")
        except Exception as e:
            print(f"❌ 복사 실패: {src_file} - {e}")

def organize_project_files(base_dir):
    """프로젝트 파일들을 카테고리별로 정리"""
    print("\n📦 파일 분류 및 복사")
    print("-" * 30)
    
    # 파일 매핑 (원본파일명 : 대상폴더)
    file_mapping = {
        # 스크래핑 관련
        "eden_personality_scraper.py": "01_scraping",
        "scrape_with_korean_names.py": "01_scraping", 
        "enhanced_scraper.py": "01_scraping",
        "extract_character_personalities.py": "01_scraping",
        "scraper_config.ini": "01_scraping",
        
        # 런쳐 관련
        "eden_integrated_launcher.py": "02_launcher",
        "run_launcher.bat": "02_launcher",
        "run_launcher.ps1": "02_launcher",
        "quick_start.bat": "02_launcher",
        
        # 퀴즈 앱
        "eden_quiz_app.py": "03_apps/quiz",
        
        # 룰렛 앱
        "streamlit_eden_restructure.py": "03_apps/roulette",
        
        # 공통 모듈
        "fix_image_character_matching.py": "03_apps/shared",
        "unified_image_matching.py": "03_apps/shared",
        "batch_rename_images.py": "03_apps/shared",
        "rename_images_to_korean.py": "03_apps/shared",
        
        # CSV 데이터
        "eden_quiz_data.csv": "04_data/csv",
        "eden_quiz_data_fixed.csv": "04_data/csv",
        "eden_roulette_data.csv": "04_data/csv",
        "eden_roulette_data_with_personalities.csv": "04_data/csv",
        "character_personalities.csv": "04_data/csv",
        "personality_matching.csv": "04_data/csv",
        "Matching_names.csv": "04_data/csv",
        
        # 아카이브 - 분석 스크립트
        "analyze_matching_issue.py": "05_archive/old_scripts",
        "app_improvement_plan.py": "05_archive/old_scripts",
        "quiz_app_benchmarking.py": "05_archive/old_scripts",
        "pipeline_analysis_report.py": "05_archive/old_scripts",
        "final_validation.py": "05_archive/old_scripts",
        "project_cleanup.py": "05_archive/old_scripts",
        "project_cleanup_final.py": "05_archive/old_scripts",
        "execute_cleanup.py": "05_archive/old_scripts",
        "setup_git_repo.py": "05_archive/old_scripts",
        "github_upload.bat": "05_archive/old_scripts",
        "github_upload.ps1": "05_archive/old_scripts",
        
        # 아카이브 - 백업 파일
        "another_eden_characters_detailed.xlsx": "05_archive/backup",
        "another_eden_characters_detailed (1).xlsx": "05_archive/backup",
    }
    
    safe_copy_files(file_mapping, base_dir)

def copy_image_directory(base_dir):
    """이미지 디렉토리 복사"""
    print("\n🖼️ 이미지 디렉토리 복사")
    print("-" * 30)
    
    try:
        src_dir = base_dir / "character_art"
        dst_dir = base_dir / "04_data" / "images" / "character_art"
        
        if src_dir.exists():
            if dst_dir.exists():
                print(f"⚠️ 이미지 디렉토리 이미 존재: {dst_dir}")
            else:
                shutil.copytree(str(src_dir), str(dst_dir))
                print(f"✅ 이미지 디렉토리 복사 완료: character_art → 04_data/images/")
        else:
            print(f"❌ 원본 이미지 디렉토리 없음: {src_dir}")
    except Exception as e:
        print(f"❌ 이미지 디렉토리 복사 실패: {e}")

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
        print(f"   경로: {quiz_path}")

def run_roulette_app():
    """룰렛 앱 실행"""
    roulette_path = PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    if roulette_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(roulette_path)])
    else:
        print("❌ 룰렛 앱을 찾을 수 없습니다.")
        print(f"   경로: {roulette_path}")

def run_scraper():
    """스크래퍼 실행"""
    scraper_path = PROJECT_ROOT / "01_scraping" / "eden_personality_scraper.py"
    if scraper_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, str(scraper_path)])
    else:
        print("❌ 스크래퍼를 찾을 수 없습니다.")
        print(f"   경로: {scraper_path}")

def show_project_structure():
    """프로젝트 구조 표시"""
    print("📁 프로젝트 구조:")
    print("├── 01_scraping/     - 데이터 스크래핑")
    print("├── 02_launcher/     - 실행 런쳐")
    print("├── 03_apps/         - 앱 알맹이")
    print("│   ├── quiz/        - 퀴즈 앱")
    print("│   ├── roulette/    - 룰렛 앱")
    print("│   └── shared/      - 공통 모듈")
    print("├── 04_data/         - 데이터 파일")
    print("│   ├── csv/         - CSV 데이터")
    print("│   └── images/      - 이미지 데이터")
    print("└── 05_archive/      - 아카이브")

def main():
    """메인 메뉴"""
    print("🎮 Another Eden 퀴즈 & 룰렛")
    print("=" * 40)
    print("1. 🎯 퀴즈 앱 실행")
    print("2. 🎰 룰렛 앱 실행") 
    print("3. 📡 데이터 스크래퍼 실행")
    print("4. 📁 프로젝트 구조 보기")
    print("5. 🚪 종료")
    print("-" * 40)
    
    while True:
        choice = input("선택하세요 (1-5): ").strip()
        
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
            show_project_structure()
            print()
        elif choice == "5":
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택해주세요.")

if __name__ == "__main__":
    main()
'''
    
    try:
        launcher_file = base_dir / "main_launcher.py"
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        print(f"✅ 메인 런쳐 생성: main_launcher.py")
    except Exception as e:
        print(f"❌ 메인 런쳐 생성 실패: {e}")

def create_structure_guide(base_dir):
    """구조 가이드 파일 생성"""
    print("\n📖 구조 가이드 생성")
    print("-" * 30)
    
    guide_content = '''# 🏗️ 프로젝트 구조 가이드

## 📁 새로운 모듈화 구조

```
📦 Another Eden Quiz & Roulette
├── 📂 01_scraping/              # 데이터 스크래핑
│   ├── eden_personality_scraper.py    # 메인 스크래퍼
│   ├── scrape_with_korean_names.py    # 한글명 스크래퍼
│   ├── enhanced_scraper.py             # 향상된 스크래퍼
│   └── scraper_config.ini              # 스크래퍼 설정
├── 📂 02_launcher/              # 실행 런쳐
│   ├── eden_integrated_launcher.py    # 통합 런쳐
│   ├── run_launcher.bat               # Windows 배치
│   └── run_launcher.ps1               # PowerShell
├── 📂 03_apps/                  # 앱 알맹이
│   ├── 📂 quiz/                 # 퀴즈 앱
│   │   └── eden_quiz_app.py
│   ├── 📂 roulette/             # 룰렛 앱
│   │   └── streamlit_eden_restructure.py
│   └── 📂 shared/               # 공통 모듈
│       ├── fix_image_character_matching.py
│       ├── unified_image_matching.py
│       └── batch_rename_images.py
├── 📂 04_data/                  # 데이터
│   ├── 📂 csv/                  # CSV 데이터
│   │   ├── eden_quiz_data_fixed.csv   # 수정된 퀴즈 데이터
│   │   ├── Matching_names.csv          # 이름 매핑
│   │   └── character_personalities.csv # 성격 데이터
│   └── 📂 images/               # 이미지 데이터
│       └── character_art/              # 캐릭터 이미지
├── 📂 05_archive/               # 아카이브
│   ├── 📂 old_scripts/          # 구버전 스크립트
│   └── 📂 backup/               # 백업 파일
├── main_launcher.py             # 🎯 메인 실행기
├── requirements.txt             # 의존성
└── README.md                    # 프로젝트 문서
```

## 🚀 사용법

### 메인 런쳐 사용 (권장)
```bash
python main_launcher.py
```

### 개별 실행
```bash
# 퀴즈 앱
streamlit run 03_apps/quiz/eden_quiz_app.py

# 룰렛 앱  
streamlit run 03_apps/roulette/streamlit_eden_restructure.py

# 스크래퍼
python 01_scraping/eden_personality_scraper.py
```

## 🔧 개발자 노트

- 기존 파일들은 그대로 유지됩니다
- 새로운 구조는 복사본으로 생성됩니다
- 필요시 기존 파일들을 삭제하여 정리할 수 있습니다

## 📋 다음 단계

1. 새로운 구조에서 앱들이 정상 작동하는지 확인
2. 경로 참조 문제가 있다면 수정
3. 기존 파일들 정리 (선택사항)
'''
    
    try:
        guide_file = base_dir / "STRUCTURE_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"✅ 구조 가이드 생성: STRUCTURE_GUIDE.md")
    except Exception as e:
        print(f"❌ 구조 가이드 생성 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🏗️ Another Eden 프로젝트 안전 구조화")
    print("=" * 60)
    
    try:
        base_dir = create_modular_structure()
        organize_project_files(base_dir)
        copy_image_directory(base_dir)
        create_main_launcher(base_dir)
        create_structure_guide(base_dir)
        
        print("\n🎉 프로젝트 구조 모듈화 완료!")
        print("=" * 60)
        print("📁 새로운 구조가 생성되었습니다:")
        print("  01_scraping/    - 스크래핑 관련")
        print("  02_launcher/    - 런쳐 관련") 
        print("  03_apps/        - 앱 알맹이")
        print("  04_data/        - 데이터 파일")
        print("  05_archive/     - 아카이브")
        print("  main_launcher.py - 메인 실행기")
        print("\n🚀 사용법: python main_launcher.py")
        print("📖 자세한 내용: STRUCTURE_GUIDE.md 참조")
        
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
