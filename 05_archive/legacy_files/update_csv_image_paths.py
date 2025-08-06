#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 CSV 이미지 경로 업데이트 스크립트
이미지 파일과 매칭하여 CSV의 이미지 경로를 업데이트합니다.
"""

import pandas as pd
import os
from pathlib import Path
import unicodedata

def normalize_name(name):
    """이름 정규화"""
    if pd.isna(name) or not name:
        return ""
    return unicodedata.normalize("NFKC", str(name)).strip()

def find_matching_image(char_name, eng_name, image_dir):
    """캐릭터 이름과 매칭되는 이미지 파일 찾기"""
    if not image_dir.exists():
        return None
    
    # 검색할 이름들 (한글명, 영문명, 정규화된 이름들)
    search_names = []
    
    if char_name and not pd.isna(char_name):
        search_names.append(normalize_name(char_name))
        # 한글명에서 특수문자 제거
        clean_kor = str(char_name).replace(" ", "").replace("(", "").replace(")", "")
        search_names.append(clean_kor)
    
    if eng_name and not pd.isna(eng_name):
        search_names.append(normalize_name(eng_name))
        # 영문명에서 특수문자 제거
        clean_eng = str(eng_name).replace(" ", "").replace("(", "").replace(")", "")
        search_names.append(clean_eng)
    
    # 이미지 파일 검색
    for file_path in image_dir.iterdir():
        if file_path.is_file():
            file_name = file_path.stem  # 확장자 제외
            
            # 정확한 매칭
            for search_name in search_names:
                if search_name and search_name.lower() == file_name.lower():
                    return str(file_path.relative_to(image_dir.parent.parent))
            
            # 부분 매칭 (포함 관계)
            for search_name in search_names:
                if search_name and search_name.lower() in file_name.lower():
                    return str(file_path.relative_to(image_dir.parent.parent))
    
    return None

def update_csv_image_paths():
    """CSV 파일의 이미지 경로 업데이트"""
    
    # 프로젝트 루트 설정
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    if not CSV_DIR.exists():
        print(f"❌ CSV 디렉토리를 찾을 수 없습니다: {CSV_DIR}")
        return
    
    if not IMAGE_DIR.exists():
        print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {IMAGE_DIR}")
        return
    
    print(f"📋 CSV 이미지 경로 업데이트 시작")
    
    # 처리할 CSV 파일들
    csv_files = [
        ("eden_quiz_data_fixed.csv", "캐릭터아이콘경로"),
        ("eden_roulette_data.csv", "image_path"),
        ("eden_roulette_data_with_personalities.csv", "image_path")
    ]
    
    for csv_file, image_column in csv_files:
        csv_path = CSV_DIR / csv_file
        
        if not csv_path.exists():
            print(f"⚠️ {csv_file} 파일이 없습니다.")
            continue
        
        print(f"\n📄 {csv_file} 처리 중...")
        
        try:
            # CSV 로드
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            # 이미지 경로 컬럼이 없으면 생성
            if image_column not in df.columns:
                df[image_column] = ""
            
            updated_count = 0
            
            for idx, row in df.iterrows():
                char_name = row.get('캐릭터명', row.get('korean_name', ''))
                eng_name = row.get('영문명', row.get('english_name', ''))
                
                # 현재 이미지 경로 (NaN 안전 처리)
                current_path = row.get(image_column, '')
                if pd.isna(current_path):
                    current_path = ""
                else:
                    current_path = str(current_path)
                
                # 이미 경로가 있으면 건너뛰기
                if current_path and current_path.strip():
                    continue
                
                # 매칭되는 이미지 찾기
                image_path = find_matching_image(char_name, eng_name, IMAGE_DIR)
                
                if image_path:
                    df.at[idx, image_column] = image_path
                    updated_count += 1
                    char_display = char_name if char_name and not pd.isna(char_name) else eng_name
                    print(f"  ✅ {char_display}: {image_path}")
            
            # 업데이트된 CSV 저장
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  📊 {updated_count}개 경로 업데이트 완료")
            
        except Exception as e:
            print(f"❌ {csv_file} 처리 실패: {e}")
    
    print(f"\n✅ 모든 CSV 파일 처리 완료")

if __name__ == "__main__":
    update_csv_image_paths() 