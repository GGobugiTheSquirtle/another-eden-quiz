#!/usr/bin/env python3
"""
🧪 사용자 경험 개선안 테스트 스크립트
개선된 UI/UX의 작동 여부와 성능을 테스트
"""

import os
import sys
from pathlib import Path
import time
import subprocess

def test_file_existence():
    """개선된 파일들의 존재 여부 확인"""
    print("=== [파일] 파일 존재성 테스트 ===")
    
    files_to_check = [
        "app_improved.py",
        "pages/1_룰렛_앱_개선.py", 
        "pages/2_퀴즈_앱_개선.py",
        "components/mobile_nav.py",
        "streamlit_config.toml"
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"[OK] {file_path} ({size:.1f}KB)")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_data_loading():
    """데이터 로딩 테스트"""
    print("\n=== [데이터] 데이터 로딩 테스트 ===")
    
    try:
        import pandas as pd
        
        # 필수 CSV 파일들 테스트
        csv_files = [
            "04_data/csv/eden_quiz_data.csv",
            "04_data/csv/eden_roulette_data.csv",
            "04_data/csv/Matching_names.csv"
        ]
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                print(f"[OK] {csv_file}: {len(df)} rows loaded")
            else:
                print(f"[FAIL] {csv_file}: NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 데이터 로딩 실패: {e}")
        return False

def test_image_processing():
    """이미지 처리 기능 테스트"""
    print("\n=== [이미지] 이미지 처리 테스트 ===")
    
    try:
        import base64
        from pathlib import Path
        
        image_dir = Path("04_data/images/character_art")
        
        if image_dir.exists():
            image_files = list(image_dir.glob("*.png"))[:5]  # 처음 5개만 테스트
            
            success_count = 0
            for img_file in image_files:
                try:
                    with open(img_file, 'rb') as f:
                        data = base64.b64encode(f.read()).decode()
                        if len(data) > 1000:  # 최소 크기 확인
                            success_count += 1
                            print(f"[OK] {img_file.name}: Base64 변환 성공")
                        else:
                            print(f"[WARN] {img_file.name}: 파일이 너무 작음")
                except Exception as e:
                    print(f"[FAIL] {img_file.name}: 변환 실패 - {e}")
            
            print(f"\n[통계] 이미지 처리 성공률: {success_count}/{len(image_files)} ({success_count/len(image_files)*100:.1f}%)")
            return success_count == len(image_files)
        else:
            print("[FAIL] 이미지 디렉토리를 찾을 수 없습니다.")
            return False
            
    except Exception as e:
        print(f"[FAIL] 이미지 처리 테스트 실패: {e}")
        return False

