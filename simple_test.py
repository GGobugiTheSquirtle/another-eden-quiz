#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.resolve()

def simple_test():
    print("Another Eden 프로젝트 간단 테스트")
    print("=" * 50)
    
    # 1. 핵심 파일 존재 확인
    core_files = [
        "01_scraping/master_scraper.py",
        "01_scraping/image_organizer.py", 
        "03_apps/quiz/eden_quiz_app.py",
        "03_apps/shared/ui_components.py",
        "02_launcher/unified_launcher.py"
    ]
    
    print("1. 핵심 파일 확인:")
    for file_path in core_files:
        exists = (PROJECT_ROOT / file_path).exists()
        status = "OK" if exists else "MISSING"
        print(f"   {status}: {file_path}")
    
    # 2. 데이터 파일 확인
    print("\n2. 데이터 파일 확인:")
    csv_dir = PROJECT_ROOT / "04_data" / "csv"
    if csv_dir.exists():
        csv_files = list(csv_dir.glob("*.csv"))
        print(f"   CSV 파일: {len(csv_files)}개")
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                has_release = '출시일' in df.columns
                release_status = " (출시일 포함)" if has_release else ""
                print(f"     {csv_file.name}: {len(df)}행{release_status}")
            except Exception as e:
                print(f"     {csv_file.name}: 읽기 오류")
    else:
        print("   CSV 디렉토리 없음")
    
    # 3. 이미지 파일 확인
    print("\n3. 이미지 파일 확인:")
    image_dirs = {
        "메인": PROJECT_ROOT / "04_data" / "images" / "character_art",
        "백업": PROJECT_ROOT / "05_archive" / "old_versions" / "icons_for_tierlist_250723"
    }
    
    for name, path in image_dirs.items():
        if path.exists():
            count = len(list(path.glob("*.png")))
            print(f"   {name}: {count}개 이미지")
        else:
            print(f"   {name}: 디렉토리 없음")
    
    # 4. 개선사항 확인
    print("\n4. 개선사항 확인:")
    
    # 출시일 기능
    scraper_file = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
    if scraper_file.exists():
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_release_feature = "release_date" in content
            print(f"   출시일 기능: {'OK' if has_release_feature else 'MISSING'}")
    
    # 이미지 정리 기능
    organizer_file = PROJECT_ROOT / "01_scraping" / "image_organizer.py"
    has_organizer = organizer_file.exists()
    print(f"   이미지 정리: {'OK' if has_organizer else 'MISSING'}")
    
    # 새 퀴즈 모드
    quiz_file = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
    if quiz_file.exists():
        with open(quiz_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_release_quiz = "guess_release_date" in content
            print(f"   출시일 퀴즈: {'OK' if has_release_quiz else 'MISSING'}")
    
    # UI 개선
    ui_file = PROJECT_ROOT / "03_apps" / "shared" / "ui_components.py"
    has_ui_components = ui_file.exists()
    print(f"   UI 컴포넌트: {'OK' if has_ui_components else 'MISSING'}")
    
    print("\n" + "=" * 50)
    print("테스트 완료!")

if __name__ == "__main__":
    simple_test()