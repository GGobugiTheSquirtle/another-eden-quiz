#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Another Eden 이미지 매칭 검증 스크립트
실제 이미지 파일과 CSV 데이터의 매칭 상태를 정확히 확인
"""

import pandas as pd
from pathlib import Path
import unicodedata

def normalize_name(name):
    """이름 정규화"""
    if pd.isna(name) or not name:
        return ""
    return unicodedata.normalize("NFKC", str(name)).strip()

def verify_image_matching():
    """이미지 매칭 상태 검증"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    print("🔍 Another Eden 이미지 매칭 검증")
    print("=" * 50)
    
    # 이미지 파일 목록
    image_files = []
    if IMAGE_DIR.exists():
        for file_path in IMAGE_DIR.iterdir():
            if file_path.is_file():
                image_files.append(file_path.stem)  # 확장자 제외
    
    print(f"📸 이미지 파일: {len(image_files)}개")
    print("첫 10개 이미지:", image_files[:10])
    
    # CSV 파일 검증
    csv_files = [
        ("eden_quiz_data_fixed.csv", "캐릭터아이콘경로"),
        ("eden_roulette_data.csv", "image_path"),
        ("eden_roulette_data_with_personalities.csv", "image_path")
    ]
    
    for csv_file, image_column in csv_files:
        csv_path = CSV_DIR / csv_file
        
        if not csv_path.exists():
            print(f"❌ {csv_file} 파일이 없습니다.")
            continue
        
        print(f"\n📄 {csv_file} 검증 중...")
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            if image_column not in df.columns:
                print(f"❌ {image_column} 컬럼이 없습니다.")
                continue
            
            # 이미지 경로가 있는 행들
            valid_paths = df[df[image_column].notna() & (df[image_column] != '')]
            missing_paths = df[df[image_column].isna() | (df[image_column] == '')]
            
            print(f"  ✅ 이미지 경로 있음: {len(valid_paths)}개")
            print(f"  ❌ 이미지 경로 없음: {len(missing_paths)}개")
            
            # 실제 파일 존재 여부 확인
            existing_files = 0
            missing_files = 0
            
            for idx, row in valid_paths.iterrows():
                image_path = row[image_column]
                if pd.isna(image_path) or not image_path:
                    continue
                
                # 상대 경로에서 파일명 추출
                if isinstance(image_path, str):
                    file_name = Path(image_path).stem
                    if file_name in image_files:
                        existing_files += 1
                    else:
                        missing_files += 1
                        print(f"    ❌ 파일 없음: {file_name}")
            
            print(f"  📁 실제 파일 존재: {existing_files}개")
            print(f"  ❌ 실제 파일 없음: {missing_files}개")
            
            # 매칭되지 않은 캐릭터들
            if len(missing_paths) > 0:
                print(f"\n  🔍 이미지 경로가 없는 캐릭터들:")
                for idx, row in missing_paths.head(10).iterrows():
                    char_name = row.get('캐릭터명', row.get('korean_name', ''))
                    eng_name = row.get('영문명', row.get('english_name', ''))
                    print(f"    - {char_name} ({eng_name})")
                
                if len(missing_paths) > 10:
                    print(f"    ... 외 {len(missing_paths) - 10}개")
            
        except Exception as e:
            print(f"❌ {csv_file} 처리 실패: {e}")

def find_missing_images():
    """누락된 이미지 찾기"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    print(f"\n🔍 누락된 이미지 찾기")
    print("=" * 30)
    
    # CSV에서 캐릭터 이름들 수집
    csv_path = CSV_DIR / "eden_quiz_data_fixed.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        char_names = []
        for idx, row in df.iterrows():
            char_name = row.get('캐릭터명', '')
            eng_name = row.get('영문명', '')
            if char_name:
                char_names.append(normalize_name(char_name))
            if eng_name:
                char_names.append(normalize_name(eng_name))
        
        # 이미지 파일명들
        image_files = []
        if IMAGE_DIR.exists():
            for file_path in IMAGE_DIR.iterdir():
                if file_path.is_file():
                    image_files.append(file_path.stem)
        
        # 매칭되지 않은 캐릭터들
        unmatched_chars = []
        for char_name in char_names:
            found = False
            for img_name in image_files:
                if char_name.lower() in img_name.lower() or img_name.lower() in char_name.lower():
                    found = True
                    break
            if not found:
                unmatched_chars.append(char_name)
        
        print(f"캐릭터 이름: {len(char_names)}개")
        print(f"이미지 파일: {len(image_files)}개")
        print(f"매칭되지 않은 캐릭터: {len(unmatched_chars)}개")
        
        if unmatched_chars:
            print("\n매칭되지 않은 캐릭터들:")
            for char in unmatched_chars[:20]:
                print(f"  - {char}")

def main():
    """메인 실행 함수"""
    verify_image_matching()
    find_missing_images()

if __name__ == "__main__":
    main() 