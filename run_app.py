#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Another Eden 앱 실행기
간단하고 빠른 앱 실행
"""

import sys
import subprocess
from pathlib import Path

def run_quiz():
    """퀴즈 앱 실행"""
    quiz_path = Path(__file__).parent / "03_apps" / "quiz" / "eden_quiz_app.py"
    if quiz_path.exists():
        print("🎯 퀴즈 앱을 시작합니다...")
        print("🌐 브라우저에서 http://localhost:8501 을 열어주세요")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(quiz_path)])
    else:
        print("❌ 퀴즈 앱 파일을 찾을 수 없습니다.")

def run_roulette():
    """룰렛 앱 실행"""
    roulette_path = Path(__file__).parent / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    if roulette_path.exists():
        print("🎰 룰렛 앱을 시작합니다...")
        print("🌐 브라우저에서 http://localhost:8501 을 열어주세요")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(roulette_path)])
    else:
        print("❌ 룰렛 앱 파일을 찾을 수 없습니다.")

def main():
    print("🎮 Another Eden 앱 실행기")
    print("=" * 30)
    print("1. 퀴즈 앱")
    print("2. 룰렛 앱")
    print("3. 종료")
    print("-" * 30)
    
    while True:
        try:
            choice = input("선택하세요 (1-3): ").strip()
            if choice == "1":
                run_quiz()
                break
            elif choice == "2":
                run_roulette()
                break
            elif choice == "3":
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break

if __name__ == "__main__":
    main() 