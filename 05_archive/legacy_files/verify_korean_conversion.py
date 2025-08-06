#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Another Eden 한글 변환 검증 스크립트
캐릭터명과 퍼스널리티 한글 변환이 제대로 되고 있는지 확인
"""

import pandas as pd
from pathlib import Path
import unicodedata

def verify_korean_conversion():
    """한글 변환 검증"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    
    print("🔍 Another Eden 한글 변환 검증")
    print("=" * 50)
    
    # 1. 매칭 파일들 확인
    print("\n📋 매칭 파일 확인:")
    
    matching_names_path = CSV_DIR / "Matching_names.csv"
    personality_matching_path = CSV_DIR / "personality_matching.csv"
    
    if matching_names_path.exists():
        df_names = pd.read_csv(matching_names_path, encoding='utf-8-sig')
        print(f"✅ Matching_names.csv: {len(df_names)}개 매칭")
        print("  예시:")
        for i, row in df_names.head(5).iterrows():
            eng = row.iloc[0]
            kor = row.iloc[1]
            print(f"    {eng} → {kor}")
    else:
        print("❌ Matching_names.csv 파일이 없습니다")
    
    if personality_matching_path.exists():
        df_personality = pd.read_csv(personality_matching_path, encoding='utf-8-sig')
        print(f"✅ personality_matching.csv: {len(df_personality)}개 매칭")
        print("  예시:")
        for i, row in df_personality.head(5).iterrows():
            eng = row['English']
            kor = row['Korean']
            print(f"    {eng} → {kor}")
    else:
        print("❌ personality_matching.csv 파일이 없습니다")
    
    # 2. 실제 데이터에서 한글 변환 확인
    print("\n📄 실제 데이터 한글 변환 확인:")
    
    quiz_data_path = CSV_DIR / "eden_quiz_data_fixed.csv"
    if quiz_data_path.exists():
        df_quiz = pd.read_csv(quiz_data_path, encoding='utf-8-sig')
        
        # 한글 캐릭터명 확인
        korean_names = df_quiz['캐릭터명'].dropna()
        korean_count = len([name for name in korean_names if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in str(name))])
        
        print(f"✅ 퀴즈 데이터: {len(df_quiz)}개 캐릭터")
        print(f"  한글 캐릭터명: {korean_count}개")
        
        # 한글 퍼스널리티 확인
        personality_col = '성격특성리스트'
        if personality_col in df_quiz.columns:
            korean_personalities = 0
            total_personalities = 0
            
            for idx, row in df_quiz.iterrows():
                personality_str = str(row.get(personality_col, ''))
                if personality_str and personality_str != 'nan':
                    total_personalities += 1
                    # 한글 문자가 포함된 퍼스널리티 확인
                    if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in personality_str):
                        korean_personalities += 1
            
            print(f"  퍼스널리티 데이터: {total_personalities}개 캐릭터")
            print(f"  한글 퍼스널리티: {korean_personalities}개")
            
            # 예시 출력
            print("  한글 퍼스널리티 예시:")
            for idx, row in df_quiz.iterrows():
                personality_str = str(row.get(personality_col, ''))
                if personality_str and personality_str != 'nan':
                    if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in personality_str):
                        char_name = row.get('캐릭터명', '')
                        print(f"    {char_name}: {personality_str}")
                        break
        else:
            print("  ❌ 성격특성리스트 컬럼이 없습니다")
    
    # 3. 매칭되지 않은 항목 찾기
    print("\n🔍 매칭되지 않은 항목 찾기:")
    
    if matching_names_path.exists() and quiz_data_path.exists():
        df_names = pd.read_csv(matching_names_path, encoding='utf-8-sig')
        df_quiz = pd.read_csv(quiz_data_path, encoding='utf-8-sig')
        
        # 매칭 딕셔너리 생성
        name_mapping = {}
        for _, row in df_names.iterrows():
            eng_name = str(row.iloc[0]).strip()
            kor_name = str(row.iloc[1]).strip()
            if eng_name and kor_name and kor_name != 'nan':
                name_mapping[eng_name.lower()] = kor_name
        
        # 매칭되지 않은 영문명 찾기
        unmatched_eng = []
        for idx, row in df_quiz.iterrows():
            eng_name = str(row.get('영문명', '')).strip()
            if eng_name and eng_name != 'nan':
                # 스타일 접미사 제거
                base_name = eng_name
                for suffix in [' (Another Style)', ' (Extra Style)', ' AS', ' ES']:
                    if eng_name.endswith(suffix):
                        base_name = eng_name[:-len(suffix)]
                        break
                
                if base_name.lower() not in name_mapping:
                    unmatched_eng.append(eng_name)
        
        print(f"  매칭되지 않은 영문명: {len(unmatched_eng)}개")
        if unmatched_eng:
            print("  예시:")
            for name in unmatched_eng[:10]:
                print(f"    - {name}")
    
    # 4. 퍼스널리티 매칭 확인
    if personality_matching_path.exists() and quiz_data_path.exists():
        df_personality = pd.read_csv(personality_matching_path, encoding='utf-8-sig')
        df_quiz = pd.read_csv(quiz_data_path, encoding='utf-8-sig')
        
        # 퍼스널리티 매칭 딕셔너리 생성
        personality_mapping = {}
        for _, row in df_personality.iterrows():
            eng = str(row['English']).strip()
            kor = str(row['Korean']).strip()
            if eng and kor and kor != 'nan':
                personality_mapping[eng.lower()] = kor
        
        # 매칭되지 않은 퍼스널리티 찾기
        unmatched_personalities = set()
        for idx, row in df_quiz.iterrows():
            personality_str = str(row.get('성격특성리스트', ''))
            if personality_str and personality_str != 'nan':
                personalities = [p.strip() for p in personality_str.split(',')]
                for personality in personalities:
                    if personality and personality.lower() not in personality_mapping:
                        unmatched_personalities.add(personality)
        
        print(f"  매칭되지 않은 퍼스널리티: {len(unmatched_personalities)}개")
        if unmatched_personalities:
            print("  예시:")
            for personality in list(unmatched_personalities)[:10]:
                print(f"    - {personality}")

def main():
    """메인 실행 함수"""
    verify_korean_conversion()

if __name__ == "__main__":
    main() 