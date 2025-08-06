#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Another Eden 데이터 문제 통합 해결 스크립트
이미지 파일명 정리 + CSV 경로 업데이트 + 데이터 검증
"""

import os
import shutil
import pandas as pd
from pathlib import Path
import re
import unicodedata

def fix_image_filenames():
    """이미지 파일명에서 &width=80 파라미터 제거"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    if not IMAGE_DIR.exists():
        print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {IMAGE_DIR}")
        return False
    
    print(f"🔧 이미지 파일명 정리 시작: {IMAGE_DIR}")
    
    # 백업 디렉토리 생성
    backup_dir = IMAGE_DIR.parent / "character_art_backup"
    backup_dir.mkdir(exist_ok=True)
    
    fixed_count = 0
    error_count = 0
    
    for file_path in IMAGE_DIR.iterdir():
        if file_path.is_file():
            old_name = file_path.name
            
            # &width=80 파라미터 제거
            if "&width=80" in old_name:
                new_name = old_name.replace("&width=80", "")
                
                # 파일명 정리 (특수문자 제거)
                new_name = re.sub(r'[<>:"/\\|?*]', '', new_name)
                new_name = new_name.strip()
                
                if new_name != old_name:
                    try:
                        # 백업 생성
                        backup_path = backup_dir / old_name
                        shutil.copy2(file_path, backup_path)
                        
                        # 파일명 변경
                        new_path = file_path.parent / new_name
                        file_path.rename(new_path)
                        
                        print(f"✅ {old_name} → {new_name}")
                        fixed_count += 1
                        
                    except Exception as e:
                        print(f"❌ {old_name} 처리 실패: {e}")
                        error_count += 1
    
    print(f"📊 이미지 정리 완료: {fixed_count}개 수정, {error_count}개 오류")
    return fixed_count > 0

def normalize_name(name):
    """이름 정규화"""
    if pd.isna(name) or not name:
        return ""
    return unicodedata.normalize("NFKC", str(name)).strip()

def find_matching_image(char_name, eng_name, image_dir):
    """캐릭터 이름과 매칭되는 이미지 파일 찾기"""
    if not image_dir.exists():
        return None
    
    # 검색할 이름들
    search_names = []
    
    if char_name:
        search_names.append(normalize_name(char_name))
        # 괄호 제거 버전
        clean_kor = char_name.replace("(", "").replace(")", "").strip()
        search_names.append(clean_kor)
        # 공백 제거 버전
        clean_kor_no_space = char_name.replace(" ", "").replace("(", "").replace(")", "")
        search_names.append(clean_kor_no_space)
    
    if eng_name:
        search_names.append(normalize_name(eng_name))
        # 괄호 제거 버전
        clean_eng = eng_name.replace("(", "").replace(")", "").strip()
        search_names.append(clean_eng)
        # 공백 제거 버전
        clean_eng_no_space = eng_name.replace(" ", "").replace("(", "").replace(")", "")
        search_names.append(clean_eng_no_space)
    
    # 이미지 파일 검색
    for file_path in image_dir.iterdir():
        if file_path.is_file():
            file_name = file_path.stem  # 확장자 제외한 파일명
            
            # 정확한 매칭
            for search_name in search_names:
                if search_name and search_name.lower() == file_name.lower():
                    return str(file_path.relative_to(image_dir.parent.parent))
            
            # 부분 매칭 (한글명이 영문 파일명에 포함되는 경우)
            for search_name in search_names:
                if search_name and search_name.lower() in file_name.lower():
                    return str(file_path.relative_to(image_dir.parent.parent))
                # 영문명이 한글 파일명에 포함되는 경우
                if search_name and file_name.lower() in search_name.lower():
                    return str(file_path.relative_to(image_dir.parent.parent))
    
    return None

