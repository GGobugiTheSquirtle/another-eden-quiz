#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 Another Eden 통합 파이프라인
스크래핑 → 데이터 정리 → 앱 실행까지 자연스럽게 연결
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import pandas as pd

class IntegratedPipeline:
    """통합 파이프라인 관리자"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.data_dir = self.project_root / "04_data"
        self.csv_dir = self.data_dir / "csv"
        self.image_dir = self.data_dir / "images" / "character_art"
        
    def check_dependencies(self):
        """필요한 디렉토리와 파일 확인"""
        print("🔍 의존성 확인 중...")
        
        # 디렉토리 확인
        required_dirs = [
            self.project_root / "01_scraping",
            self.project_root / "02_launcher", 
            self.project_root / "03_apps",
            self.data_dir,
            self.csv_dir,
            self.image_dir
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                print(f"❌ 디렉토리 없음: {dir_path}")
                return False
            else:
                print(f"✅ {dir_path.name}")
        
        return True
    
    def run_scraping(self):
        """스크래핑 실행"""
        print("\n📡 스크래핑 시작...")
        
        scraper_path = self.project_root / "01_scraping" / "master_scraper.py"
        if not scraper_path.exists():
            print(f"❌ 스크래퍼 파일 없음: {scraper_path}")
            return False
        
        try:
            result = subprocess.run([sys.executable, str(scraper_path)], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ 스크래핑 완료")
                return True
            else:
                print(f"❌ 스크래핑 실패: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ 스크래핑 시간 초과")
            return False
        except Exception as e:
            print(f"❌ 스크래핑 오류: {e}")
            return False
    
    def fix_data_issues(self):
        """데이터 문제 자동 수정"""
        print("\n🔧 데이터 문제 수정 중...")
        
        fix_script = self.project_root / "fix_data_issues.py"
        if not fix_script.exists():
            print(f"❌ 수정 스크립트 없음: {fix_script}")
            return False
        
        try:
            result = subprocess.run([sys.executable, str(fix_script)], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ 데이터 문제 수정 완료")
                return True
            else:
                print(f"❌ 데이터 수정 실패: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 데이터 수정 오류: {e}")
            return False
    
    def verify_data_integrity(self):
        """데이터 무결성 검증"""
        print("\n🔍 데이터 무결성 검증...")
        
        # CSV 파일 확인
        csv_files = [
            "eden_quiz_data_fixed.csv",
            "eden_roulette_data.csv", 
            "eden_roulette_data_with_personalities.csv"
        ]
        
        for csv_file in csv_files:
            csv_path = self.csv_dir / csv_file
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8-sig')
                    image_col = '캐릭터아이콘경로' if '캐릭터아이콘경로' in df.columns else 'image_path'
                    valid_images = df[image_col].notna() & (df[image_col] != '')
                    print(f"✅ {csv_file}: {len(df)}개 캐릭터, {valid_images.sum()}개 이미지")
                except Exception as e:
                    print(f"❌ {csv_file} 읽기 실패: {e}")
            else:
                print(f"⚠️ {csv_file} 파일 없음")
        
        # 이미지 파일 확인
        if self.image_dir.exists():
            image_count = len([f for f in self.image_dir.iterdir() if f.is_file()])
            print(f"✅ 이미지 파일: {image_count}개")
        else:
            print("❌ 이미지 디렉토리 없음")
    
    def run_app(self, app_type="quiz"):
        """앱 실행"""
        print(f"\n🎮 {app_type} 앱 실행...")
        
        if app_type == "quiz":
            app_path = self.project_root / "03_apps" / "quiz" / "eden_quiz_app.py"
        elif app_type == "roulette":
            app_path = self.project_root / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
        else:
            print(f"❌ 알 수 없는 앱 타입: {app_type}")
            return False
        
        if not app_path.exists():
            print(f"❌ 앱 파일 없음: {app_path}")
            return False
        
        try:
            print(f"🚀 {app_type} 앱을 시작합니다...")
            print(f"🌐 브라우저에서 http://localhost:8501 을 열어주세요")
            
            # Streamlit 앱 실행
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
            return True
        except KeyboardInterrupt:
            print("\n⏹️ 앱이 중단되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 앱 실행 오류: {e}")
            return False
    
    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        print("🔄 Another Eden 통합 파이프라인")
        print("=" * 50)
        
        # 1. 의존성 확인
        if not self.check_dependencies():
            print("❌ 의존성 확인 실패")
            return False
        
        # 2. 스크래핑 (필요시)
        print("\n📋 데이터 상태 확인...")
        csv_files = list(self.csv_dir.glob("*.csv"))
        image_files = list(self.image_dir.glob("*.png")) if self.image_dir.exists() else []
        
        if not csv_files or len(image_files) < 100:
            print("📡 데이터가 부족합니다. 스크래핑을 시작합니다...")
            if not self.run_scraping():
                print("❌ 스크래핑 실패")
                return False
        else:
            print(f"✅ 데이터 확인됨: {len(csv_files)}개 CSV, {len(image_files)}개 이미지")
        
        # 3. 데이터 문제 수정
        if not self.fix_data_issues():
            print("⚠️ 데이터 수정 중 일부 문제 발생")
        
        # 4. 데이터 무결성 검증
        self.verify_data_integrity()
        
        # 5. 앱 선택 및 실행
        print("\n🎮 실행할 앱을 선택하세요:")
        print("1. 퀴즈 앱")
        print("2. 룰렛 앱")
        print("3. 종료")
        
        while True:
            try:
                choice = input("\n선택 (1-3): ").strip()
                if choice == "1":
                    return self.run_app("quiz")
                elif choice == "2":
                    return self.run_app("roulette")
                elif choice == "3":
                    print("👋 파이프라인을 종료합니다.")
                    return True
                else:
                    print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
            except KeyboardInterrupt:
                print("\n👋 파이프라인을 종료합니다.")
                return True

def main():
    """메인 실행 함수"""
    pipeline = IntegratedPipeline()
    pipeline.run_full_pipeline()

if __name__ == "__main__":
    main() 