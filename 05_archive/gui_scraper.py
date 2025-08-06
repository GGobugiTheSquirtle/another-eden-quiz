#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 Another Eden 데이터 스크래퍼 GUI
Streamlit 기반 인터랙티브 스크래핑 도구
"""

import streamlit as st
import sys
import os
import time
import threading
import queue
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import subprocess

# 프로젝트 루트 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# 데이터 경로 설정
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"
SCRAPING_DIR = PROJECT_ROOT / "01_scraping"

st.set_page_config(
    page_title="📡 Another Eden 스크래퍼",
    page_icon="📡",
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
    
    .scraper-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .status-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .progress-container {
        background: rgba(0,0,0,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .log-container {
        background: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
        margin: 1rem 0;
    }
    
    .step-item {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    .step-completed {
        border-left-color: #28a745;
        background: rgba(40, 167, 69, 0.1);
    }
    
    .step-running {
        border-left-color: #ffc107;
        background: rgba(255, 193, 7, 0.1);
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

def check_prerequisites():
    """전제 조건 확인"""
    status = {
        'directories': True,
        'mapping_files': True,
        'internet': True,
        'details': {}
    }
    
    # 디렉토리 확인
    required_dirs = [CSV_DIR, IMAGE_DIR, SCRAPING_DIR]
    for dir_path in required_dirs:
        exists = dir_path.exists()
        status['details'][f'dir_{dir_path.name}'] = exists
        if not exists:
            status['directories'] = False
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # 매핑 파일 확인
    mapping_files = [
        CSV_DIR / "Matching_names.csv",
        SCRAPING_DIR / "personality_matching.csv"
    ]
    
    for file_path in mapping_files:
        exists = file_path.exists()
        status['details'][f'file_{file_path.name}'] = exists
        if not exists:
            status['mapping_files'] = False
    
    return status

def get_scraping_steps():
    """스크래핑 단계 정의"""
    return [
        {"id": "setup", "name": "환경 설정", "description": "디렉토리 생성 및 매핑 파일 로드"},
        {"id": "character_list", "name": "캐릭터 목록 수집", "description": "위키에서 캐릭터 목록 스크래핑"},
        {"id": "character_details", "name": "캐릭터 상세 정보", "description": "각 캐릭터의 상세 정보 수집"},
        {"id": "personality_data", "name": "성격 데이터", "description": "캐릭터 성격 정보 수집"},
        {"id": "image_download", "name": "이미지 다운로드", "description": "캐릭터 이미지 다운로드"},
        {"id": "csv_generation", "name": "CSV 생성", "description": "수집된 데이터를 CSV 파일로 저장"},
        {"id": "data_fixing", "name": "데이터 정리", "description": "이미지 매칭 및 데이터 검증"},
        {"id": "final_datasets", "name": "최종 데이터셋", "description": "앱용 최종 데이터 파일 생성"}
    ]

def run_scraper_process():
    """스크래퍼 프로세스 실행"""
    if 'scraper_running' not in st.session_state:
        st.session_state.scraper_running = False
    
    if 'scraper_logs' not in st.session_state:
        st.session_state.scraper_logs = []
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    scraper_path = SCRAPING_DIR / "master_scraper.py"
    
    if not scraper_path.exists():
        st.error(f"스크래퍼 파일을 찾을 수 없습니다: {scraper_path}")
        return
    
    # 스크래퍼 실행
    os.chdir(PROJECT_ROOT)
    
    try:
        st.session_state.scraper_running = True
        st.session_state.scraper_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 스크래퍼 시작...")
        
        # 백그라운드에서 스크래퍼 실행
        process = subprocess.Popen(
            [sys.executable, str(scraper_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        st.session_state.scraper_process = process
        return True
        
    except Exception as e:
        st.session_state.scraper_running = False
        st.session_state.scraper_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 오류: {e}")
        return False

def show_file_status():
    """파일 상태 표시"""
    st.markdown("### 📁 생성될 파일 목록")
    
    expected_files = [
        ("eden_quiz_data.csv", "기본 퀴즈 데이터"),
        ("eden_quiz_data_fixed.csv", "수정된 퀴즈 데이터 (앱에서 사용)"),
        ("eden_roulette_data.csv", "기본 룰렛 데이터"),
        ("eden_roulette_data_with_personalities.csv", "성격 포함 룰렛 데이터 (앱에서 사용)"),
        ("character_personalities.csv", "캐릭터 성격 데이터"),
        ("another_eden_characters_detailed.xlsx", "상세 정보 엑셀 파일")
    ]
    
    for filename, description in expected_files:
        file_path = CSV_DIR / filename
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            st.markdown(f"✅ **{filename}** - {description} ({size_mb:.2f} MB)")
        else:
            st.markdown(f"⏳ **{filename}** - {description} (생성 예정)")

def show_image_status():
    """이미지 상태 표시"""
    st.markdown("### 🖼️ 이미지 파일 상태")
    
    if IMAGE_DIR.exists():
        image_files = list(IMAGE_DIR.glob("*.png")) + list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.jpeg"))
        
        if image_files:
            st.markdown(f"📊 **총 {len(image_files)}개의 이미지 파일**")
            
            # 최근 다운로드된 파일 표시
            recent_files = sorted(image_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            st.markdown("**최근 다운로드된 파일:**")
            for file in recent_files:
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                st.markdown(f"- {file.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            st.markdown("📂 이미지 파일이 없습니다. 스크래핑을 실행하세요.")
    else:
        st.markdown("📂 이미지 디렉토리가 없습니다.")

def main():
    """메인 함수"""
    # 헤더
    st.markdown("""
    <div class="scraper-header">
        <h1>📡 Another Eden 데이터 스크래퍼</h1>
        <p>위키에서 최신 캐릭터 데이터를 수집하고 정리합니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 설정
    st.sidebar.markdown("## ⚙️ 스크래핑 설정")
    
    # 전제 조건 확인
    prerequisites = check_prerequisites()
    
    st.sidebar.markdown("### 📋 전제 조건")
    if prerequisites['directories']:
        st.sidebar.success("✅ 디렉토리 준비 완료")
    else:
        st.sidebar.warning("⚠️ 디렉토리 생성 중...")
    
    if prerequisites['mapping_files']:
        st.sidebar.success("✅ 매핑 파일 존재")
    else:
        st.sidebar.warning("⚠️ 매핑 파일 없음 (자동 생성됨)")
    
    # 스크래핑 옵션
    st.sidebar.markdown("### 🔧 옵션")
    download_images = st.sidebar.checkbox("이미지 다운로드", value=True)
    create_excel = st.sidebar.checkbox("엑셀 파일 생성", value=True)
    fix_data = st.sidebar.checkbox("데이터 정리 및 매칭", value=True)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 스크래핑은 시간이 오래 걸릴 수 있습니다. (10-30분)")
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 홈", "📊 상태", "📝 로그", "🔧 도구"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("## 🚀 스크래핑 실행")
            
            # 스크래핑 단계 표시
            steps = get_scraping_steps()
            current_step = st.session_state.get('current_step', 0)
            
            for i, step in enumerate(steps):
                if i < current_step:
                    st.markdown(f"""
                    <div class="step-item step-completed">
                        ✅ <strong>{step['name']}</strong><br>
                        <small>{step['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif i == current_step and st.session_state.get('scraper_running', False):
                    st.markdown(f"""
                    <div class="step-item step-running">
                        🔄 <strong>{step['name']}</strong><br>
                        <small>{step['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="step-item">
                        ⏳ <strong>{step['name']}</strong><br>
                        <small>{step['description']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 실행 버튼
            if not st.session_state.get('scraper_running', False):
                if st.button("📡 스크래핑 시작", type="primary", use_container_width=True):
                    if run_scraper_process():
                        st.rerun()
            else:
                st.warning("🔄 스크래핑이 진행 중입니다...")
                if st.button("⏹️ 중지", use_container_width=True):
                    if 'scraper_process' in st.session_state:
                        st.session_state.scraper_process.terminate()
                    st.session_state.scraper_running = False
                    st.rerun()
        
        with col2:
            st.markdown("## 📈 진행률")
            
            if st.session_state.get('scraper_running', False):
                progress = st.session_state.get('current_step', 0) / len(steps)
                st.progress(progress)
                st.markdown(f"**{progress*100:.0f}% 완료**")
            else:
                st.progress(0)
                st.markdown("**대기 중**")
            
            # 실시간 상태 업데이트
            if st.session_state.get('scraper_running', False):
                status_placeholder = st.empty()
                with status_placeholder.container():
                    st.markdown("### 🔄 실시간 상태")
                    if 'scraper_process' in st.session_state:
                        process = st.session_state.scraper_process
                        if process.poll() is None:
                            st.success("✅ 실행 중")
                        else:
                            st.info("✅ 완료")
                            st.session_state.scraper_running = False
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            show_file_status()
        
        with col2:
            show_image_status()
    
    with tab3:
        st.markdown("## 📝 스크래핑 로그")
        
        if 'scraper_logs' in st.session_state and st.session_state.scraper_logs:
            log_text = "\n".join(st.session_state.scraper_logs)
            st.markdown(f"""
            <div class="log-container">
                {log_text.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("로그가 없습니다. 스크래핑을 시작하면 로그가 표시됩니다.")
        
        # 로그 자동 새로고침
        if st.session_state.get('scraper_running', False):
            time.sleep(1)
            st.rerun()
    
    with tab4:
        st.markdown("## 🔧 유틸리티 도구")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📁 파일 관리")
            
            if st.button("데이터 폴더 열기"):
                os.startfile(str(CSV_DIR))
            
            if st.button("이미지 폴더 열기"):
                os.startfile(str(IMAGE_DIR))
            
            if st.button("로그 지우기"):
                st.session_state.scraper_logs = []
                st.rerun()
        
        with col2:
            st.markdown("### 🔄 데이터 관리")
            
            if st.button("기존 데이터 백업"):
                backup_dir = PROJECT_ROOT / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                # CSV 파일 백업
                for csv_file in CSV_DIR.glob("*.csv"):
                    if csv_file.exists():
                        import shutil
                        shutil.copy2(csv_file, backup_dir / csv_file.name)
                
                st.success(f"백업 완료: {backup_dir}")
            
            if st.button("캐시 정리"):
                st.cache_data.clear()
                st.success("캐시가 정리되었습니다!")
            
            if st.button("데이터 검증"):
                # 데이터 파일 검증
                required_files = [
                    "eden_quiz_data_fixed.csv",
                    "eden_roulette_data_with_personalities.csv"
                ]
                
                missing = []
                for file in required_files:
                    if not (CSV_DIR / file).exists():
                        missing.append(file)
                
                if missing:
                    st.error(f"누락된 파일: {', '.join(missing)}")
                else:
                    st.success("모든 필수 파일이 존재합니다!")

if __name__ == "__main__":
    main()
