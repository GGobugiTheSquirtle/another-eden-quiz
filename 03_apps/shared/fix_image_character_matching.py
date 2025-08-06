#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지-캐릭터명-설명 매칭 불일치 문제 해결 스크립트
구조적 분석 및 통합 매칭 로직 개선
"""

import os
import sys
import pandas as pd
from pathlib import Path
import re
import unicodedata

# 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = BASE_DIR / "character_art"
DATA_CSV = BASE_DIR / "eden_quiz_data.csv"
ORIGINAL_CSV = BASE_DIR / "eden_roulette_data.csv"
MATCHING_CSV = BASE_DIR / "Matching_names.csv"
OUTPUT_CSV = BASE_DIR / "eden_quiz_data_fixed.csv"

def load_korean_mapping():
    """한글 매핑 로드"""
    mapping = {}
    if MATCHING_CSV.exists():
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

def find_all_image_files():
    """모든 이미지 파일 검색"""
    image_files = {}
    if not IMAGE_DIR.exists():
        return image_files
    
    # 모든 하위 디렉토리 포함 검색
    for root, dirs, files in os.walk(IMAGE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                full_path = Path(root) / file
                # 파일명(확장자 제외)을 키로 사용
                filename_key = file.lower().rsplit('.', 1)[0]
                image_files[filename_key] = str(full_path)
    
    return image_files

def normalize_name(name):
    """이름 정규화"""
    if not name:
        return ""
    name = unicodedata.normalize('NFKC', str(name))
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_style_suffix(name):
    """스타일 접미사 분리"""
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
    return base_name.strip(), style_suffix

def find_matching_image(char_name, eng_name, image_files, korean_mapping):
    """캐릭터에 맞는 이미지 파일 찾기"""
    # 검색할 이름 후보들
    search_names = []
    
    # 1. 한글 이름 (있는 경우)
    if char_name and char_name != eng_name:
        search_names.append(normalize_name(char_name))
    
    # 2. 영문 이름
    if eng_name:
        search_names.append(normalize_name(eng_name))
    
    # 3. 영문 이름의 한글 매핑
    if eng_name:
        base_eng, style_suffix = extract_style_suffix(eng_name)
        korean_mapped = korean_mapping.get(base_eng.lower())
        if korean_mapped:
            search_names.append(normalize_name(korean_mapped + style_suffix))
    
    # 각 후보 이름으로 이미지 파일 검색
    for search_name in search_names:
        if not search_name:
            continue
            
        # 정확한 매칭
        search_key = search_name.lower()
        if search_key in image_files:
            return image_files[search_key]
        
        # 부분 매칭 (스타일 접미사 제거)
        base_search, _ = extract_style_suffix(search_name)
        base_key = base_search.lower()
        if base_key in image_files:
            return image_files[base_key]
        
        # 유사 매칭 (공백, 특수문자 제거)
        clean_key = re.sub(r'[^\w가-힣]', '', search_key)
        for file_key, file_path in image_files.items():
            clean_file_key = re.sub(r'[^\w가-힣]', '', file_key)
            if clean_key == clean_file_key:
                return file_path
    
    return None

def fix_data_matching():
    """데이터 매칭 수정"""
    print("이미지-캐릭터명 매칭 수정 시작...")
    print("=" * 50)
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매핑 로드: {len(korean_mapping)}개")
    
    # 이미지 파일 검색
    image_files = find_all_image_files()
    print(f"이미지 파일 발견: {len(image_files)}개")
    
    if not image_files:
        print("[WARN] 이미지 파일이 없습니다. 원본 데이터를 사용합니다.")
        # 원본 데이터 사용
        if ORIGINAL_CSV.exists():
            df_orig = pd.read_csv(ORIGINAL_CSV, encoding='utf-8-sig')
            # 컬럼명 통일
            df_result = pd.DataFrame()
            df_result['캐릭터명'] = df_orig.get('Name', df_orig.get('korean_name', ''))
            df_result['영문명'] = df_orig.get('Name', df_orig.get('english_name', ''))
            df_result['캐릭터아이콘경로'] = df_orig.get('CharacterIconPath', df_orig.get('image_path', ''))
            df_result['희귀도'] = df_orig.get('Rarity', '')
            df_result['속성명리스트'] = df_orig.get('AttributeListStr', '')
            df_result['무기명리스트'] = df_orig.get('WeaponListStr', '')
            df_result['성격특성리스트'] = df_orig.get('PersonalityListStr', '')
        else:
            print("[ERROR] 원본 데이터도 없습니다.")
            return False
    else:
        # 기존 데이터 로드
        if DATA_CSV.exists():
            df = pd.read_csv(DATA_CSV, encoding='utf-8-sig')
        elif ORIGINAL_CSV.exists():
            df = pd.read_csv(ORIGINAL_CSV, encoding='utf-8-sig')
            # 컬럼명 변환
            column_mapping = {
                'Name': '영문명',
                'CharacterIconPath': '캐릭터아이콘경로',
                'Rarity': '희귀도',
                'AttributeListStr': '속성명리스트',
                'WeaponListStr': '무기명리스트',
                'PersonalityListStr': '성격특성리스트'
            }
            df = df.rename(columns=column_mapping)
            # 캐릭터명이 없으면 영문명 사용
            if '캐릭터명' not in df.columns:
                df['캐릭터명'] = df['영문명']
        else:
            print("[ERROR] 데이터 파일이 없습니다.")
            return False
        
        # 매칭 수정
        results = []
        matched_count = 0
        missing_count = 0
        
        for _, row in df.iterrows():
            char_name = normalize_name(row.get('캐릭터명', ''))
            eng_name = normalize_name(row.get('영문명', ''))
            
            # 이미지 파일 찾기
            image_path = find_matching_image(char_name, eng_name, image_files, korean_mapping)
            
            # 한글 이름 보정
            if not char_name or char_name == eng_name:
                if eng_name:
                    base_eng, style_suffix = extract_style_suffix(eng_name)
                    korean_mapped = korean_mapping.get(base_eng.lower())
                    if korean_mapped:
                        char_name = korean_mapped + style_suffix
                    else:
                        char_name = eng_name
            
            # 결과 추가
            results.append({
                '캐릭터명': char_name,
                '영문명': eng_name,
                '캐릭터아이콘경로': image_path or '',
                '희귀도': row.get('희귀도', ''),
                '속성명리스트': row.get('속성명리스트', ''),
                '무기명리스트': row.get('무기명리스트', ''),
                '성격특성리스트': row.get('성격특성리스트', '')
            })
            
            if image_path:
                matched_count += 1
            else:
                missing_count += 1
        
        df_result = pd.DataFrame(results)
    
    # 결과 저장
    try:
        df_result.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"\n수정된 데이터 저장: {OUTPUT_CSV}")
        print(f"총 레코드: {len(df_result)}개")
        print(f"이미지 매칭: {matched_count}개")
        print(f"이미지 누락: {missing_count}개")
        
        # 샘플 출력
        print("\n수정된 데이터 샘플:")
        for i, row in df_result.head(5).iterrows():
            print(f"{i+1}. {row['캐릭터명']} ({row['영문명']})")
            print(f"   이미지: {row['캐릭터아이콘경로']}")
            if row['캐릭터아이콘경로']:
                exists = os.path.exists(row['캐릭터아이콘경로'])
                print(f"   존재: {exists}")
            print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 결과 저장 실패: {e}")
        return False

def update_apps():
    """앱에서 수정된 데이터 사용하도록 업데이트"""
    print("\n앱 업데이트 시작...")
    
    # 퀴즈 앱 업데이트
    quiz_app_path = BASE_DIR / "eden_quiz_app.py"
    if quiz_app_path.exists():
        try:
            with open(quiz_app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CSV 파일명 변경
            content = content.replace('eden_quiz_data.csv', 'eden_quiz_data_fixed.csv')
            
            with open(quiz_app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("[OK] 퀴즈 앱 업데이트 완료")
            
        except Exception as e:
            print(f"[ERROR] 퀴즈 앱 업데이트 실패: {e}")
    
    # 룰렛 앱 업데이트
    roulette_app_path = BASE_DIR / "streamlit_eden_restructure.py"
    if roulette_app_path.exists():
        try:
            with open(roulette_app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 통합 데이터 사용 로직 추가
            if 'eden_quiz_data_fixed.csv' not in content:
                # load_and_prepare_data 함수에서 수정된 데이터 우선 사용
                content = content.replace(
                    'unified_csv_path = "eden_quiz_data.csv"',
                    'unified_csv_path = "eden_quiz_data_fixed.csv"'
                )
            
            with open(roulette_app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("[OK] 룰렛 앱 업데이트 완료")
            
        except Exception as e:
            print(f"[ERROR] 룰렛 앱 업데이트 실패: {e}")

def main():
    """메인 실행 함수"""
    print("이미지-캐릭터명-설명 매칭 불일치 문제 해결")
    print("=" * 50)
    
    success = fix_data_matching()
    if success:
        update_apps()
        print("\n✅ 매칭 문제 해결 완료!")
        print("수정된 데이터로 앱을 다시 실행해보세요.")
    else:
        print("\n❌ 매칭 문제 해결 실패")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
