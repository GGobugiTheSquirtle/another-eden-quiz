#!/usr/bin/env python3
"""
🎮 어나더에덴 퀴즈쇼 - 개선된 사용자 경험
원터치 게임 시작 및 직관적 인터페이스
"""

import streamlit as st
import pandas as pd
import random
import time
import os
from pathlib import Path
import base64

# 경로 설정
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 페이지 설정
st.set_page_config(
    page_title="🎮 어나더에덴 퀴즈",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 개선된 CSS
st.markdown("""
<style>
    /* 메인 레이아웃 */
    .quiz-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 게임 모드 선택 */
    .game-mode-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .game-mode-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .game-mode-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .game-mode-card.selected {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* 퀴즈 컨테이너 */
    .quiz-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    .quiz-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 답안 버튼 */
    .answer-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .answer-btn {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        border-radius: 15px;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .answer-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }
    
    .answer-correct {
        background: rgba(76, 175, 80, 0.8) !important;
        border-color: #4CAF50 !important;
    }
    
    .answer-wrong {
        background: rgba(244, 67, 54, 0.8) !important;
        border-color: #F44336 !important;
    }
    
    /* 통계 패널 */
    .stats-panel {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
        margin: 1rem 0;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* 빠른 시작 버튼 */
    .quick-start-btn {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .quick-start-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .quiz-header {
            padding: 1.5rem;
        }
        
        .game-mode-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .game-mode-card {
            padding: 1.5rem;
        }
        
        .quiz-container {
            padding: 1.5rem;
            min-height: 300px;
        }
        
        .answer-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* 애니메이션 */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .animated {
        animation: slideIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

def safe_icon_to_data_uri(path):
    """이미지를 data URI로 변환"""
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
        return pd.DataFrame()

class QuickQuizGame:
    """간단한 퀴즈 게임 클래스"""
    
    def __init__(self, df):
        self.df = df
        self.score = 0
        self.total_questions = 0
        self.current_question = None
    
    def generate_question(self, quiz_type):
        """퀴즈 문제 생성"""
        if len(self.df) < 4:
            return None
        
        characters = self.df.sample(n=4).to_dict('records')
        correct_char = random.choice(characters)
        
        question_types = {
            "이름 맞추기": {
                "question": "이 캐릭터의 이름은?",
                "image_key": "캐릭터아이콘경로",
                "answer_key": "캐릭터명"
            },
            "속성 맞추기": {
                "question": "이 캐릭터의 속성은?",
                "image_key": "캐릭터아이콘경로", 
                "answer_key": "속성명리스트"
            },
            "무기 맞추기": {
                "question": "이 캐릭터의 무기는?",
                "image_key": "캐릭터아이콘경로",
                "answer_key": "무기명리스트"
            }
        }
        
        q_config = question_types.get(quiz_type, question_types["이름 맞추기"])
        
        return {
            "question": q_config["question"],
            "image": safe_icon_to_data_uri(correct_char.get(q_config["image_key"], "")),
            "options": [char.get(q_config["answer_key"], "N/A") for char in characters],
            "correct_answer": correct_char.get(q_config["answer_key"], "N/A"),
            "character_info": correct_char
        }

def main():
    # 데이터 로드
    df = load_character_data()
    if df.empty:
        st.error("데이터를 로드할 수 없습니다.")
        return

    # 게임 초기화
    if 'quiz_game' not in st.session_state:
        st.session_state.quiz_game = QuickQuizGame(df)
    
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    
    if 'current_quiz_type' not in st.session_state:
        st.session_state.current_quiz_type = None

    # 헤더
    st.markdown("""
    <div class="quiz-header animated">
        <h1>🎮 어나더에덴 퀴즈쇼</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">
            캐릭터에 대해 얼마나 알고 있는지 테스트해보세요!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 게임이 시작되지 않았을 때
    if not st.session_state.game_started:
        
        # 빠른 시작 섹션
        st.markdown("### 🚀 빠른 시작")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏷️ 이름 맞추기", key="quick_name", use_container_width=True):
                st.session_state.current_quiz_type = "이름 맞추기"
                st.session_state.game_started = True
                st.rerun()
        
        with col2:
            if st.button("🔥 속성 맞추기", key="quick_element", use_container_width=True):
                st.session_state.current_quiz_type = "속성 맞추기"
                st.session_state.game_started = True
                st.rerun()
        
        with col3:
            if st.button("⚔️ 무기 맞추기", key="quick_weapon", use_container_width=True):
                st.session_state.current_quiz_type = "무기 맞추기"
                st.session_state.game_started = True
                st.rerun()

        st.markdown("---")
        
        # 게임 모드 상세 선택
        st.markdown("### 🎯 게임 모드 선택")
        
        game_modes = [
            {
                "name": "🏷️ 이름 맞추기",
                "desc": "캐릭터 이미지를 보고 이름을 맞춰보세요",
                "difficulty": "⭐ 쉬움",
                "key": "이름 맞추기"
            },
            {
                "name": "🔥 속성 맞추기", 
                "desc": "캐릭터의 속성(Fire, Water 등)을 맞춰보세요",
                "difficulty": "⭐⭐ 보통",
                "key": "속성 맞추기"
            },
            {
                "name": "⚔️ 무기 맞추기",
                "desc": "캐릭터가 사용하는 무기를 맞춰보세요", 
                "difficulty": "⭐⭐⭐ 어려움",
                "key": "무기 맞추기"
            },
            {
                "name": "🎭 퍼스널리티 맞추기",
                "desc": "캐릭터의 성격 특성을 맞춰보세요",
                "difficulty": "⭐⭐⭐⭐ 고수",
                "key": "퍼스널리티 맞추기"
            }
        ]
        
        cols = st.columns(2)
        for i, mode in enumerate(game_modes):
            col = cols[i % 2]
            with col:
                if st.button(
                    f"**{mode['name']}**\n\n{mode['desc']}\n\n{mode['difficulty']}",
                    key=f"mode_{mode['key']}",
                    use_container_width=True,
                    help=f"{mode['desc']} - 난이도: {mode['difficulty']}"
                ):
                    st.session_state.current_quiz_type = mode['key']
                    st.session_state.game_started = True
                    st.rerun()

        # 통계 정보
        st.markdown("### 📊 게임 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-panel">
                <div class="stat-item">
                    <div class="stat-number">{len(df)}</div>
                    <div class="stat-label">총 캐릭터</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            five_star_count = len(df[df['희귀도'].str.contains('5★', na=False)]) if '희귀도' in df.columns else 0
            st.markdown(f"""
            <div class="stats-panel">
                <div class="stat-item">
                    <div class="stat-number">{five_star_count}</div>
                    <div class="stat-label">5성 캐릭터</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stats-panel">
                <div class="stat-item">
                    <div class="stat-number">4</div>
                    <div class="stat-label">퀴즈 모드</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stats-panel">
                <div class="stat-item">
                    <div class="stat-number">{st.session_state.quiz_game.score}</div>
                    <div class="stat-label">현재 점수</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # 게임이 시작된 상태
        game = st.session_state.quiz_game
        
        # 상단 컨트롤
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**현재 모드:** {st.session_state.current_quiz_type}")
            st.markdown(f"**점수:** {game.score} | **문제 수:** {game.total_questions}")
        
        with col2:
            if st.button("🔄 새 문제", key="new_question", use_container_width=True):
                st.session_state.current_question = game.generate_question(st.session_state.current_quiz_type)
                st.session_state.answer_selected = False
                st.rerun()
        
        with col3:
            if st.button("🏠 홈으로", key="go_home", use_container_width=True):
                st.session_state.game_started = False
                st.session_state.current_question = None
                st.rerun()

        # 퀴즈 컨테이너
        if 'current_question' not in st.session_state:
            st.session_state.current_question = game.generate_question(st.session_state.current_quiz_type)
            st.session_state.answer_selected = False

        if st.session_state.current_question:
            question = st.session_state.current_question
            
            st.markdown(f"""
            <div class="quiz-container quiz-active animated">
                <h2>{question['question']}</h2>
            """, unsafe_allow_html=True)
            
            # 이미지 표시
            if question['image']:
                st.markdown(f"""
                <div style="text-align: center; margin: 2rem 0;">
                    <img src="{question['image']}" style="max-width: 200px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 답안 선택
            if not st.session_state.get('answer_selected', False):
                st.markdown("### 답을 선택하세요:")
                
                cols = st.columns(2)
                for i, option in enumerate(question['options']):
                    col = cols[i % 2]
                    with col:
                        if st.button(
                            option,
                            key=f"answer_{i}",
                            use_container_width=True
                        ):
                            # 답안 처리
                            is_correct = option == question['correct_answer']
                            if is_correct:
                                game.score += 10
                                st.success(f"✅ 정답! +10점")
                            else:
                                st.error(f"❌ 틀렸습니다. 정답: {question['correct_answer']}")
                            
                            game.total_questions += 1
                            st.session_state.answer_selected = True
                            st.rerun()
            
            # 답안 선택 후 결과 표시
            if st.session_state.get('answer_selected', False):
                st.markdown("### 🎉 결과")
                
                char_info = question['character_info']
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**캐릭터 정보:**")
                    st.write(f"**이름:** {char_info.get('캐릭터명', 'N/A')}")
                    st.write(f"**희귀도:** {char_info.get('희귀도', 'N/A')}")
                    st.write(f"**속성:** {char_info.get('속성명리스트', 'N/A')}")
                    st.write(f"**무기:** {char_info.get('무기명리스트', 'N/A')}")
                
                with col2:
                    if st.button("➡️ 다음 문제", key="next_question", use_container_width=True):
                        st.session_state.current_question = game.generate_question(st.session_state.current_quiz_type)
                        st.session_state.answer_selected = False
                        st.rerun()

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>© WFS | 데이터 출처: Another Eden Wiki</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()