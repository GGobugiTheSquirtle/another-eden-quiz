#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Another Eden 통합 런처 v2.0 (UI/UX 개선)
향상된 사용자 경험과 일관된 디자인을 제공하는 통합 런처
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import pandas as pd
import time

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 공통 UI 컴포넌트 임포트
try:
    from apps.shared.ui_components import apply_common_styles, render_header, render_card, render_feature_grid, render_data_summary, render_status_message, render_footer
except ImportError:
    # Fallback: 직접 import
    sys.path.insert(0, str(PROJECT_ROOT / "03_apps" / "shared"))
    try:
        from ui_components import apply_common_styles, render_header, render_card, render_feature_grid, render_data_summary, render_status_message, render_footer
    except ImportError:
        st.error("UI 컴포넌트를 로드할 수 없습니다.")
        st.stop()

# 페이지 설정
st.set_page_config(
    page_title="🚀 Another Eden 통합 런처",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 공통 스타일 적용
apply_common_styles()

def check_data_status():
    """데이터 파일 상태 확인"""
    data_dir = PROJECT_ROOT / "04_data"
    csv_dir = data_dir / "csv"
    images_dir = data_dir / "images" / "character_art"
    
    status = {
        "CSV 파일": 0,
        "캐릭터 이미지": 0,
        "백업 이미지": 0,
        "정리된 이미지": 0
    }
    
    # CSV 파일 확인
    csv_files = ["eden_quiz_data.csv", "eden_roulette_data.csv", "character_personalities.csv"]
    for csv_file in csv_files:
        if (csv_dir / csv_file).exists():
            status["CSV 파일"] += 1
    
    # 이미지 파일 확인
    if images_dir.exists():
        status["캐릭터 이미지"] = len(list(images_dir.glob("*.png")))
    
    # 백업 이미지 확인
    backup_dir = PROJECT_ROOT / "05_archive" / "old_versions" / "icons_for_tierlist_250723"
    if backup_dir.exists():
        status["백업 이미지"] = len(list(backup_dir.glob("*.png")))
    
    # 정리된 이미지 확인
    organized_dir = data_dir / "images" / "organized_character_art"
    if organized_dir.exists():
        for subdir in organized_dir.iterdir():
            if subdir.is_dir():
                status["정리된 이미지"] += len(list(subdir.glob("*.png")))
    
    return status

def run_scraper():
    """스크래퍼 실행"""
    try:
        scraper_path = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
        if not scraper_path.exists():
            render_status_message("스크래퍼 파일을 찾을 수 없습니다.", "error")
            return False
        
        with st.spinner("🔄 데이터 스크래핑 중... 잠시만 기다려주세요."):
            result = subprocess.run(
                [sys.executable, str(scraper_path)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=600  # 10분 타임아웃
            )
        
        if result.returncode == 0:
            render_status_message("데이터 스크래핑이 완료되었습니다!", "success")
            st.code(result.stdout, language="text")
            return True
        else:
            render_status_message(f"스크래핑 중 오류가 발생했습니다: {result.stderr}", "error")
            return False
    except subprocess.TimeoutExpired:
        render_status_message("스크래핑이 시간 초과되었습니다.", "warning")
        return False
    except Exception as e:
        render_status_message(f"예기치 못한 오류가 발생했습니다: {e}", "error")
        return False

def run_app(app_type):
    """앱 실행"""
    app_paths = {
        "quiz": PROJECT_ROOT / "03_apps" / "quiz" / "eden_quiz_app.py",
        "roulette": PROJECT_ROOT / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
    }
    
    app_path = app_paths.get(app_type)
    if not app_path or not app_path.exists():
        render_status_message(f"{app_type} 앱을 찾을 수 없습니다.", "error")
        return False
    
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(app_path)
        ], cwd=PROJECT_ROOT)
        
        render_status_message(f"{app_type.capitalize()} 앱이 새 창에서 실행됩니다.", "success")
        return True
    except Exception as e:
        render_status_message(f"앱 실행 중 오류가 발생했습니다: {e}", "error")
        return False

