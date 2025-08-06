#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 데이터 및 이미지 검증 스크립트
- 통합 데이터(eden_quiz_data.csv) 검증
- 이미지 파일 존재 여부 확인
- 앱 호환성 검증
"""

import os
import sys
import pandas as pd
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = BASE_DIR / "character_art"
DATA_CSV = BASE_DIR / "eden_quiz_data.csv"

def validate_data_file():
    """데이터 파일 검증"""
    print("데이터 파일 검증 시작...")
    print("=" * 50)
    
    if not DATA_CSV.exists():
        print(f"[ERROR] 데이터 파일 없음: {DATA_CSV}")
        return False
    
    try:
        df = pd.read_csv(DATA_CSV, encoding='utf-8-sig')
        print(f"[OK] 데이터 로드 성공: {len(df)}개 레코드")
    except Exception as e:
        print(f"[ERROR] 데이터 로드 실패: {e}")
        return False
    
    # 필수 컬럼 확인
    required_columns = ['캐릭터명', '영문명', '캐릭터아이콘경로']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"[ERROR] 필수 컬럼 누락: {missing_columns}")
        return False
    
    print(f"[OK] 필수 컬럼 존재: {required_columns}")
    
    # 데이터 샘플 출력
    print("\n데이터 샘플:")
    print(df.head(3))
    
    return True

def validate_image_files():
    """이미지 파일 검증"""
    print("\n이미지 파일 검증 시작...")
    print("=" * 50)
    
    if not IMAGE_DIR.exists():
        print(f"[WARN] 이미지 디렉토리 없음: {IMAGE_DIR}")
        return True
    
    try:
        df = pd.read_csv(DATA_CSV, encoding='utf-8-sig')
    except Exception as e:
        print(f"[ERROR] 데이터 로드 실패: {e}")
        return False
    
    # 이미지 경로 검증
    missing_count = 0
    checked_count = 0
    
    for _, row in df.iterrows():
        image_path = row.get('캐릭터아이콘경로', '')
        if image_path:
            checked_count += 1
            if not os.path.exists(image_path):
                missing_count += 1
                if missing_count <= 5:  # 처음 5개만 출력
                    print(f"[WARN] 이미지 없음: {image_path}")
    
    print(f"[결과] 이미지 검증: {checked_count}개 중 {missing_count}개 누락")
    return missing_count == 0

def validate_app_compatibility():
    """앱 호환성 검증"""
    print("\n앱 호환성 검증 시작...")
    print("=" * 50)
    
    # 퀴즈 앱 검증
    quiz_app_path = BASE_DIR / "eden_quiz_app.py"
    if not quiz_app_path.exists():
        print(f"[ERROR] 퀴즈 앱 없음: {quiz_app_path}")
        return False
    
    # 룰렛 앱 검증
    roulette_app_path = BASE_DIR / "streamlit_eden_restructure.py"
    if not roulette_app_path.exists():
        print(f"[ERROR] 룰렛 앱 없음: {roulette_app_path}")
        return False
    
    print("[OK] 앱 파일 존재 확인")
    
    # 앱 데이터 로드 로직 검증 (간단히)
    try:
        with open(quiz_app_path, 'r', encoding='utf-8') as f:
            quiz_content = f.read()
        if "eden_quiz_data.csv" not in quiz_content:
            print("[WARN] 퀴즈 앱에서 통합 데이터 사용 안 함")
        
        with open(roulette_app_path, 'r', encoding='utf-8') as f:
            roulette_content = f.read()
        if "eden_quiz_data.csv" not in roulette_content:
            print("[WARN] 룰렛 앱에서 통합 데이터 사용 안 함")
    except Exception as e:
        print(f"[ERROR] 앱 파일 검사 실패: {e}")
    
    print("[OK] 앱 호환성 검증 완료")
    return True

def main():
    """메인 검증 함수"""
    print("Another Eden 프로젝트 최종 검증 스크립트")
    print("버전: 1.0")
    
    validations = [
        ("데이터 파일 검증", validate_data_file),
        ("이미지 파일 검증", validate_image_files),
        ("앱 호환성 검증", validate_app_compatibility)
    ]
    
    results = []
    for name, func in validations:
        print(f"\n[{name}]")
        try:
            result = func()
            results.append(result)
            status = "PASS" if result else "FAIL"
            print(f"[{status}] {name}")
        except Exception as e:
            print(f"[ERROR] {name} 실행 중 오류: {e}")
            results.append(False)
    
    # 최종 결과
    print("\n" + "=" * 50)
    print("최종 검증 결과:")
    all_passed = all(results)
    status = "모두 통과" if all_passed else "일부 실패"
    print(f"상태: {status} ({sum(results)}/{len(results)})")
    
    if all_passed:
        print("\n🎉 모든 검증이 성공적으로 완료되었습니다!")
        print("프로젝트가 정상적으로 작동할 준비가 되었습니다.")
    else:
        print("\n⚠️  일부 검증이 실패했습니다.")
        print("위의 오류 메시지를 확인하고 필요한 조치를 취해주세요.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
