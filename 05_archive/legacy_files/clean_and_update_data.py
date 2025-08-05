#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 Another Eden 데이터 정리 및 업데이트 스크립트
기존 데이터를 정리하고 새로운 스크래핑 데이터로 업데이트
"""

import pandas as pd
from pathlib import Path
import shutil

def clean_and_update_data():
    """데이터 정리 및 업데이트"""
    
    PROJECT_ROOT = Path(__file__).parent.resolve()
    CSV_DIR = PROJECT_ROOT / "04_data" / "csv"
    
    print("🧹 Another Eden 데이터 정리 및 업데이트")
    print("=" * 50)
    
    # 1. 기존 데이터 백업
    print("\n📦 기존 데이터 백업 중...")
    backup_dir = CSV_DIR / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    csv_files = [
        "eden_quiz_data_fixed.csv",
        "eden_roulette_data.csv", 
        "eden_roulette_data_with_personalities.csv",
        "character_personalities.csv"
    ]
    
    for csv_file in csv_files:
        csv_path = CSV_DIR / csv_file
        if csv_path.exists():
            backup_path = backup_dir / f"{csv_file}.backup"
            shutil.copy2(csv_path, backup_path)
            print(f"  ✅ {csv_file} 백업 완료")
    
    # 2. 새로운 스크래핑 실행
    print("\n📡 새로운 스크래핑 실행 중...")
    try:
        import subprocess
        import sys
        
        result = subprocess.run([sys.executable, "01_scraping/master_scraper.py"], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ 스크래핑 완료")
        else:
            print(f"❌ 스크래핑 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 스크래핑 오류: {e}")
        return False
    
    # 3. 데이터 무결성 검증
    print("\n🔍 데이터 무결성 검증...")
    
    for csv_file in csv_files:
        csv_path = CSV_DIR / csv_file
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                print(f"  ✅ {csv_file}: {len(df)}개 행")
                
                # 중복 체크
                if '캐릭터명' in df.columns:
                    duplicates = df['캐릭터명'].duplicated().sum()
                    if duplicates > 0:
                        print(f"    ⚠️ 중복 캐릭터명: {duplicates}개")
                        # 중복 제거
                        df = df.drop_duplicates(subset=['캐릭터명'])
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        print(f"    ✅ 중복 제거 완료: {len(df)}개 행")
                
                elif 'english_name' in df.columns:
                    duplicates = df['english_name'].duplicated().sum()
                    if duplicates > 0:
                        print(f"    ⚠️ 중복 영문명: {duplicates}개")
                        # 중복 제거
                        df = df.drop_duplicates(subset=['english_name'])
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        print(f"    ✅ 중복 제거 완료: {len(df)}개 행")
                
            except Exception as e:
                print(f"  ❌ {csv_file} 읽기 실패: {e}")
        else:
            print(f"  ⚠️ {csv_file} 파일이 없습니다")
    
    # 4. 이미지 경로 업데이트
    print("\n🖼️ 이미지 경로 업데이트 중...")
    try:
        result = subprocess.run([sys.executable, "fix_data_issues.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 이미지 경로 업데이트 완료")
        else:
            print(f"⚠️ 이미지 경로 업데이트 실패: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 이미지 경로 업데이트 오류: {e}")
    
    # 5. 최종 검증
    print("\n✅ 최종 검증...")
    
    quiz_data_path = CSV_DIR / "eden_quiz_data_fixed.csv"
    if quiz_data_path.exists():
        df = pd.read_csv(quiz_data_path, encoding='utf-8-sig')
        
        # 한글 캐릭터명 수
        korean_names = df['캐릭터명'].dropna()
        korean_count = len([name for name in korean_names if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in str(name))])
        
        # 한글 퍼스널리티 수
        personality_col = '성격특성리스트'
        korean_personalities = 0
        if personality_col in df.columns:
            for idx, row in df.iterrows():
                personality_str = str(row.get(personality_col, ''))
                if personality_str and personality_str != 'nan':
                    if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in personality_str):
                        korean_personalities += 1
        
        print(f"  📊 최종 통계:")
        print(f"    - 총 캐릭터: {len(df)}개")
        print(f"    - 한글 캐릭터명: {korean_count}개")
        print(f"    - 한글 퍼스널리티: {korean_personalities}개")
        
        # 중복 확인
        duplicates = df['캐릭터명'].duplicated().sum()
        if duplicates == 0:
            print(f"    - 중복: 없음 ✅")
        else:
            print(f"    - 중복: {duplicates}개 ⚠️")
    
    print("\n🎉 데이터 정리 및 업데이트 완료!")
    return True

def main():
    """메인 실행 함수"""
    clean_and_update_data()

if __name__ == "__main__":
    main() 