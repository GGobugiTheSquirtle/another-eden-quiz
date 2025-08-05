#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 이미지 파일을 한글 이름으로 일괄 이름변경하는 스크립트
- Matching_names.csv 기반 매칭
- 스타일 접미사(AS/ES 등) 유지
- 기존 파일명 기반 매칭
"""

import os
import sys
import pandas as pd
import re
import unicodedata
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = BASE_DIR / "character_art"
MATCHING_CSV = BASE_DIR / "Matching_names.csv"
OUTPUT_CSV = BASE_DIR / "renamed_image_mapping.csv"

# 한글 매핑 로드
def load_korean_mapping():
    """Matching_names.csv에서 한글 매핑 로드"""
    mapping = {}
    if not MATCHING_CSV.exists():
        print(f"[WARN] {MATCHING_CSV} 없음, 영어명만 사용")
        return mapping
    
    try:
        df = pd.read_csv(MATCHING_CSV, encoding='utf-8-sig')
        for _, row in df.iterrows():
            eng = str(row.iloc[0]).strip()
            kor = str(row.iloc[1]).strip()
            if eng and kor and kor != 'nan':
                mapping[eng.lower()] = kor
    except Exception as e:
        print(f"[ERROR] 매핑 파일 읽기 실패: {e}")
    
    return mapping

# 스타일 접미사 처리
def extract_style_suffix(name):
    """AS/ES/NS 등 스타일 접미사 분리"""
    style_patterns = [
        r'\s+(AS)$', r'\s+(ES)$', r'\s+(NS)$',
        r'\s+(Another\s*Style)$', r'\s+(Extra\s*Style)$',
        r'\s+(Manifestation)$', r'\s+(Alter)$',
    ]
    base_name = name
    style_suffix = ""
    
    for pattern in style_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            style_suffix = " " + match.group(1)
            base_name = name[:match.start()]
            break
    return base_name, style_suffix

# 파일명 안전화
def sanitize_filename(name):
    """파일명으로 안전하게 변환"""
    name = unicodedata.normalize('NFKC', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip()
    return name

# 이미지 파일 일괄 이름변경
def batch_rename_images():
    """이미지 파일 일괄 이름변경"""
    print("이미지 파일 한글명 일괄 변경 시작...")
    print("=" * 50)
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매칭 로드: {len(korean_mapping)}개")
    
    # 이미지 디렉토리 확인
    if not IMAGE_DIR.exists():
        print(f"[ERROR] 이미지 디렉토리 없음: {IMAGE_DIR}")
        return False
    
    # 이미지 파일 목록
    image_files = list(IMAGE_DIR.iterdir())
    image_files = [f for f in image_files if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']]
    print(f"이미지 파일 수: {len(image_files)}개")
    
    if not image_files:
        print("[WARN] 이미지 파일 없음")
        return True
    
    # 이름변경 처리
    rename_results = []
    renamed_count = 0
    error_count = 0
    
    for img_file in image_files:
        try:
            # 기존 파일명 (확장자 제외)
            base_name = img_file.stem
            ext = img_file.suffix
            
            # 스타일 접미사 분리
            eng_base, style_suffix = extract_style_suffix(base_name)
            
            # 한글명 매칭
            kor_name = korean_mapping.get(eng_base.lower(), eng_base)
            new_name = sanitize_filename(kor_name + style_suffix) + ext
            new_path = IMAGE_DIR / new_name
            
            # 이름변경
            if str(img_file) != str(new_path):
                # 중복 파일 처리
                if new_path.exists():
                    print(f"[SKIP] 이미 존재함: {new_name}")
                    continue
                
                img_file.rename(new_path)
                renamed_count += 1
                print(f"[RENAME] {img_file.name} → {new_name}")
            
            # 결과 기록
            rename_results.append({
                'old_name': img_file.name,
                'new_name': new_name,
                'korean_name': kor_name + style_suffix,
                'english_base': eng_base,
                'style_suffix': style_suffix
            })
            
        except Exception as e:
            error_count += 1
            print(f"[ERROR] 이름변경 실패 {img_file.name}: {e}")
    
    # 결과 저장
    if rename_results:
        df_result = pd.DataFrame(rename_results)
        try:
            df_result.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
            print(f"\n결과 저장 완료: {OUTPUT_CSV}")
        except Exception as e:
            print(f"[ERROR] 결과 저장 실패: {e}")
    
    print(f"\n처리 완료: {renamed_count}개 변경, {error_count}개 오류")
    return error_count == 0

if __name__ == "__main__":
    success = batch_rename_images()
    sys.exit(0 if success else 1)
