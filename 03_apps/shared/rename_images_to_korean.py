#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 이미지 파일 한글명/영문명 기준 일괄 이름변경 스크립트
- 기존 character_art 폴더의 이미지를 한글 matching names 기준으로 이름 변경
- 기존 파일을 다운로드하지 않고 이름만 변경하여 속도 향상
"""

import os
import sys
import pandas as pd
import re
import unicodedata
from pathlib import Path
import shutil

# 한글 매핑 로드
def load_korean_mapping():
    """Matching_names.csv에서 한글 매핑 로드"""
    mapping = {}
    csv_path = "Matching_names.csv"
    if not os.path.exists(csv_path):
        print(f"[WARN] {csv_path} 없음, 영어명만 사용")
        return mapping
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        for _, row in df.iterrows():
            eng = str(row.iloc[0]).strip()
            kor = str(row.iloc[1]).strip()
            if eng and kor and kor != 'nan':
                mapping[eng.lower()] = kor  # 대소문자 구분 없이 매칭
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

# 기존 파일 이름 파싱
def parse_existing_filename(filename):
    """기존 파일명에서 캐릭터명 추출"""
    name_without_ext = os.path.splitext(filename)[0]
    
    # 다양한 네이밍 패턴 처리
    # 1. 일반적인 영어 이름
    # 2. 스타일 접미사 포함 (AS, ES 등)
    # 3. 숫자 접미사 (중복 방지용)
    
    # 스타일 접미사 제거하여 기본 이름 추출
    base_name, style_suffix = extract_style_suffix(name_without_ext)
    
    # 숫자 접미사 제거 (예: Aldo_1, Shion_2)
    base_name = re.sub(r'_\d+$', '', base_name)
    
    return base_name, style_suffix

# 이미지 파일 이름 변경
def rename_images_to_korean():
    """기존 이미지 파일 이름을 한글 기준으로 변경"""
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매핑 로드: {len(korean_mapping)}개")
    
    # character_art 디렉토리 확인
    image_dir = "character_art"
    if not os.path.exists(image_dir):
        print(f"[ERROR] {image_dir} 디렉토리가 없습니다")
        return
    
    # 이미지 파일 찾기
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    image_files = []
    
    for file in os.listdir(image_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("[ERROR] 이미지 파일이 없습니다")
        return
    
    print(f"총 {len(image_files)}개 이미지 파일 발견")
    
    # 이름 변경 계획 수립
    rename_plan = []
    used_names = set()
    
    for filename in image_files:
        filepath = os.path.join(image_dir, filename)
        
        # 기존 파일명에서 캐릭터명 추출
        base_name, style_suffix = parse_existing_filename(filename)
        
        # 한글명 변환
        korean_base = korean_mapping.get(base_name.lower(), base_name)
        
        # 새 파일명 생성
        new_base = sanitize_filename(korean_base + style_suffix)
        
        # 중복 방지
        counter = 1
        new_filename = f"{new_base}{os.path.splitext(filename)[1]}"
        while new_filename in used_names or os.path.exists(os.path.join(image_dir, new_filename)):
            new_filename = f"{new_base}_{counter}{os.path.splitext(filename)[1]}"
            counter += 1
        
        used_names.add(new_filename)
        
        rename_plan.append({
            'old_path': filepath,
            'new_path': os.path.join(image_dir, new_filename),
            'old_name': filename,
            'new_name': new_filename,
            'english_base': base_name,
            'korean_base': korean_base,
            'style_suffix': style_suffix
        })
    
    # 변경 계획 출력
    print("\n변경 계획:")
    print("-" * 80)
    
    korean_renamed = 0
    for plan in rename_plan:
        if plan['korean_base'] != plan['english_base']:
            korean_renamed += 1
            print(f"KO: {plan['old_name']} -> {plan['new_name']}")
        else:
            print(f"EN: {plan['old_name']} -> {plan['new_name']}")
    
    print(f"\n한글로 변경: {korean_renamed}개")
    print(f"영문 유지: {len(rename_plan) - korean_renamed}개")
    
    # 실제 변경 실행
    print("\n파일 이름 변경 중...")
    success_count = 0
    
    for plan in rename_plan:
        try:
            if plan['old_path'] != plan['new_path']:
                os.rename(plan['old_path'], plan['new_path'])
                success_count += 1
                print(f"✓ {plan['old_name']} -> {plan['new_name']}")
        except Exception as e:
            print(f"✗ 실패 {plan['old_name']}: {e}")
    
    # 결과 CSV 생성
    results = []
    for plan in rename_plan:
        results.append({
            'english_name': plan['english_base'] + plan['style_suffix'],
            'korean_name': plan['korean_base'] + plan['style_suffix'],
            'image_filename': plan['new_name'],
            'image_path': plan['new_path'],
            'status': 'renamed' if plan['korean_base'] != plan['english_base'] else 'english_kept'
        })
    
    df_result = pd.DataFrame(results)
    csv_path = 'eden_roulette_data.csv'
    df_result.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\n" + "=" * 50)
    print(f"이름 변경 완료!")
    print(f"총 변경: {success_count}개")
    print(f"결과 저장: {csv_path}")
    
    # 통계
    status_counts = df_result['status'].value_counts()
    print("\n상태별 통계:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

# CSV 데이터 검증
def validate_csv_data():
    """CSV 데이터 검증"""
    csv_path = 'eden_roulette_data.csv'
    if not os.path.exists(csv_path):
        print("[ERROR] CSV 파일이 없습니다")
        return
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"CSV 로드 완료: {len(df)}개 레코드")
        
        # 이미지 파일 존재 확인
        missing_images = []
        for _, row in df.iterrows():
            image_path = row.get('image_path', '')
            if image_path and not os.path.exists(image_path):
                missing_images.append(image_path)
        
        if missing_images:
            print(f"[WARN] 누락된 이미지: {len(missing_images)}개")
            for img in missing_images[:5]:  # 처음 5개만 표시
                print(f"  {img}")
        else:
            print("✅ 모든 이미지 파일 존재 확인")
            
    except Exception as e:
        print(f"[ERROR] CSV 검증 실패: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        validate_csv_data()
    else:
        rename_images_to_korean()
        validate_csv_data()
