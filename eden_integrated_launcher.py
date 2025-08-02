"""
🚀 Another Eden 통합 런처
데이터 수집부터 퀴즈쇼까지 모든 기능을 하나의 앱에서 관리
"""

import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="🎮 Another Eden 통합 런처",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .status-good {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .status-warning {
        color: #FF9800;
        font-weight: bold;
    }
    
    .status-error {
        color: #F44336;
        font-weight: bold;
    }
    
    .info-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FFD700;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_file_status():
    """프로젝트 파일들의 상태를 체크"""
    files_status = {}
    
    # 필수 파일들
    essential_files = {
        "eden_roulette_data.csv": "룰렛/퀴즈 데이터",
        "Matching_names.csv": "캐릭터명 매핑",
        "another_eden_characters_detailed.xlsx": "상세 캐릭터 데이터",
        "character_art/": "캐릭터 이미지 폴더"
    }
    
    # 새로 생성된 파일들
    new_files = {
        "eden_quiz_app.py": "퀴즈쇼 앱",
        "eden_personality_scraper.py": "개선된 스크레이퍼"
    }
    
    all_files = {**essential_files, **new_files}
    
    for file_path, description in all_files.items():
        if os.path.exists(file_path):
            if file_path.endswith('/'):
                # 디렉토리인 경우
                try:
                    file_count = len([f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))])
                    files_status[file_path] = {"status": "✅", "description": description, "details": f"({file_count}개 파일)"}
                except OSError:
                    files_status[file_path] = {"status": "⚠️", "description": description, "details": "(접근 불가)"}
            else:
                # 파일인 경우
                size = os.path.getsize(file_path)
                if size > 0:
                    files_status[file_path] = {"status": "✅", "description": description, "details": f"({size:,} bytes)"}
                else:
                    files_status[file_path] = {"status": "⚠️", "description": description, "details": "(빈 파일)"}
        else:
            files_status[file_path] = {"status": "❌", "description": description, "details": "(없음)"}
    
    return files_status