def show_home_page():
    """홈 페이지"""
    render_header("Another Eden 통합 런처", "캐릭터 퀴즈와 룰렛을 즐겨보세요!", "🚀")
    
    # 데이터 현황 확인
    data_status = check_data_status()
    render_data_summary(data_status)
    
    # 주요 기능 소개
    features = [
        {
            "icon": "🎯",
            "title": "캐릭터 퀴즈",
            "description": "다양한 퀴즈 모드로 캐릭터 지식을 테스트하세요!",
            "items": [
                "🏷️ 이름 맞추기 (3-4성 최대)",
                "🔥 속성 맞추기 (3-4성 최대)", 
                "⚔️ 무기 맞추기 (3-4성 최대)",
                "🎭 퍼스널리티 빈칸맞추기 (NEW!)",
                "📅 출시일 순서맞추기 (NEW!)",
                "👤 실루엣 퀴즈 (전체캐릭터)"
            ]
        },
        {
            "icon": "🎰",
            "title": "캐릭터 룰렛",
            "description": "필터를 설정하고 랜덤 캐릭터를 뽑아보세요!",
            "items": [
                "🔍 고급 필터링",
                "🎲 시각적 룰렛",
                "📊 상세 캐릭터 정보",
                "🎨 애니메이션 효과"
            ]
        },
        {
            "icon": "📡",
            "title": "데이터 스크래퍼",
            "description": "최신 캐릭터 정보를 자동으로 수집합니다.",
            "items": [
                "🔄 자동 데이터 수집",
                "🌐 한국어 번역",
                "🖼️ 이미지 다운로드",
                "🗂️ 자동 정리 (NEW!)"
            ]
        }
    ]
    
    render_feature_grid(features)
    
    # 빠른 실행 버튼들
    st.markdown("### 🚀 빠른 실행")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 퀴즈 앱 실행", use_container_width=True, type="primary"):
            run_app("quiz")
    
    with col2:
        if st.button("🎰 룰렛 앱 실행", use_container_width=True, type="primary"):
            run_app("roulette")
    
    with col3:
        if st.button("📡 데이터 업데이트", use_container_width=True):
            if run_scraper():
                st.rerun()  # 데이터 현황 업데이트

