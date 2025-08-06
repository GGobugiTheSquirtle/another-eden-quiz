#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Another Eden 프로젝트 통합 테스트
복원된 기능들의 정상 작동을 검증합니다.
"""

import os
import sys
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def test_project_structure():
    """프로젝트 구조 검증"""
    print("프로젝트 구조 검증 중...")
    
    required_dirs = [
        "01_scraping",
        "02_launcher", 
        "03_apps/quiz",
        "03_apps/roulette",
        "03_apps/shared",
        "04_data/csv",
        "04_data/images",
        "05_archive"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"누락된 디렉토리: {missing_dirs}")
        return False
    
    print("프로젝트 구조 검증 완료")
    return True

def test_scraper_files():
    """스크래퍼 파일 검증"""
    print("스크래퍼 파일 검증 중...")
    
    required_files = [
        "01_scraping/master_scraper.py",
        "01_scraping/image_organizer.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"누락된 파일: {missing_files}")
        return False
    
    # 출시일 기능 확인
    scraper_file = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
    with open(scraper_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "release_date" not in content or "출시일" not in content:
            print("스크래퍼에 출시일 기능이 없습니다.")
            return False
    
    print("스크래퍼 파일 검증 완료")
    return True

def test_app_files():
    """앱 파일 검증"""
    print("🔍 앱 파일 검증 중...")
    
    required_files = [
        "03_apps/quiz/eden_quiz_app.py",
        "03_apps/roulette/streamlit_eden_restructure.py",
        "03_apps/shared/ui_components.py",
        "02_launcher/unified_launcher.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 누락된 파일: {missing_files}")
        return False
    
    # 퀴즈 앱에서 출시일 퀴즈 기능 확인
    quiz_file = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
    with open(quiz_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "guess_release_date" not in content:
            print("❌ 퀴즈 앱에 출시일 퀴즈 기능이 없습니다.")
            return False
    
    print("✅ 앱 파일 검증 완료")
    return True

def test_data_files():
    """데이터 파일 검증"""
    print("🔍 데이터 파일 검증 중...")
    
    csv_dir = PROJECT_ROOT / "04_data" / "csv"
    required_csv_files = [
        "eden_quiz_data.csv",
        "eden_roulette_data.csv",
        "character_personalities.csv",
        "Matching_names.csv"
    ]
    
    existing_files = []
    missing_files = []
    
    for csv_file in required_csv_files:
        file_path = csv_dir / csv_file
        if file_path.exists():
            existing_files.append(csv_file)
            
            # CSV 파일 내용 검증
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                print(f"  📄 {csv_file}: {len(df)}행, {len(df.columns)}컬럼")
                
                # 출시일 컬럼 확인
                if csv_file in ["eden_quiz_data.csv", "eden_roulette_data.csv"]:
                    if '출시일' in df.columns:
                        non_empty_dates = df[df['출시일'].notna() & (df['출시일'] != '')]['출시일'].count()
                        print(f"    ✅ 출시일 데이터: {non_empty_dates}개")
                    else:
                        print(f"    ⚠️ {csv_file}에 출시일 컬럼이 없습니다.")
                        
            except Exception as e:
                print(f"  ❌ {csv_file} 읽기 실패: {e}")
        else:
            missing_files.append(csv_file)
    
    if missing_files:
        print(f"⚠️ 누락된 CSV 파일: {missing_files}")
        print("💡 스크래퍼를 실행하여 데이터 파일을 생성하세요.")
    
    if existing_files:
        print(f"✅ 기존 CSV 파일: {len(existing_files)}개")
        return True
    else:
        print("❌ CSV 파일이 없습니다.")
        return False

def test_image_files():
    """이미지 파일 검증"""
    print("🔍 이미지 파일 검증 중...")
    
    image_dir = PROJECT_ROOT / "04_data" / "images" / "character_art"
    backup_dir = PROJECT_ROOT / "05_archive" / "old_versions" / "icons_for_tierlist_250723"
    organized_dir = PROJECT_ROOT / "04_data" / "images" / "organized_character_art"
    
    # 메인 이미지 디렉토리
    if image_dir.exists():
        main_images = len(list(image_dir.glob("*.png")))
        print(f"  📸 메인 이미지: {main_images}개")
    else:
        print("  ⚠️ 메인 이미지 디렉토리가 없습니다.")
        main_images = 0
    
    # 백업 이미지
    if backup_dir.exists():
        backup_images = len(list(backup_dir.glob("*.png")))
        print(f"  💾 백업 이미지: {backup_images}개")
    else:
        print("  ⚠️ 백업 이미지 디렉토리가 없습니다.")
        backup_images = 0
    
    # 정리된 이미지
    organized_images = 0
    if organized_dir.exists():
        for subdir in organized_dir.iterdir():
            if subdir.is_dir():
                subdir_images = len(list(subdir.glob("*.png")))
                organized_images += subdir_images
                print(f"    🗂️ {subdir.name}: {subdir_images}개")
        print(f"  📁 정리된 이미지: {organized_images}개")
    else:
        print("  ℹ️ 정리된 이미지 디렉토리가 아직 없습니다.")
    
    if main_images > 0 or backup_images > 0:
        print("✅ 이미지 파일 검증 완료")
        return True
    else:
        print("❌ 이미지 파일이 부족합니다.")
        return False

def test_launcher_files():
    """런처 파일 검증"""
    print("🔍 런처 파일 검증 중...")
    
    launcher_files = [
        "main_launcher.py",
        "02_launcher/unified_launcher.py",
        "02_launcher/eden_integrated_launcher.py"
    ]
    
    working_launchers = []
    for launcher in launcher_files:
        file_path = PROJECT_ROOT / launcher
        if file_path.exists():
            working_launchers.append(launcher)
            
            # 새 기능들이 포함되었는지 확인
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if launcher == "main_launcher.py":
                if "통합 런처" in content and "UI/UX" in content:
                    print(f"  ✅ {launcher}: 개선된 기능 포함")
                else:
                    print(f"  ⚠️ {launcher}: 일부 기능 누락")
    
    print(f"✅ 런처 파일: {len(working_launchers)}개 확인")
    return len(working_launchers) > 0

def generate_test_report():
    """테스트 결과 리포트 생성"""
    print("📝 테스트 리포트 생성 중...")
    
    report = {
        "test_date": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "results": {
            "project_structure": test_project_structure(),
            "scraper_files": test_scraper_files(),
            "app_files": test_app_files(),
            "data_files": test_data_files(),
            "image_files": test_image_files(),
            "launcher_files": test_launcher_files()
        }
    }
    
    # CSV 파일 상태 정보 추가
    csv_dir = PROJECT_ROOT / "04_data" / "csv"
    csv_info = {}
    
    if csv_dir.exists():
        for csv_file in csv_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                csv_info[csv_file.name] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "has_release_date": '출시일' in df.columns,
                    "size_kb": round(csv_file.stat().st_size / 1024, 1)
                }
            except Exception:
                csv_info[csv_file.name] = {"error": "읽기 실패"}
    
    report["csv_details"] = csv_info
    
    # 이미지 파일 상태 정보
    image_info = {}
    image_dirs = {
        "main": PROJECT_ROOT / "04_data" / "images" / "character_art",
        "backup": PROJECT_ROOT / "05_archive" / "old_versions" / "icons_for_tierlist_250723",
        "organized": PROJECT_ROOT / "04_data" / "images" / "organized_character_art"
    }
    
    for dir_name, dir_path in image_dirs.items():
        if dir_path.exists():
            if dir_name == "organized":
                total_images = 0
                subdirs = {}
                for subdir in dir_path.iterdir():
                    if subdir.is_dir():
                        subdir_count = len(list(subdir.glob("*.png")))
                        subdirs[subdir.name] = subdir_count
                        total_images += subdir_count
                image_info[dir_name] = {"total": total_images, "subdirs": subdirs}
            else:
                image_info[dir_name] = len(list(dir_path.glob("*.png")))
        else:
            image_info[dir_name] = 0
    
    report["image_details"] = image_info
    
    # 리포트 저장
    report_path = PROJECT_ROOT / "test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 테스트 리포트 저장: {report_path}")
    return report

def main():
    """메인 테스트 실행"""
    print("Another Eden 프로젝트 통합 테스트 시작")
    print("=" * 60)
    
    # 개별 테스트 실행
    report = generate_test_report()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed_tests = sum(1 for result in report["results"].values() if result)
    total_tests = len(report["results"])
    
    print(f"통과: {passed_tests}/{total_tests} 테스트")
    
    for test_name, result in report["results"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    # 복원된 기능 확인
    print("\n🔄 복원된 기능 확인:")
    if report["csv_details"]:
        for csv_name, details in report["csv_details"].items():
            if isinstance(details, dict) and "has_release_date" in details:
                release_status = "✅ 포함됨" if details["has_release_date"] else "❌ 누락됨"
                print(f"  📅 {csv_name} 출시일: {release_status}")
    
    image_details = report["image_details"]
    organized_count = image_details.get("organized", {}).get("total", 0)
    if organized_count > 0:
        print(f"  🗂️ 이미지 자동 정리: ✅ {organized_count}개 파일 정리됨")
    else:
        print(f"  🗂️ 이미지 자동 정리: ⚠️ 아직 실행되지 않음")
    
    # 권장사항
    print("\n💡 권장사항:")
    if not all(report["results"].values()):
        print("  - 실패한 테스트의 원인을 확인하고 해결하세요.")
    
    if not report["csv_details"]:
        print("  - 데이터 스크래퍼를 실행하여 CSV 파일을 생성하세요.")
    
    if organized_count == 0:
        print("  - 이미지 정리 기능을 실행하여 사용자 편의성을 향상시키세요.")
    
    print(f"\n📋 상세 리포트: {PROJECT_ROOT}/test_report.json")
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main()