def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🎮 Another Eden 통합 런처</h1>
        <p>데이터 수집부터 퀴즈쇼까지 모든 기능을 한 곳에서!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 빠른 실행
    st.sidebar.header("🚀 빠른 실행")
    
    if st.sidebar.button("🎯 퀴즈쇼 시작", use_container_width=True):
        if os.path.exists("eden_quiz_app.py"):
            st.sidebar.success("퀴즈쇼 앱을 실행합니다...")
            st.sidebar.code("streamlit run eden_quiz_app.py --server.port 8502", language="bash")
        else:
            st.sidebar.error("eden_quiz_app.py 파일이 없습니다.")
    
    if st.sidebar.button("🎰 기존 룰렛 앱", use_container_width=True):
        if os.path.exists("streamlit_eden_restructure.py"):
            st.sidebar.success("룰렛 앱을 실행합니다...")
            st.sidebar.code("streamlit run streamlit_eden_restructure.py --server.port 8503", language="bash")
        else:
            st.sidebar.error("streamlit_eden_restructure.py 파일이 없습니다.")
    
    if st.sidebar.button("🔧 개선된 스크레이퍼", use_container_width=True):
        if os.path.exists("eden_personality_scraper.py"):
            st.sidebar.success("스크레이퍼를 실행합니다...")
            st.sidebar.code("python eden_personality_scraper.py", language="bash")
        else:
            st.sidebar.error("eden_personality_scraper.py 파일이 없습니다.")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚀 통합 데이터 생성", use_container_width=True, type="primary"):
        if os.path.exists("eden_personality_scraper.py"):
            st.sidebar.success("통합 데이터 생성을 시작합니다...")
            st.sidebar.code("python eden_personality_scraper.py --integrated", language="bash")
            st.sidebar.info("이 명령어는 모든 필요한 데이터를 한 번에 생성합니다!")
        else:
            st.sidebar.error("eden_personality_scraper.py 파일이 없습니다.")
    
    # 메인 컨텐츠
    tab1, tab2, tab3, tab4 = st.tabs(["📊 프로젝트 상태", "🎮 앱 런처", "🔧 도구", "📖 가이드"])
    
    with tab1:
        st.header("📊 프로젝트 파일 상태")
        
        files_status = check_file_status()
        
        # 상태 요약
        total_files = len(files_status)
        good_files = sum(1 for f in files_status.values() if f["status"] == "✅")
        warning_files = sum(1 for f in files_status.values() if f["status"] == "⚠️")
        error_files = sum(1 for f in files_status.values() if f["status"] == "❌")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("전체 파일", total_files)
        with col2:
            st.metric("정상", good_files, delta=None)
        with col3:
            st.metric("주의", warning_files, delta=None)
        with col4:
            st.metric("오류", error_files, delta=None)
        
        # 파일별 상세 상태
        st.subheader("파일별 상세 상태")
        for file_path, info in files_status.items():
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                st.write(info["status"])
            with col2:
                st.write(f"**{file_path}**")
                st.caption(info["description"])
            with col3:
                st.write(info["details"])
        
        # 권장 사항
        if error_files > 0:
            st.error(f"❌ {error_files}개 파일이 누락되었습니다. 스크레이퍼를 실행하여 데이터를 생성하세요.")
        elif warning_files > 0:
            st.warning(f"⚠️ {warning_files}개 파일에 주의가 필요합니다.")
        else:
            st.success("✅ 모든 파일이 정상적으로 준비되었습니다!")
    
    with tab2:
        st.header("🎮 애플리케이션 런처")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>🎯 퀴즈쇼 앱</h3>
                <p>새로 개발된 인터랙티브 퀴즈 게임</p>
            </div>
            """, unsafe_allow_html=True)
            
            if os.path.exists("eden_quiz_app.py"):
                st.success("✅ 파일 준비됨")
                if st.button("퀴즈쇼 실행", key="quiz_main", use_container_width=True):
                    st.code("streamlit run eden_quiz_app.py --server.port 8502")
                    st.info("위 명령어를 터미널에서 실행하세요!")
            else:
                st.error("❌ eden_quiz_app.py 파일 없음")
            
            st.markdown("**주요 기능:**")
            st.markdown("- 🏷️ 이름 맞추기")
            st.markdown("- ⭐ 희귀도 맞추기")
            st.markdown("- 🔥 속성 맞추기")
            st.markdown("- ⚔️ 무기 맞추기")
            st.markdown("- 👤 실루엣 퀴즈")
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>🎰 기존 룰렛 앱</h3>
                <p>캐릭터 필터링 및 룰렛 기능</p>
            </div>
            """, unsafe_allow_html=True)
            
            if os.path.exists("streamlit_eden_restructure.py"):
                st.success("✅ 파일 준비됨")
                if st.button("룰렛 앱 실행", key="roulette_main", use_container_width=True):
                    st.code("streamlit run streamlit_eden_restructure.py --server.port 8503")
                    st.info("위 명령어를 터미널에서 실행하세요!")
            else:
                st.error("❌ streamlit_eden_restructure.py 파일 없음")
            
            st.markdown("**주요 기능:**")
            st.markdown("- 🔍 캐릭터 필터링")
            st.markdown("- 🎰 슬롯머신 룰렛")
            st.markdown("- 🎴 캐릭터 카드 표시")
            st.markdown("- 📊 통계 정보")
    
    with tab3:
        st.header("🔧 개발 도구")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 데이터 수집")
            
            if os.path.exists("eden_personality_scraper.py"):
                st.success("✅ 개선된 스크레이퍼 준비됨")
                if st.button("Personality 스크레이퍼 실행", use_container_width=True):
                    st.code("python eden_personality_scraper.py")
                    st.info("Personalities 데이터를 포함한 완전한 스크레이핑을 수행합니다.")
            else:
                st.error("❌ eden_personality_scraper.py 파일 없음")
            
            st.markdown("**개선 사항:**")
            st.markdown("- ✨ Personalities 데이터 추가")
            st.markdown("- 🔄 자동 CSV 생성")
            st.markdown("- 📊 향상된 진행률 표시")
            st.markdown("- 🛡️ 에러 처리 강화")
            st.markdown("- 🚀 통합 데이터 생성 기능")
            
            st.markdown("---")
            
            # 통합 데이터 생성 섹션
            st.subheader("🚀 통합 데이터 생성")
            st.markdown("한 번에 모든 필요한 데이터를 생성합니다.")
            
            if st.button("통합 데이터 생성 실행", key="integrated_gen", use_container_width=True, type="primary"):
                st.code("python eden_personality_scraper.py --integrated", language="bash")
                st.info("""
                **생성되는 파일들:**
                - another_eden_characters_detailed.xlsx
                - eden_roulette_data_with_personalities.csv  
                - character_personalities.csv
                
                모든 파일이 자동으로 현재 디렉토리에 복사됩니다!
                """)
        
        with col2:
            st.subheader("📋 기존 도구들")
            
            existing_tools = [
                ("another_eden_gui_scraper copy 2.py", "최신 GUI 스크레이퍼"),
                ("eden_data_preprocess_gui_with personality.py", "데이터 전처리 도구"),
                ("통합적용.PY", "통합 적용 스크립트")
            ]
            
            for tool_file, description in existing_tools:
                if os.path.exists(tool_file):
                    st.success(f"✅ {tool_file}")
                    st.caption(description)
                else:
                    st.error(f"❌ {tool_file}")
    
    with tab4:
        st.header("📖 사용 가이드")
        
        st.markdown("""
        ## 🚀 빠른 시작 가이드
        
        ### 1단계: 데이터 수집
        
        **방법 1: 통합 데이터 생성 (권장)**
        ```bash
        python eden_personality_scraper.py --integrated
        ```
        - 모든 필요한 데이터를 한 번에 생성
        - 자동으로 현재 디렉토리에 파일 복사
        
        **방법 2: GUI 스크레이퍼**
        ```bash
        python eden_personality_scraper.py
        ```
        1. 출력 폴더 선택 후 "캐릭터 데이터 수집" 버튼 클릭
        2. Personalities 데이터를 포함한 완전한 데이터 수집 완료
        
        ### 2단계: 앱 실행
        1. **퀴즈쇼 앱**: 
           ```bash
           streamlit run eden_quiz_app.py --server.port 8502
           ```
        2. **룰렛 앱**: 
           ```bash
           streamlit run streamlit_eden_restructure.py --server.port 8503
           ```
        
        ### 3단계: 즐기기!
        - 🎯 다양한 퀴즈 모드로 캐릭터 지식 테스트
        - 🎰 룰렛으로 랜덤 캐릭터 뽑기
        - 🔍 필터링으로 원하는 캐릭터 찾기
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ## 🆕 새로운 기능들
        
        ### 🎮 퀴즈쇼 앱의 특징
        - **5가지 퀴즈 모드**: 이름, 희귀도, 속성, 무기, 실루엣
        - **실시간 점수 시스템**: 정답률 추적
        - **시각적 힌트**: 캐릭터 이미지 및 실루엣
        - **상세 정보 표시**: 정답 후 캐릭터 정보 제공
        
        ### 🔧 개선된 스크레이퍼
        - **Personalities 데이터**: 캐릭터별 성격 특성 정보
        - **자동 CSV 생성**: Excel → CSV 변환 자동화
        - **에러 처리 강화**: 네트워크 오류 대응 개선
        - **진행률 개선**: 더 정확한 스크레이핑 상태 표시
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ## 🛠️ 트러블슈팅
        
        ### 자주 발생하는 문제들
        
        **Q: eden_roulette_data.csv 파일이 없다고 나옵니다.**
        A: 스크레이퍼를 먼저 실행하여 데이터를 생성하세요.
        
        **Q: 캐릭터 이미지가 표시되지 않습니다.**
        A: character_art 폴더와 하위 이미지들이 있는지 확인하세요.
        
        **Q: Personalities 데이터가 비어있습니다.**
        A: 개선된 스크레이퍼(eden_personality_scraper.py)를 사용하세요.
        
        **Q: 포트 충돌로 앱이 실행되지 않습니다.**
        A: 다른 포트 번호를 사용하세요 (--server.port 8504)
        """)
        
        # 저작권 정보
        st.markdown("---")
        st.caption("""
        📊 데이터 출처: [Another Eden Wiki](https://anothereden.wiki/w/Another_Eden_Wiki)  
        🎮 모든 캐릭터 이미지의 저작권은 © WFS에 있습니다.  
        💻 이 도구는 팬 프로젝트이며 상업적 목적이 아닙니다.
        """)

if __name__ == "__main__":
    main()