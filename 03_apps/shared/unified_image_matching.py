#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 이미지 매칭 및 데이터 생성 스크립트
- 한글/영문 이름 매칭
- 이미지 파일 경로 정규화 및 존재 확인
- 퀴즈/룰렛 앱에서 사용 가능한 통합 CSV 데이터 생성
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
INPUT_CSV = BASE_DIR / "eden_roulette_data.csv"
OUTPUT_CSV = BASE_DIR / "eden_quiz_data.csv"

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

# 이미지 파일 검색
def find_image_file(base_name, style_suffix=""):
    """이미지 파일 검색 (대소문자 무시)"""
    if not IMAGE_DIR.exists():
        return None
    
    # 파일명 생성
    filename_base = sanitize_filename(base_name + style_suffix)
    
    # 확장자 목록
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    # 정확한 이름으로 검색
    for ext in extensions:
        target_file = f"{filename_base}{ext}"
        target_path = IMAGE_DIR / target_file
        if target_path.exists():
            return str(target_path)
    
    # 대소문자 무시하고 검색
    filename_base_lower = filename_base.lower()
    for file in IMAGE_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in extensions:
            if file.stem.lower() == filename_base_lower:
                return str(file)
    
    return None

# 통합 데이터 생성
def create_unified_data():
    """통합 데이터 생성"""
    print("통합 이미지 매칭 및 데이터 생성 시작...")
    print("=" * 50)
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매칭 로드: {len(korean_mapping)}개")
    
    # 입력 CSV 로드
    if not INPUT_CSV.exists():
        print(f"[ERROR] 입력 파일 없음: {INPUT_CSV}")
        return False
    
    try:
        df = pd.read_csv(INPUT_CSV, encoding='utf-8-sig')
        print(f"입력 데이터 로드: {len(df)}개 레코드")
    except Exception as e:
        print(f"[ERROR] 입력 파일 읽기 실패: {e}")
        return False
    
    # 데이터 처리
    results = []
    match_stats = {'matched_korean': 0, 'matched_english': 0, 'no_image': 0}
    
    for _, row in df.iterrows():
        # 기존 데이터
        eng_name = str(row.get('english_name', '')).strip()
        kor_name = str(row.get('korean_name', '')).strip()
        
        # 이름 분석
        base_name, style_suffix = extract_style_suffix(eng_name)
        
        # 한글명 확인 (기존 데이터가 없거나 영어와 동일한 경우)
        if not kor_name or kor_name == eng_name:
            kor_name = korean_mapping.get(base_name.lower(), base_name) + style_suffix
        
        # 이미지 파일 검색
        image_path = find_image_file(base_name, style_suffix)
        
        # 결과 추가
        results.append({
            '캐릭터명': kor_name,
            '영문명': eng_name,
            '캐릭터아이콘경로': image_path or '',
            '희귀도': str(row.get('희귀도', '')),
            '속성명리스트': str(row.get('속성명리스트', '')),
            '무기명리스트': str(row.get('무기명리스트', '')),
            '성격특성리스트': str(row.get('성격특성리스트', '')),
            'image_status': 'found' if image_path else 'missing'
        })
        
        # 통계 업데이트
        if image_path:
            if kor_name != eng_name:
                match_stats['matched_korean'] += 1
            else:
                match_stats['matched_english'] += 1
        else:
            match_stats['no_image'] += 1
    
    # 결과 저장
    df_result = pd.DataFrame(results)
    df_result = df_result.drop(columns=['image_status'])  # 내부용 컬럼 제거
    
    try:
        df_result.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"\n결과 저장 완료: {OUTPUT_CSV}")
        print(f"총 레코드: {len(df_result)}개")
        
        # 통계 출력
        print("\n매칭 통계:")
        print(f"  한글 매칭: {match_stats['matched_korean']}개")
        print(f"  영문 유지: {match_stats['matched_english']}개")
        print(f"  이미지 없음: {match_stats['no_image']}개")
        
        # 누락된 이미지 샘플 출력
        if match_stats['no_image'] > 0:
            missing_sample = df_result[df_result['캐릭터아이콘경로'] == ''].head(10)
            print("\n누락된 이미지 샘플 (처음 10개):")
            for _, row in missing_sample.iterrows():
                print(f"  {row['캐릭터명']} ({row['영문명']})")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 결과 저장 실패: {e}")
        return False

# 앱용 데이터 검증
def validate_for_apps():
    """앱에서 사용 가능한지 검증"""
    if not OUTPUT_CSV.exists():
        print(f"[ERROR] 출력 파일 없음: {OUTPUT_CSV}")
        return False
    
    try:
        df = pd.read_csv(OUTPUT_CSV, encoding='utf-8-sig')
        print(f"\n앱용 데이터 검증: {len(df)}개 레코드")
        
        # 필수 컬럼 확인
        required_columns = ['캐릭터명', '영문명', '캐릭터아이콘경로']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"[ERROR] 누락된 필수 컬럼: {missing_columns}")
            return False
        
        # 이미지 파일 존재 확인 (샘플)
        missing_count = 0
        check_limit = 50  # 처음 50개만 확인
        checked = 0
        
        for _, row in df.iterrows():
            if checked >= check_limit:
                break
                
            image_path = row.get('캐릭터아이콘경로', '')
            if image_path and not os.path.exists(image_path):
                missing_count += 1
                if missing_count <= 5:  # 처음 5개만 출력
                    print(f"[WARN] 파일 없음: {image_path}")
            checked += 1
        
        print(f"파일 존재 확인: {checked}개 중 {missing_count}개 누락")
        
        # 중복 이름 확인
        name_counts = df['캐릭터명'].value_counts()
        duplicates = name_counts[name_counts > 1]
        if len(duplicates) > 0:
            print(f"[WARN] 중복 이름: {len(duplicates)}개")
            for name, count in duplicates.head(5).items():
                print(f"  {name}: {count}개")
        else:
            print("이름 중복 없음")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 데이터 검증 실패: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        success = validate_for_apps()
        sys.exit(0 if success else 1)
    else:
        success = create_unified_data()
        if success:
            validate_for_apps()
        sys.exit(0 if success else 1)
