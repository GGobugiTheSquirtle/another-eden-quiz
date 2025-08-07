#!/usr/bin/env python3
"""
🎮 어나더에덴 미니게임 런처 - 개선된 사용자 경험
직관적이고 접근성이 높은 인터페이스로 재설계
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# 페이지 설정 - 모바일 친화적
st.set_page_config(
    page_title="어나더에덴 미니게임",
    page_icon="🎮",
    layout="wide",  # 더 넓은 레이아웃
    initial_sidebar_state="collapsed"  # 사이드바 기본 숨김
)

# 커스텀 CSS - 모바일/PC 반응형
st.markdown("""
<style>
    /* 메인 컨테이너 최적화 */
    .main-container {
        padding: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* 게임 카드 디자인 */
    .game-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        cursor: pointer;
        border: none;
    }
    
    .game-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    .game-card h2 {
        margin: 0 0 1rem 0;
        font-size: 2rem;
    }
    
    .game-card p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* 빠른 액션 버튼 */
    .quick-action {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    
    .quick-action:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
    }
    
    /* 통계 카드 */
    .stat-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin: 0;
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .game-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        .game-card h2 {
            font-size: 1.5rem;
        }
        
        .quick-action {
            width: 100%;
            margin: 0.5rem 0;
        }
        
        .stat-number {
            font-size: 2rem;
        }
    }
    
    /* 애니메이션 */
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .animated {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

def load_stats():
    """통계 데이터 로드"""
    try:
        df = pd.read_csv('04_data/csv/eden_quiz_data.csv', encoding='utf-8-sig')
        total_chars = len(df)
        
        # 5성 캐릭터 수 계산
        five_star_count = len(df[df['희귀도'].str.contains('5★', na=False)])
        
        return {
            'total_characters': total_chars,
            'five_star_characters': five_star_count,
            'quiz_modes': 7,
            'image_count': 368
        }
    except:
        return {
            'total_characters': 373,
            'five_star_characters': 150,
            'quiz_modes': 7,
            'image_count': 368
        }

def main():
    # 헤더
    st.markdown("""
    <div class="main-container animated">
        <h1 style="text-align: center; color: #667eea; margin-bottom: 2rem;">
            🎮 어나더에덴 미니게임 플랫폼
        </h1>
        <p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">
            캐릭터 룰렛과 퀴즈 게임을 즐겨보세요!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 통계 로드
    stats = load_stats()
    
    # 빠른 시작 섹션
    st.markdown("### 🚀 바로 시작하기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎲 룰렛 돌리기", key="quick_roulette", help="바로 캐릭터 룰렛 시작"):
            st.switch_page("pages/1_룰렛_앱.py")
    
    with col2:
        if st.button("🎮 퀴즈 시작", key="quick_quiz", help="바로 퀴즈 게임 시작"):
            st.switch_page("pages/2_퀴즈_앱.py")

    st.markdown("---")
    
    # 게임 카드 섹션
    st.markdown("### 🎯 게임 선택")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="game-card" onclick="window.location.href='pages/1_룰렛_앱.py'">
            <h2>🎲 캐릭터 룰렛</h2>
            <p>🔥 속성, 희귀도, 무기로 필터링</p>
            <p>🎰 슬롯머신 애니메이션</p>
            <p>🎯 운명의 캐릭터를 뽑아보세요!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("룰렛 앱 시작 →", key="card_roulette", use_container_width=True):
            st.switch_page("pages/1_룰렛_앱.py")
    
    with col2:
        st.markdown("""
        <div class="game-card">
            <h2>🎮 퀴즈 게임</h2>
            <p>🏷️ 이름, 속성, 무기 맞추기</p>
            <p>👤 실루엣 퀴즈 도전</p>
            <p>📊 점수와 통계 추적</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("퀴즈 앱 시작 →", key="card_quiz", use_container_width=True):
            st.switch_page("pages/2_퀴즈_앱.py")

    st.markdown("---")
    
    # 통계 섹션
    st.markdown("### 📊 플랫폼 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card animated">
            <p class="stat-number">{stats['total_characters']}</p>
            <p class="stat-label">총 캐릭터</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card animated">
            <p class="stat-number">{stats['five_star_characters']}</p>
            <p class="stat-label">5성 캐릭터</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card animated">
            <p class="stat-number">{stats['quiz_modes']}</p>
            <p class="stat-label">퀴즈 모드</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card animated">
            <p class="stat-number">{stats['image_count']}</p>
            <p class="stat-label">캐릭터 이미지</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 최근 업데이트 정보
    st.markdown("### 📝 최근 업데이트")
    
    with st.expander("🆕 새로운 기능", expanded=False):
        st.markdown("""
        - ✅ **개선된 UI**: 모바일 친화적 인터페이스
        - ✅ **빠른 시작**: 메인 화면에서 바로 게임 시작
        - ✅ **반응형 디자인**: PC/모바일 최적화
        - ✅ **향상된 성능**: 더 빠른 로딩과 반응성
        """)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 2rem 0;">
        <p>© WFS | 데이터 출처: <a href="https://anothereden.wiki" target="_blank">Another Eden Wiki</a></p>
        <p style="font-size: 0.9rem;">모든 캐릭터 이미지의 저작권은 해당 소유자에게 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()