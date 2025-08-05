#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지-캐릭터명-설명 매칭 불일치 문제 분석 스크립트
"""

import os
import sys
import pandas as pd
from pathlib import Path
import re

# 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = BASE_DIR / "character_art"
DATA_CSV = BASE_DIR / "eden_quiz_data.csv"
ORIGINAL_CSV = BASE_DIR / "eden_roulette_data.csv"

def analyze_data_structure():
    """데이터 구조 분석"""
    print("=== 데이터 구조 분석 ===")
    
    # 통합 데이터 분석
    if DATA_CSV.exists():
        try:
            df = pd.read_csv(DATA_CSV, encoding='utf-8-sig')
            print(f"통합 데이터: {len(df)}개 레코드")
            print(f"컬럼: {list(df.columns)}")
            
            # 샘플 데이터 출력
            print("\n샘플 데이터 (처음 3개):")
            for i, row in df.head(3).iterrows():
                print(f"{i+1}. 캐릭터명: {row.get('캐릭터명', 'N/A')}")
                print(f"   영문명: {row.get('영문명', 'N/A')}")
                print(f"   이미지경로: {row.get('캐릭터아이콘경로', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"통합 데이터 읽기 실패: {e}")
    
    # 원본 데이터 분석
    if ORIGINAL_CSV.exists():
        try:
            df_orig = pd.read_csv(ORIGINAL_CSV, encoding='utf-8-sig')
            print(f"\n원본 데이터: {len(df_orig)}개 레코드")
            print(f"컬럼: {list(df_orig.columns)}")
            
            # 샘플 데이터 출력
            print("\n원본 샘플 데이터 (처음 3개):")
            for i, row in df_orig.head(3).iterrows():
                name_col = None
                for col in ['캐릭터명', 'Name', 'korean_name', 'english_name']:
                    if col in df_orig.columns:
                        name_col = col
                        break
                
                image_col = None
                for col in ['캐릭터아이콘경로', 'image_path', 'CharacterIconPath']:
                    if col in df_orig.columns:
                        image_col = col
                        break
                
                print(f"{i+1}. 이름({name_col}): {row.get(name_col, 'N/A')}")
                print(f"   이미지({image_col}): {row.get(image_col, 'N/A')}")
                print()
                
        except Exception as e:
            print(f"원본 데이터 읽기 실패: {e}")

def analyze_image_files():
    """이미지 파일 분석"""
    print("\n=== 이미지 파일 분석 ===")
    
    if not IMAGE_DIR.exists():
        print(f"이미지 디렉토리 없음: {IMAGE_DIR}")
        return
    
    # 이미지 파일 목록
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        image_files.extend(list(IMAGE_DIR.glob(f"*{ext}")))
        image_files.extend(list(IMAGE_DIR.glob(f"**/*{ext}")))
    
    print(f"총 이미지 파일 수: {len(image_files)}개")
    
    # 파일명 패턴 분석
    korean_pattern = re.compile(r'[가-힣]')
    english_pattern = re.compile(r'[a-zA-Z]')
    
    korean_files = []
    english_files = []
    mixed_files = []
    
    for img_file in image_files[:20]:  # 처음 20개만 분석
        filename = img_file.stem
        has_korean = bool(korean_pattern.search(filename))
        has_english = bool(english_pattern.search(filename))
        
        if has_korean and has_english:
            mixed_files.append(filename)
        elif has_korean:
            korean_files.append(filename)
        elif has_english:
            english_files.append(filename)
    
    print(f"한글 파일명: {len(korean_files)}개")
    print(f"영문 파일명: {len(english_files)}개")
    print(f"혼합 파일명: {len(mixed_files)}개")
    
    # 샘플 출력
    if korean_files:
        print(f"\n한글 파일명 샘플: {korean_files[:3]}")
    if english_files:
        print(f"영문 파일명 샘플: {english_files[:3]}")
    if mixed_files:
        print(f"혼합 파일명 샘플: {mixed_files[:3]}")

def analyze_matching_issues():
    """매칭 문제 분석"""
    print("\n=== 매칭 문제 분석 ===")
    
    if not DATA_CSV.exists():
        print("통합 데이터 파일 없음")
        return
    
    try:
        df = pd.read_csv(DATA_CSV, encoding='utf-8-sig')
        
        # 이미지 경로 존재 여부 확인
        missing_images = 0
        path_mismatches = []
        
        for i, row in df.head(10).iterrows():  # 처음 10개만 확인
            char_name = row.get('캐릭터명', '')
            eng_name = row.get('영문명', '')
            image_path = row.get('캐릭터아이콘경로', '')
            
            if image_path:
                if not os.path.exists(image_path):
                    missing_images += 1
                    
                    # 파일명에서 캐릭터명 추출
                    if image_path:
                        filename = Path(image_path).stem
                        path_mismatches.append({
                            'index': i,
                            'char_name': char_name,
                            'eng_name': eng_name,
                            'filename': filename,
                            'image_path': image_path
                        })
        
        print(f"누락된 이미지: {missing_images}개")
        
        if path_mismatches:
            print("\n경로 불일치 샘플:")
            for mismatch in path_mismatches[:5]:
                print(f"  {mismatch['index']+1}. 캐릭터명: {mismatch['char_name']}")
                print(f"     영문명: {mismatch['eng_name']}")
                print(f"     파일명: {mismatch['filename']}")
                print(f"     경로: {mismatch['image_path']}")
                print()
                
    except Exception as e:
        print(f"매칭 분석 실패: {e}")

def suggest_solutions():
    """해결방안 제시"""
    print("\n=== 해결방안 ===")
    print("1. 데이터-이미지 매칭 재구성")
    print("   - 실제 존재하는 이미지 파일 기준으로 데이터 재매칭")
    print("   - 파일명과 캐릭터명 일치성 확보")
    
    print("\n2. 이미지 파일 정리")
    print("   - 중복/누락 파일 정리")
    print("   - 일관된 파일명 규칙 적용")
    
    print("\n3. 앱 매칭 로직 개선")
    print("   - 대소문자 무시 매칭")
    print("   - 파일 존재 여부 사전 확인")
    print("   - 대체 이미지 로직 강화")

def main():
    """메인 분석 함수"""
    print("이미지-캐릭터명-설명 매칭 불일치 문제 분석")
    print("=" * 50)
    
    analyze_data_structure()
    analyze_image_files()
    analyze_matching_issues()
    suggest_solutions()
    
    print("\n분석 완료!")

if __name__ == "__main__":
    main()
