#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Another Eden 퀴즈 & 룰렛 메인 런쳐
모듈화된 프로젝트 구조의 통합 실행기
"""

import sys
import os
from pathlib import Path
import subprocess

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

def run_quiz_app():
    """퀴즈 앱 실행"""
    quiz_path = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
    if quiz_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(quiz_path)])
    else:
        print("❌ 퀴즈 앱을 찾을 수 없습니다.")
        print(f"   경로: {quiz_path}")

def run_roulette_app():
    """룰렛 앱 실행"""
    roulette_path = PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    if roulette_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(roulette_path)])
    else:
        print("❌ 룰렛 앱을 찾을 수 없습니다.")
        print(f"   경로: {roulette_path}")

def run_scraper():
    """스크래퍼 실행"""
    scraper_path = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
    if scraper_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, str(scraper_path)])
    else:
        print("❌ 스크래퍼를 찾을 수 없습니다.")
        print(f"   경로: {scraper_path}")

def show_project_structure():
    """프로젝트 구조 표시"""
    print("📁 프로젝트 구조:")
    print("├── 01_scraping/              - 데이터 스크래핑")
    print("│   └── master_scraper.py     - 통합 마스터 스크래퍼")
    print("├── 02_launcher/              - 실행 런쳐")
    print("│   ├── terminal_launcher.py  - 터미널 통합 런쳐")
    print("│   └── eden_integrated_launcher.py - Streamlit 런쳐")
    print("├── 03_apps/                  - 앱 알맹이")
    print("│   ├── quiz/                 - 퀴즈 앱")
    print("│   └── roulette/             - 룰렛 앱")
    print("├── 04_data/                  - 데이터 파일")
    print("│   ├── csv/                  - CSV 데이터")
    print("│   └── images/               - 이미지 데이터")
    print("└── 05_archive/               - 아카이브")

def run_terminal_launcher():
    """터미널 런처 실행"""
    launcher_path = PROJECT_ROOT / "02_launcher" / "terminal_launcher.py"
    if launcher_path.exists():
        os.chdir(PROJECT_ROOT)
        subprocess.run([sys.executable, str(launcher_path)])
    else:
        print("❌ 터미널 런처를 찾을 수 없습니다.")
        print(f"   경로: {launcher_path}")

def main():
    """메인 메뉴"""
    print("\033[95m" + "🎮 Another Eden 퀴즈 & 룰렛" + "\033[0m")
    print("\033[94m" + "=" * 50 + "\033[0m")
    print("\033[93m" + "1. 🎯 퀴즈 앱 실행" + "\033[0m")
    print("\033[93m" + "2. 🎰 룰렛 앱 실행" + "\033[0m") 
    print("\033[93m" + "3. 📡 데이터 스크래퍼 실행" + "\033[0m")
    print("\033[93m" + "4. 🚀 터미널 통합 런처 실행" + "\033[0m")
    print("\033[93m" + "5. 📁 프로젝트 구조 보기" + "\033[0m")
    print("\033[93m" + "6. 🚪 종료" + "\033[0m")
    print("\033[94m" + "-" * 50 + "\033[0m")
    
    while True:
        try:
            choice = input("\033[96m" + "선택하세요 (1-6): " + "\033[0m").strip()
            
            if choice == "1":
                print("\033[92m" + "🎯 퀴즈 앱을 시작합니다..." + "\033[0m")
                run_quiz_app()
                break
            elif choice == "2":
                print("\033[92m" + "🎰 룰렛 앱을 시작합니다..." + "\033[0m")
                run_roulette_app()
                break
            elif choice == "3":
                print("\033[92m" + "📡 스크래퍼를 시작합니다..." + "\033[0m")
                run_scraper()
                break
            elif choice == "4":
                print("\033[92m" + "🚀 터미널 런처를 시작합니다..." + "\033[0m")
                run_terminal_launcher()
                break
            elif choice == "5":
                print("\033[92m" + "📁 프로젝트 구조를 표시합니다..." + "\033[0m")
                show_project_structure()
                print("\n" + "\033[94m" + "-" * 50 + "\033[0m")
            elif choice == "6":
                print("\033[91m" + "🚪 프로그램을 종료합니다. 안녕히 가세요!" + "\033[0m")
                break
            else:
                print("\033[91m" + "❌ 잘못된 선택입니다. 1-6 중에서 선택해주세요." + "\033[0m")
        except KeyboardInterrupt:
            print("\n\033[91m" + "🚪 프로그램을 종료합니다. 안녕히 가세요!" + "\033[0m")
            break

if __name__ == "__main__":
    main()