def test_streamlit_syntax():
    """Streamlit 코드 구문 검사"""
    print("\n=== [구문] Streamlit 구문 검사 ===")
    
    py_files = [
        "app_improved.py",
        "pages/1_룰렛_앱_개선.py",
        "pages/2_퀴즈_앱_개선.py"
    ]
    
    all_valid = True
    
    for py_file in py_files:
        if os.path.exists(py_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 기본 구문 검사
                compile(code, py_file, 'exec')
                print(f"[OK] {py_file}: 구문 검사 통과")
                
                # Streamlit 필수 요소 검사
                required_elements = ['st.', 'streamlit']
                missing_elements = [elem for elem in required_elements if elem not in code]
                
                if missing_elements:
                    print(f"[WARN] {py_file}: Streamlit 요소 부족 - {missing_elements}")
                else:
                    print(f"[OK] {py_file}: Streamlit 요소 확인됨")
                    
            except SyntaxError as e:
                print(f"[FAIL] {py_file}: 구문 오류 - {e}")
                all_valid = False
            except Exception as e:
                print(f"[WARN] {py_file}: 검사 중 오류 - {e}")
        else:
            print(f"[FAIL] {py_file}: 파일을 찾을 수 없음")
            all_valid = False
    
    return all_valid

def performance_test():
    """성능 테스트"""
    print("\n=== [성능] 성능 테스트 ===")
    
    try:
        # 데이터 로딩 시간 측정
        start_time = time.time()
        
        import pandas as pd
        df = pd.read_csv("04_data/csv/eden_quiz_data.csv", encoding='utf-8-sig')
        
        load_time = time.time() - start_time
        print(f"[OK] 데이터 로딩 시간: {load_time:.3f}초")
        
        # 메모리 사용량 추정
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        print(f"[OK] 메모리 사용량: {memory_usage:.2f}MB")
        
        # 필터링 성능 테스트
        start_time = time.time()
        filtered_df = df[df['희귀도'].str.contains('5★', na=False)]
        filter_time = time.time() - start_time
        print(f"[OK] 필터링 시간: {filter_time:.3f}초 ({len(filtered_df)}개 결과)")
        
        return load_time < 1.0 and filter_time < 0.1  # 1초, 0.1초 기준
        
    except Exception as e:
        print(f"[FAIL] 성능 테스트 실패: {e}")
        return False

def mobile_responsiveness_check():
    """모바일 반응형 요소 확인"""
    print("\n=== [반응형] 모바일 반응형 검사 ====")
    
    css_files = [
        "app_improved.py",
        "pages/1_룰렛_앱_개선.py", 
        "pages/2_퀴즈_앱_개선.py"
    ]
    
    mobile_features = [
        "@media (max-width: 768px)",  # 모바일 미디어 쿼리
        "use_container_width=True",   # 전체 너비 사용
        "initial_sidebar_state=\"collapsed\"",  # 사이드바 기본 숨김
        "layout=\"wide\""  # 와이드 레이아웃
    ]
    
    all_responsive = True
    
    for file_path in css_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_features = [feature for feature in mobile_features if feature in content]
            missing_features = [feature for feature in mobile_features if feature not in content]
            
            print(f"[모바일] {file_path}:")
            print(f"  [OK] 발견된 모바일 기능: {len(found_features)}/{len(mobile_features)}")
            
            if missing_features:
                print(f"  [WARN] 누락된 기능: {len(missing_features)}개")
                all_responsive = False
            else:
                print(f"  [OK] 모든 모바일 기능 포함됨")
        else:
            print(f"[FAIL] {file_path}: 파일을 찾을 수 없음")
            all_responsive = False
    
    return all_responsive

def generate_test_report():
    """종합 테스트 리포트 생성"""
    print("\n" + "="*60)
    print("[리포트] 종합 사용성 테스트 리포트")
    print("="*60)
    
    tests = [
        ("파일 존재성", test_file_existence),
        ("데이터 로딩", test_data_loading),
        ("이미지 처리", test_image_processing),
        ("Streamlit 구문", test_streamlit_syntax),
        ("성능", performance_test),
        ("모바일 반응형", mobile_responsiveness_check)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n[실행] {test_name} 테스트 실행 중...")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"[결과] {test_name} 테스트: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"[오류] {test_name} 테스트 오류: {e}")
    
    # 최종 결과
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "="*60)
    print("[요약] 최종 테스트 결과")
    print("="*60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {test_name}")
    
    print(f"\n[통계] 전체 성공률: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("[평가] 우수! 대부분의 테스트를 통과했습니다.")
        print("[권장] 배포 준비가 완료되었습니다.")
    elif success_rate >= 60:
        print("[평가] 양호! 일부 개선이 필요합니다.")
        print("[권장] 실패한 테스트를 확인하여 수정하세요.")
    else:
        print("[평가] 주의! 많은 개선이 필요합니다.")
        print("[권장] 기본 기능부터 다시 점검해보세요.")
    
    return success_rate >= 80

if __name__ == "__main__":
    print("[시작] 어나더에덴 미니게임 앱 - 사용성 테스트")
    print(f"[경로] 테스트 디렉토리: {os.getcwd()}")
    
    success = generate_test_report()
    
    if success:
        print("\n[완료] 모든 테스트 완료! 개선된 버전을 사용할 준비가 되었습니다.")
    else:
        print("\n[실패] 일부 테스트 실패. 문제를 수정 후 다시 테스트하세요.")
    
    sys.exit(0 if success else 1)