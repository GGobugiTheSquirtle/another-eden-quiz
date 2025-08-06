#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 Another Eden 퀴즈 & 룰렛 GUI 메인 런쳐
Streamlit 기반 통합 실행기 with 파일 경로 최적화
"""

import streamlit as st
import sys
import os
import subprocess
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# 데이터 경로 설정
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images"

st.set_page_config(
    page_title="🎮 Another Eden 런쳐",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .app-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .app-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .file-status {
        background: rgba(0,0,0,0.05);
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

def check_file_status():
    """파일 상태 확인"""
    status = {
        'data_files': {},
        'app_files': {},
        'scraper_files': {}
    }
    
    # 데이터 파일 확인
    data_files = [
        'eden_quiz_data_fixed.csv',
        'eden_roulette_data_with_personalities.csv',
        'Matching_names.csv',
        'character_personalities.csv'
    ]
    
    for file in data_files:
        file_path = CSV_DIR / file
        status['data_files'][file] = {
            'exists': file_path.exists(),
            'path': str(file_path),
            'size': file_path.stat().st_size if file_path.exists() else 0
        }
    
    # 앱 파일 확인
    app_files = {
        'quiz_app': PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py",
        'roulette_app': PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    }
    
    for name, file_path in app_files.items():
        status['app_files'][name] = {
            'exists': file_path.exists(),
            'path': str(file_path)
        }
    
    # 스크래퍼 파일 확인
    scraper_path = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
    status['scraper_files']['master_scraper'] = {
        'exists': scraper_path.exists(),
        'path': str(scraper_path)
    }
    
    return status

def run_app_with_fixed_paths(app_name, app_path):
    """경로 수정된 앱 실행"""
    if not app_path.exists():
        st.error(f"❌ {app_name}을 찾을 수 없습니다: {app_path}")
        return
    
    # 작업 디렉토리를 프로젝트 루트로 설정
    os.chdir(PROJECT_ROOT)
    
    try:
        # Streamlit 앱 실행
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", str(8501 if app_name == "퀴즈" else 8502)
        ])
        st.success(f"✅ {app_name} 앱이 시작되었습니다!")
        st.info(f"브라우저에서 http://localhost:{'8501' if app_name == '퀴즈' else '8502'}로 접속하세요.")
    except Exception as e:
        st.error(f"❌ {app_name} 앱 실행 실패: {e}")

def run_scraper():
    """스크래퍼 실행"""
    scraper_path = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
    if not scraper_path.exists():
        st.error(f"❌ 스크래퍼를 찾을 수 없습니다: {scraper_path}")
        return
    
    os.chdir(PROJECT_ROOT)
    
    try:
        # 스크래퍼를 백그라운드에서 실행
        process = subprocess.Popen([sys.executable, str(scraper_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        st.success("✅ 데이터 스크래퍼가 시작되었습니다!")
        st.info("스크래핑 진행 상황은 터미널에서 확인할 수 있습니다.")
        
        # 프로세스 상태 표시
        with st.expander("스크래퍼 실행 상태"):
            st.write(f"프로세스 ID: {process.pid}")
            st.write(f"실행 경로: {scraper_path}")
            
    except Exception as e:
        st.error(f"❌ 스크래퍼 실행 실패: {e}")

def show_project_status():
    """프로젝트 상태 표시"""
    st.markdown("## 📊 프로젝트 상태")
    
    status = check_file_status()
    
    # 데이터 파일 상태
    st.markdown("### 📁 데이터 파일")
    for file, info in status['data_files'].items():
        if info['exists']:
            size_mb = info['size'] / 1024 / 1024
            st.markdown(f"✅ **{file}** ({size_mb:.2f} MB)")
            st.markdown(f'<div class="file-status">{info["path"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"❌ **{file}** (없음)")
            st.markdown(f'<div class="file-status">{info["path"]}</div>', unsafe_allow_html=True)
    
    # 앱 파일 상태
    st.markdown("### 🎮 앱 파일")
    for name, info in status['app_files'].items():
        if info['exists']:
            st.markdown(f"✅ **{name}**")
        else:
            st.markdown(f"❌ **{name}** (없음)")
        st.markdown(f'<div class="file-status">{info["path"]}</div>', unsafe_allow_html=True)
    
    # 스크래퍼 파일 상태
    st.markdown("### 📡 스크래퍼 파일")
    for name, info in status['scraper_files'].items():
        if info['exists']:
            st.markdown(f"✅ **{name}**")
        else:
            st.markdown(f"❌ **{name}** (없음)")
        st.markdown(f'<div class="file-status">{info["path"]}</div>', unsafe_allow_html=True)

def main():
    """메인 함수"""
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🎮 Another Eden 퀴즈 & 룰렛</h1>
        <p>통합 런쳐 - 파일 경로 최적화 버전</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 빠른 실행
    st.sidebar.markdown("## 🚀 빠른 실행")
    
    if st.sidebar.button("🎯 퀴즈 앱 실행", use_container_width=True):
        quiz_path = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
        run_app_with_fixed_paths("퀴즈", quiz_path)
    
    if st.sidebar.button("🎰 룰렛 앱 실행", use_container_width=True):
        roulette_path = PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
        run_app_with_fixed_paths("룰렛", roulette_path)
    
    if st.sidebar.button("📡 데이터 스크래퍼 실행", use_container_width=True):
        run_scraper()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ℹ️ 정보")
    st.sidebar.info("이 런쳐는 모든 파일 경로를 자동으로 최적화하여 실행합니다.")
    
    # 메인 컨텐츠
    tab1, tab2, tab3 = st.tabs(["🏠 홈", "📊 상태", "🔧 도구"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="app-card">
                <h3>🎯 퀴즈 앱</h3>
                <p>Another Eden 캐릭터 퀴즈 게임</p>
                <ul>
                    <li>다양한 퀴즈 모드</li>
                    <li>진행률 표시</li>
                    <li>타이머 & 힌트 시스템</li>
                    <li>통계 및 점수 추적</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("퀴즈 앱 시작", key="quiz_main", use_container_width=True):
                quiz_path = PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py"
                run_app_with_fixed_paths("퀴즈", quiz_path)
        
        with col2:
            st.markdown("""
            <div class="app-card">
                <h3>🎰 룰렛 앱</h3>
                <p>Another Eden 캐릭터 룰렛 게임</p>
                <ul>
                    <li>슬롯머신 애니메이션</li>
                    <li>필터링 및 검색</li>
                    <li>캐릭터 카드 표시</li>
                    <li>사운드 이펙트</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("룰렛 앱 시작", key="roulette_main", use_container_width=True):
                roulette_path = PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
                run_app_with_fixed_paths("룰렛", roulette_path)
        
        st.markdown("---")
        
        st.markdown("""
        <div class="app-card">
            <h3>📡 데이터 스크래퍼</h3>
            <p>Another Eden 위키에서 최신 캐릭터 데이터를 수집합니다</p>
            <ul>
                <li>캐릭터 정보 스크래핑</li>
                <li>이미지 다운로드</li>
                <li>CSV 파일 생성</li>
                <li>데이터 정리 및 매칭</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("데이터 스크래퍼 실행", key="scraper_main", use_container_width=True):
            run_scraper()
    
    with tab2:
        show_project_status()
    
    with tab3:
        st.markdown("## 🔧 유틸리티 도구")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📁 파일 관리")
            
            if st.button("데이터 디렉토리 열기"):
                os.startfile(str(CSV_DIR))
            
            if st.button("이미지 디렉토리 열기"):
                os.startfile(str(IMAGE_DIR))
            
            if st.button("프로젝트 루트 열기"):
                os.startfile(str(PROJECT_ROOT))
        
        with col2:
            st.markdown("### 🔄 데이터 관리")
            
            if st.button("데이터 파일 검증"):
                status = check_file_status()
                missing_files = [f for f, info in status['data_files'].items() if not info['exists']]
                if missing_files:
                    st.error(f"누락된 파일: {', '.join(missing_files)}")
                    st.info("데이터 스크래퍼를 실행하여 파일을 생성하세요.")
                else:
                    st.success("모든 데이터 파일이 존재합니다!")
            
            if st.button("캐시 정리"):
                # Streamlit 캐시 정리
                st.cache_data.clear()
                st.success("캐시가 정리되었습니다!")

if __name__ == "__main__":
    main()