def show_data_management():
    """데이터 관리 페이지"""
    render_header("데이터 관리", "데이터 스크래핑 및 파일 관리", "📊")
    
    # 파일 업로드 섹션 (Cloud Streamlit 지원)
    st.markdown("### 📤 CSV 파일 업로드 (Cloud 환경용)")
    st.info("💡 **Cloud Streamlit 환경에서는 파일 업로드가 필요할 수 있습니다.**")
    
    uploaded_files = st.file_uploader(
        "CSV 파일들을 선택하세요",
        type=['csv'],
        accept_multiple_files=True,
        help="eden_quiz_data.csv, eden_roulette_data.csv, character_personalities.csv 등을 업로드하세요."
    )
    
    if uploaded_files:
        csv_dir = PROJECT_ROOT / "04_data" / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_count = 0
        for uploaded_file in uploaded_files:
            try:
                # 파일 저장
                file_path = csv_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ {uploaded_file.name} 업로드 완료")
                uploaded_count += 1
                
                # 파일 내용 미리보기
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    st.info(f"📊 {uploaded_file.name}: {len(df)}행, {len(df.columns)}컬럼")
                except:
                    st.warning(f"⚠️ {uploaded_file.name}: 파일 읽기 실패 (인코딩 문제일 수 있음)")
                    
            except Exception as e:
                st.error(f"❌ {uploaded_file.name} 업로드 실패: {str(e)}")
        
        if uploaded_count > 0:
            st.success(f"🎉 총 {uploaded_count}개 파일 업로드 완료!")
            st.info("💡 이제 퀴즈나 룰렛 앱을 실행해보세요.")
    
    # 파일 존재 여부 확인
    st.markdown("### 📁 현재 파일 상태")
    csv_files = [
        "eden_quiz_data.csv",
        "eden_roulette_data.csv", 
        "character_personalities.csv"
    ]
    
    for filename in csv_files:
        file_path = csv_dir / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                st.success(f"✅ {filename}: {len(df)}행")
            except:
                st.warning(f"⚠️ {filename}: 파일 존재하지만 읽기 실패")
        else:
            st.error(f"❌ {filename}: 파일 없음")
    
    # 스크래퍼 실행 섹션
    st.markdown("### 📡 데이터 스크래퍼 실행")
    st.info("💡 **로컬 환경에서만 실행하세요.** Cloud 환경에서는 파일 업로드를 사용하세요.")
    
    if st.button("🚀 스크래퍼 실행", type="primary"):
        try:
            # 스크래퍼 실행
            scraper_path = PROJECT_ROOT / "01_scraping" / "master_scraper.py"
            if scraper_path.exists():
                st.info("📡 스크래퍼를 실행하는 중...")
                
                # Python 스크립트 실행
                import subprocess
                result = subprocess.run([
                    sys.executable, str(scraper_path)
                ], capture_output=True, text=True, cwd=PROJECT_ROOT)
                
                if result.returncode == 0:
                    st.success("✅ 스크래퍼 실행 완료!")
                    st.info("📊 새로 생성된 데이터를 확인하세요.")
                else:
                    st.error(f"❌ 스크래퍼 실행 실패: {result.stderr}")
            else:
                st.error("❌ 스크래퍼 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"❌ 스크래퍼 실행 중 오류: {str(e)}")
    
    # 데이터 백업/복원
    st.markdown("### 💾 데이터 백업/복원")
    st.info("💡 **중요한 데이터는 백업해두세요.**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 데이터 백업"):
            try:
                import shutil
                from datetime import datetime
                
                backup_dir = PROJECT_ROOT / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                # CSV 파일들 백업
                for filename in csv_files:
                    src = csv_dir / filename
                    if src.exists():
                        dst = backup_dir / filename
                        shutil.copy2(src, dst)
                
                st.success(f"✅ 백업 완료: {backup_dir}")
            except Exception as e:
                st.error(f"❌ 백업 실패: {str(e)}")
    
    with col2:
        if st.button("🔄 데이터 복원"):
            st.info("�� 백업 기능은 개발 중입니다.")

def show_app_launcher():
    """앱 실행 페이지"""
    render_header("앱 실행", "원하는 앱을 선택하여 실행하세요", "🎮")
    
    # 앱 카드들
    col1, col2 = st.columns(2)
    
    with col1:
        render_card("""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #667eea; margin: 0 0 1rem 0;">🎯 캐릭터 퀴즈</h2>
            <p style="margin: 1rem 0;">다양한 퀴즈 모드로 캐릭터 지식을 테스트하세요!</p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>6가지 퀴즈 모드 (재구성 완료!)</li>
                <li>3-4성 최대 제한 (밸런스 개선)</li>
                <li>퍼스널리티 빈칸맞추기 (신규!)</li>
                <li>출시일 순서맞추기 (신규!)</li>
            </ul>
        </div>
        """)
        
        if st.button("🎯 퀴즈 앱 실행", use_container_width=True, type="primary", key="quiz_launch"):
            run_app("quiz")
    
    with col2:
        render_card("""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #667eea; margin: 0 0 1rem 0;">🎰 캐릭터 룰렛</h2>
            <p style="margin: 1rem 0;">필터를 설정하고 랜덤 캐릭터를 뽑아보세요!</p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>고급 필터링 시스템</li>
                <li>시각적 룰렛 애니메이션</li>
                <li>상세 캐릭터 정보</li>
                <li>반응형 디자인</li>
            </ul>
        </div>
        """)
        
        if st.button("🎰 룰렛 앱 실행", use_container_width=True, type="primary", key="roulette_launch"):
            run_app("roulette")

def main():
    """메인 함수"""
    # 사이드바 네비게이션
    st.sidebar.header("🚀 메뉴")
    
    pages = {
        "🏠 홈": show_home_page,
        "🎮 앱 실행": show_app_launcher,
        "📊 데이터 관리": show_data_management
    }
    
    selected_page = st.sidebar.selectbox("페이지 선택", list(pages.keys()))
    
    # 데이터 현황 사이드바 표시
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 데이터 현황")
    data_status = check_data_status()
    for key, value in data_status.items():
        st.sidebar.metric(key, value)
    
    # 빠른 링크
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 빠른 링크")
    
    if st.sidebar.button("🎯 퀴즈 앱", use_container_width=True):
        run_app("quiz")
    
    if st.sidebar.button("🎰 룰렛 앱", use_container_width=True):
        run_app("roulette")
    
    if st.sidebar.button("📡 데이터 업데이트", use_container_width=True):
        if run_scraper():
            st.rerun()
    
    # 선택된 페이지 렌더링
    pages[selected_page]()
    
    # 공통 푸터
    render_footer()

if __name__ == "__main__":
    main()