#!/usr/bin/env python3
"""
🎲 어나더에덴 캐릭터 룰렛 - 개선된 사용자 경험
메인 영역 중심의 직관적 인터페이스
"""

import streamlit as st
import pandas as pd
import random
import os
import re
import base64
from pathlib import Path

# 경로 설정
BASE_DIR = Path(__file__).parent.parent.resolve()
PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 페이지 설정
st.set_page_config(
    page_title="🎲 어나더에덴 룰렛",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 개선된 CSS
st.markdown("""
<style>
    /* 컨테이너 */
    .main-content {
        max-width: 1400px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* 헤더 */
    .header-section {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    /* 컨트롤 패널 */
    .control-panel {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    /* 룰렛 버튼 */
    .roulette-btn {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        border: none;
        padding: 1.5rem 3rem;
        border-radius: 50px;
        font-size: 1.5rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4);
        width: 100%;
        margin: 1rem 0;
    }
    
    .roulette-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(255, 107, 107, 0.6);
    }
    
    /* 필터 카드 */
    .filter-card {
        background: rgba(255, 255, 255, 0.8);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* 결과 카드 */
    .winner-display {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.4);
        animation: pulse 1s ease-in-out;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* 캐릭터 그리드 */
    .character-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .character-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .character-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .character-card.winner {
        background: linear-gradient(135deg, #fff9e6, #fffbf0);
        border: 3px solid #FFD700;
    }
    
    /* 통계 */
    .stat-row {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        margin: 0.5rem;
        flex: 1;
        min-width: 120px;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .header-section {
            padding: 1.5rem;
        }
        
        .control-panel {
            padding: 1.5rem;
        }
        
        .roulette-btn {
            padding: 1rem 2rem;
            font-size: 1.2rem;
        }
        
        .character-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .stat-row {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

def safe_icon_to_data_uri(path):
    """이미지 파일을 data URI로 변환 (간단 버전)"""
    if not path or pd.isna(path):
        return ""
    
    try:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{data}"
    except:
        pass
    return ""

@st.cache_data
def load_character_data():
    """캐릭터 데이터 로드"""
    try:
        df = pd.read_csv(CSV_DIR / "eden_quiz_data.csv", encoding='utf-8-sig')
        return df.fillna('')
    except:
        st.error("데이터를 로드할 수 없습니다.")
        return pd.DataFrame()

def main():
    # 데이터 로드
    df = load_character_data()
    if df.empty:
        st.error("데이터 파일을 찾을 수 없습니다.")
        return

    # 헤더
    st.markdown("""
    <div class="header-section">
        <h1>🎲 어나더에덴 캐릭터 룰렛</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">
            필터를 설정하고 운명의 캐릭터를 뽑아보세요!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 통계 정보
    total_chars = len(df)
    five_star_count = len(df[df['희귀도'].str.contains('5★', na=False)]) if '희귀도' in df.columns else 0
    
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <div class="stat-number">{total_chars}</div>
            <div>총 캐릭터</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{five_star_count}</div>
            <div>5성 캐릭터</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">7</div>
            <div>필터 옵션</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 메인 컨트롤 패널
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # 필터 섹션을 메인 영역에 배치
    st.markdown("### 🎯 필터 설정")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        st.markdown("**희귀도 선택**")
        rarity_options = sorted(df['희귀도'].dropna().unique()) if '희귀도' in df.columns else []
        selected_rarity = st.multiselect(
            "희귀도", 
            rarity_options,
            key="rarity_filter",
            help="원하는 희귀도를 선택하세요"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        st.markdown("**속성 선택**")
        # 속성 추출 (쉼표로 구분된 값들 처리)
        all_elements = set()
        if '속성명리스트' in df.columns:
            for elements in df['속성명리스트'].dropna():
                all_elements.update([e.strip() for e in str(elements).split(',') if e.strip()])
        
        selected_elements = st.multiselect(
            "속성",
            sorted(list(all_elements)),
            key="element_filter",
            help="원하는 속성을 선택하세요"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        st.markdown("**무기 선택**")
        # 무기 추출
        all_weapons = set()
        if '무기명리스트' in df.columns:
            for weapons in df['무기명리스트'].dropna():
                all_weapons.update([w.strip() for w in str(weapons).split(',') if w.strip()])
        
        selected_weapons = st.multiselect(
            "무기",
            sorted(list(all_weapons)),
            key="weapon_filter",
            help="원하는 무기를 선택하세요"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 검색 옵션
    search_name = st.text_input(
        "🔍 캐릭터 이름 검색",
        placeholder="캐릭터 이름을 입력하세요...",
        help="부분 검색도 가능합니다"
    )

    # 필터링 로직
    filtered_df = df.copy()
    
    if selected_rarity:
        filtered_df = filtered_df[filtered_df['희귀도'].isin(selected_rarity)]
    
    if selected_elements:
        for element in selected_elements:
            filtered_df = filtered_df[filtered_df['속성명리스트'].str.contains(element, na=False)]
    
    if selected_weapons:
        for weapon in selected_weapons:
            filtered_df = filtered_df[filtered_df['무기명리스트'].str.contains(weapon, na=False)]
    
    if search_name:
        filtered_df = filtered_df[filtered_df['캐릭터명'].str.contains(search_name, case=False, na=False)]

    st.markdown('</div>', unsafe_allow_html=True)

    # 룰렛 버튼 (큰 버튼으로 메인 영역에 배치)
    st.markdown("### 🎰 룰렛 실행")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            f"🎲 룰렛 돌리기! ({len(filtered_df)}명 중에서)",
            key="main_roulette_btn",
            help=f"현재 필터된 {len(filtered_df)}명의 캐릭터 중에서 무작위 선택",
            use_container_width=True
        ):
            if not filtered_df.empty:
                winner = filtered_df.sample(1).iloc[0]
                st.session_state['roulette_winner'] = winner.to_dict()
                st.rerun()
            else:
                st.error("필터 조건에 맞는 캐릭터가 없습니다!")

    # 당첨자 표시
    if 'roulette_winner' in st.session_state and st.session_state['roulette_winner']:
        winner = st.session_state['roulette_winner']
        
        st.markdown("### 🎉 당첨 결과")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(f"""
            <div class="winner-display">
                <h2>🎊 축하합니다! 🎊</h2>
                <h1>{winner.get('캐릭터명', 'Unknown')}</h1>
                <p><strong>희귀도:</strong> {winner.get('희귀도', 'N/A')}</p>
                <p><strong>속성:</strong> {winner.get('속성명리스트', 'N/A')}</p>
                <p><strong>무기:</strong> {winner.get('무기명리스트', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 이미지 표시
        if winner.get('캐릭터아이콘경로'):
            image_uri = safe_icon_to_data_uri(winner['캐릭터아이콘경로'])
            if image_uri:
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center; margin: 2rem 0;">
                        <img src="{image_uri}" style="max-width: 200px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
                    </div>
                    """, unsafe_allow_html=True)

    # 캐릭터 목록 표시 (개선된 그리드)
    st.markdown(f"### 📋 캐릭터 목록 ({len(filtered_df)}명)")
    
    if not filtered_df.empty:
        # 페이지네이션
        items_per_page = 12
        total_pages = (len(filtered_df) - 1) // items_per_page + 1
        
        if total_pages > 1:
            current_page = st.selectbox(
                "페이지 선택",
                range(1, total_pages + 1),
                index=0,
                format_func=lambda x: f"페이지 {x} / {total_pages}"
            )
        else:
            current_page = 1
        
        # 현재 페이지 데이터
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        # 그리드로 캐릭터 표시
        cols = st.columns(4)
        winner_name = st.session_state.get('roulette_winner', {}).get('캐릭터명')
        
        for idx, (_, char) in enumerate(page_df.iterrows()):
            col = cols[idx % 4]
            
            is_winner = char['캐릭터명'] == winner_name
            card_class = "character-card winner" if is_winner else "character-card"
            
            with col:
                # 이미지
                image_uri = safe_icon_to_data_uri(char.get('캐릭터아이콘경로', ''))
                img_html = f'<img src="{image_uri}" style="width: 80px; height: 80px; border-radius: 10px; object-fit: cover;">' if image_uri else ""
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="text-align: center;">
                        {img_html}
                        <h4 style="margin: 10px 0 5px 0;">{char.get('캐릭터명', 'N/A')}</h4>
                        <p style="margin: 5px 0; font-size: 0.9rem; color: #666;">
                            {char.get('희귀도', 'N/A')}
                        </p>
                        <p style="margin: 5px 0; font-size: 0.8rem; color: #888;">
                            {char.get('속성명리스트', 'N/A')[:20]}...
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🔍 필터 조건에 맞는 캐릭터가 없습니다. 필터를 조정해보세요!")

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>© WFS | 데이터 출처: Another Eden Wiki</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()