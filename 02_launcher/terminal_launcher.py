#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Another Eden 터미널 통합 런처
IDE에서 간편하게 프로젝트를 관리하고 실행할 수 있는 터미널 기반 런처
"""

import os
import sys
import subprocess
from pathlib import Path

def get_project_root():
    """프로젝트 루트 경로를 반환합니다."""
    return Path(__file__).parent.parent.resolve()

def run_scraper():
    """마스터 스크래퍼를 실행합니다."""
    print("🚀 마스터 스크래퍼 실행 중...")
    scraper_path = get_project_root() / "01_scraping" / "master_scraper.py"
    try:
        result = subprocess.run([sys.executable, str(scraper_path)], check=True)
        if result.returncode == 0:
            print("✅ 마스터 스크래퍼 실행 완료!")
        else:
            print("❌ 마스터 스크래퍼 실행 실패!")
    except subprocess.CalledProcessError as e:
        print(f"❌ 마스터 스크래퍼 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print(f"❌ 스크래퍼 파일을 찾을 수 없습니다: {scraper_path}")

def run_quiz_app():
    """퀴즈 앱을 실행합니다."""
    print("🎯 퀴즈 앱 실행 중...")
    app_path = get_project_root() / "03_apps" / "quiz" / "eden_quiz_app.py"
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 퀴즈 앱 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print(f"❌ 퀴즈 앱 파일을 찾을 수 없습니다: {app_path}")

def run_roulette_app():
    """룰렛 앱을 실행합니다."""
    print("🎰 룰렛 앱 실행 중...")
    app_path = get_project_root() / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 룰렛 앱 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print(f"❌ 룰렛 앱 파일을 찾을 수 없습니다: {app_path}")

def restructure_project():
    """프로젝트 구조를 재정비합니다."""
    print("🏗️ 프로젝트 구조 재정비 중...")
    script_path = get_project_root() / "restructure_project.py"
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        if result.returncode == 0:
            print("✅ 프로젝트 구조 재정비 완료!")
        else:
            print("❌ 프로젝트 구조 재정비 실패!")
    except subprocess.CalledProcessError as e:
        print(f"❌ 프로젝트 구조 재정비 중 오류 발생: {e}")
    except FileNotFoundError:
        print(f"❌ 구조 재정비 스크립트를 찾을 수 없습니다: {script_path}")

def show_menu():
    """메인 메뉴를 표시합니다."""
    print("\n" + "="*50)
    print("🔧 Another Eden 터미널 통합 런처")
    print("="*50)
    print("1. 🚀 마스터 스크래퍼 실행 (데이터 새로 생성)")
    print("2. 🎯 퀴즈 앱 실행")
    print("3. 🎰 룰렛 앱 실행")
    print("4. 🏗️ 프로젝트 구조 재정비")
    print("5. 🚪 종료")
    print("-"*50)

def main():
    """메인 실행 함수"""
    while True:
        show_menu()
        choice = input("실행할 작업의 번호를 입력하세요 (1-5): ").strip()
        
        if choice == '1':
            run_scraper()
        elif choice == '2':
            run_quiz_app()
        elif choice == '3':
            run_roulette_app()
        elif choice == '4':
            restructure_project()
        elif choice == '5':
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("❌ 잘못된 입력입니다. 1에서 5 사이의 숫자를 입력해주세요.")
        
        input("\n계속하려면 Enter 키를 누르세요...")

if __name__ == "__main__":
    main()
