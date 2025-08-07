#!/usr/bin/env python3
"""
📱 모바일 친화적 네비게이션 바 컴포넌트
하단 고정 네비게이션으로 쉬운 접근성 제공
"""

import streamlit as st

def mobile_navigation():
    """모바일 친화적 하단 네비게이션 바"""
    
    st.markdown("""
    <style>
        /* 모바일 네비게이션 바 */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 0.5rem;
            z-index: 1000;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.3);
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        
        .nav-item {
            color: white;
            text-decoration: none;
            text-align: center;
            padding: 0.5rem;
            border-radius: 10px;
            transition: all 0.3s ease;
            cursor: pointer;
            flex: 1;
            max-width: 80px;
        }
        
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .nav-item.active {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .nav-icon {
            font-size: 1.5rem;
            display: block;
            margin-bottom: 0.2rem;
        }
        
        .nav-label {
            font-size: 0.7rem;
            display: block;
        }
        
        /* 메인 콘텐츠에 하단 여백 추가 */
        .main .block-container {
            padding-bottom: 120px;
        }
        
        /* 데스크톱에서는 숨김 */
        @media (min-width: 769px) {
            .mobile-nav {
                display: none;
            }
            
            .main .block-container {
                padding-bottom: 2rem;
            }
        }
        
        /* 모바일에서만 표시 */
        @media (max-width: 768px) {
            .mobile-nav {
                display: flex;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # 현재 페이지 확인
    current_page = st.session_state.get('current_page', 'home')
    
    # 네비게이션 바 HTML
    nav_html = f"""
    <div class="mobile-nav">
        <a class="nav-item {'active' if current_page == 'home' else ''}" onclick="window.location.href='/'">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">홈</span>
        </a>
        <a class="nav-item {'active' if current_page == 'roulette' else ''}" onclick="window.location.href='/1_룰렛_앱'">
            <span class="nav-icon">🎲</span>
            <span class="nav-label">룰렛</span>
        </a>
        <a class="nav-item {'active' if current_page == 'quiz' else ''}" onclick="window.location.href='/2_퀴즈_앱'">
            <span class="nav-icon">🎮</span>
            <span class="nav-label">퀴즈</span>
        </a>
        <a class="nav-item" onclick="window.scrollTo(0, 0)">
            <span class="nav-icon">⬆️</span>
            <span class="nav-label">위로</span>
        </a>
    </div>
    """
    
    st.markdown(nav_html, unsafe_allow_html=True)

def floating_action_button():
    """플로팅 액션 버튼 (모바일용)"""
    
    st.markdown("""
    <style>
        .fab {
            position: fixed;
            bottom: 100px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            border-radius: 50%;
            color: white;
            font-size: 1.5rem;
            border: none;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4);
            z-index: 999;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .fab:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
        }
        
        /* 데스크톱에서는 숨김 */
        @media (min-width: 769px) {
            .fab {
                display: none;
            }
        }
    </style>
    
    <button class="fab" onclick="window.location.reload()">
        🔄
    </button>
    """, unsafe_allow_html=True)

def breadcrumb_navigation(pages):
    """브레드크럼 네비게이션"""
    
    breadcrumb_html = """
    <div style="
        background: rgba(102, 126, 234, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.9rem;
    ">
    """
    
    for i, page in enumerate(pages):
        if i > 0:
            breadcrumb_html += " → "
        
        if i == len(pages) - 1:  # 현재 페이지
            breadcrumb_html += f'<strong style="color: #667eea;">{page}</strong>'
        else:
            breadcrumb_html += f'<span style="color: #666;">{page}</span>'
    
    breadcrumb_html += "</div>"
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

# 사용 예시
if __name__ == "__main__":
    # 테스트용 페이지
    st.title("모바일 네비게이션 테스트")
    
    breadcrumb_navigation(["홈", "룰렛 앱", "게임 결과"])
    
    st.markdown("""
    ## 테스트 콘텐츠
    
    이 페이지는 모바일 네비게이션을 테스트하기 위한 페이지입니다.
    
    - 모바일에서는 하단에 네비게이션 바가 표시됩니다.
    - 우측 하단에 새로고침 FAB 버튼이 있습니다.
    - 데스크톱에서는 이 요소들이 숨겨집니다.
    """)
    
    # 모바일 네비게이션 추가
    mobile_navigation()
    floating_action_button()