def update_csv_image_paths():
    """CSV 파일의 이미지 경로 업데이트"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    if not CSV_DIR.exists():
        print(f"❌ CSV 디렉토리를 찾을 수 없습니다: {CSV_DIR}")
        return False
    
    print(f"📋 CSV 이미지 경로 업데이트 시작")
    
    # 처리할 CSV 파일들
    csv_files = [
        ("eden_quiz_data_fixed.csv", "캐릭터아이콘경로"),
        ("eden_roulette_data.csv", "image_path"),
        ("eden_roulette_data_with_personalities.csv", "image_path")
    ]
    
    total_updated = 0
    
    for csv_file, image_column in csv_files:
        csv_path = CSV_DIR / csv_file
        
        if not csv_path.exists():
            print(f"⚠️ {csv_file} 파일이 없습니다.")
            continue
        
        print(f"\n📄 {csv_file} 처리 중...")
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            if image_column not in df.columns:
                df[image_column] = ""
            
            updated_count = 0
            
            for idx, row in df.iterrows():
                char_name = row.get('캐릭터명', row.get('korean_name', ''))
                eng_name = row.get('영문명', row.get('english_name', ''))
                
                current_path = row.get(image_column, '')
                
                # 이미 경로가 있으면 건너뛰기
                if current_path and str(current_path).strip():
                    continue
                
                image_path = find_matching_image(char_name, eng_name, IMAGE_DIR)
                
                if image_path:
                    df.at[idx, image_column] = image_path
                    updated_count += 1
                    print(f"  ✅ {char_name or eng_name}: {image_path}")
            
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  📊 {updated_count}개 경로 업데이트 완료")
            total_updated += updated_count
            
        except Exception as e:
            print(f"❌ {csv_file} 처리 실패: {e}")
    
    print(f"📊 CSV 업데이트 완료: 총 {total_updated}개 경로 수정")
    return total_updated > 0

def verify_data_integrity():
    """데이터 무결성 검증"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    print(f"\n🔍 데이터 무결성 검증")
    
    # 이미지 파일 수 확인
    if IMAGE_DIR.exists():
        image_count = len([f for f in IMAGE_DIR.iterdir() if f.is_file()])
        print(f"📸 이미지 파일: {image_count}개")
    else:
        print("❌ 이미지 디렉토리가 없습니다")
    
    # CSV 파일 확인
    csv_files = [
        "eden_quiz_data_fixed.csv",
        "eden_roulette_data.csv",
        "eden_roulette_data_with_personalities.csv"
    ]
    
    for csv_file in csv_files:
        csv_path = CSV_DIR / csv_file
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                image_paths = df.get('캐릭터아이콘경로', df.get('image_path', pd.Series()))
                valid_paths = image_paths[image_paths.notna() & (image_paths != '')]
                print(f"📄 {csv_file}: {len(df)}개 캐릭터, {len(valid_paths)}개 이미지 경로")
            except Exception as e:
                print(f"❌ {csv_file} 읽기 실패: {e}")
        else:
            print(f"⚠️ {csv_file} 파일이 없습니다")

def main():
    """메인 실행 함수"""
    print("Another Eden 데이터 문제 통합 해결")
    print("=" * 50)
    
    # 1. 이미지 파일명 정리
    print("\n1️⃣ 이미지 파일명 정리 중...")
    image_fixed = fix_image_filenames()
    
    # 2. CSV 이미지 경로 업데이트
    print("\n2️⃣ CSV 이미지 경로 업데이트 중...")
    csv_updated = update_csv_image_paths()
    
    # 3. 데이터 무결성 검증
    print("\n3️⃣ 데이터 무결성 검증 중...")
    verify_data_integrity()
    
    print("\n" + "=" * 50)
    if image_fixed or csv_updated:
        print("데이터 문제 해결 완료!")
        print("이제 앱을 실행해보세요.")
    else:
        print("수정할 데이터가 없습니다.")
        print("이제 앱을 실행해보세요.")

if __name__ == "__main__":
    main() 