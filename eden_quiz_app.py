"""
🎮 Another Eden 캐릭터 퀴즈쇼 앱
기존 룰렛 시스템을 확장하여 다양한 퀴즈 게임 모드를 제공합니다.
"""

import os
import pandas as pd
import streamlit as st
import random
import time
from typing import List, Dict, Any
import streamlit.components.v1 as components
import base64
import html
import re
from pathlib import Path
import unicodedata

# 프로젝트 루트 절대경로
BASE_DIR = Path(__file__).parent.resolve()

st.set_page_config(
    page_title="🎮 Another Eden 퀴즈쇼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .quiz-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .quiz-question {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .quiz-options {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .quiz-option {
        background: rgba(255, 255, 255, 0.2);
        padding: 1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .quiz-option:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: #FFD700;
    }
    
    .correct-answer {
        background: rgba(76, 175, 80, 0.8) !important;
        border-color: #4CAF50 !important;
    }
    
    .wrong-answer {
        background: rgba(244, 67, 54, 0.8) !important;
        border-color: #F44336 !important;
    }
    
    .score-display {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin: 1rem 0;
    }
    
    .character-hint {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

def safe_icon_to_data_uri(path: str) -> str:
    """아이콘 경로를 data URI로 안전하게 변환"""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"
    
    def normalize_path(p: str) -> str:
        p = unicodedata.normalize("NFKC", p)
        return p.replace("\\", "/").strip().lstrip("\ufeff").replace("\u00A0", "")
    
    path = normalize_path(path or '')
    if not path:
        return placeholder
    if path.startswith(("http://", "https://", "data:image")):
        return path
    
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path.lstrip("/\\"))
    
    if not os.path.exists(path):
        dir_path, file_name = os.path.split(path)
        try:
            if dir_path and os.path.isdir(dir_path):
                lc = file_name.lower()
                for f in os.listdir(dir_path):
                    if f.lower() == lc:
                        path = os.path.join(dir_path, f)
                        break
        except Exception:
            pass
        if not os.path.exists(path):
            return placeholder
    
    try:
        with open(path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{b64_str}"
    except Exception:
        return placeholder

@st.cache_data
def load_character_data():
    """캐릭터 데이터 로드"""
    csv_path = "eden_roulette_data.csv"
    if not os.path.exists(csv_path):
        st.error("eden_roulette_data.csv 파일이 없습니다. 먼저 스크레이퍼를 실행해주세요.")
        st.stop()
    
    df = pd.read_csv(csv_path).fillna('')
    return df

class QuizGame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.score = 0
        self.total_questions = 0
        self.current_question = None
        
    def get_random_characters(self, n: int = 4) -> List[Dict]:
        """랜덤 캐릭터 n명 선택"""
        if len(self.df) < n:
            return self.df.to_dict('records')
        return self.df.sample(n=n).to_dict('records')
    
    def generate_quiz_question(self, quiz_type: str) -> Dict[str, Any]:
        """퀴즈 문제 생성"""
        characters = self.get_random_characters(4)
        correct_char = random.choice(characters)
        
        if quiz_type == "guess_name":
            question = "이 캐릭터의 이름은 무엇일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
            
        elif quiz_type == "guess_rarity":
            question = f"{correct_char.get('캐릭터명', '')}의 희귀도는?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            # 가능한 희귀도 목록 생성
            rarities = list(set([char.get('희귀도', '') for char in self.df.to_dict('records') if char.get('희귀도', '')]))
            options = random.sample(rarities, min(4, len(rarities)))
            if correct_char.get('희귀도', '') not in options:
                options[0] = correct_char.get('희귀도', '')
            correct_answer = correct_char.get('희귀도', '')
            
        elif quiz_type == "guess_element":
            question = f"{correct_char.get('캐릭터명', '')}의 속성은?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            # 속성 리스트에서 선택
            all_elements = []
            for char in self.df.to_dict('records'):
                elements = str(char.get('속성명리스트', '')).split(',')
                all_elements.extend([elem.strip() for elem in elements if elem.strip()])
            unique_elements = list(set(all_elements))
            options = random.sample(unique_elements, min(4, len(unique_elements)))
            char_elements = str(correct_char.get('속성명리스트', '')).split(',')
            char_elements = [elem.strip() for elem in char_elements if elem.strip()]
            if char_elements and char_elements[0] not in options:
                options[0] = char_elements[0]
            correct_answer = char_elements[0] if char_elements else ''
            
        elif quiz_type == "guess_weapon":
            question = f"{correct_char.get('캐릭터명', '')}의 무기는?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            # 무기 리스트에서 선택
            all_weapons = []
            for char in self.df.to_dict('records'):
                weapons = str(char.get('무기명리스트', '')).split(',')
                all_weapons.extend([weapon.strip() for weapon in weapons if weapon.strip()])
            unique_weapons = list(set(all_weapons))
            options = random.sample(unique_weapons, min(4, len(unique_weapons)))
            char_weapons = str(correct_char.get('무기명리스트', '')).split(',')
            char_weapons = [weapon.strip() for weapon in char_weapons if weapon.strip()]
            if char_weapons and char_weapons[0] not in options:
                options[0] = char_weapons[0]
            correct_answer = char_weapons[0] if char_weapons else ''
        
        else:  # silhouette_quiz
            question = "실루엣을 보고 캐릭터를 맞춰보세요!"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
        
        random.shuffle(options)
        
        return {
            "question": question,
            "hint_image": hint_image,
            "options": options,
            "correct_answer": correct_answer,
            "character_info": correct_char
        }

def main():
    st.title("🎮 Another Eden 캐릭터 퀴즈쇼")
    st.markdown("---")
    
    # 데이터 로드
    df = load_character_data()
    
    # 세션 상태 초기화
    if 'quiz_game' not in st.session_state:
        st.session_state.quiz_game = QuizGame(df)
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None
    if 'quiz_answered' not in st.session_state:
        st.session_state.quiz_answered = False
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    
    # 사이드바 - 게임 설정
    st.sidebar.header("🎲 퀴즈 설정")
    
    quiz_type = st.sidebar.selectbox(
        "퀴즈 유형 선택",
        options=[
            "guess_name", "guess_rarity", "guess_element", 
            "guess_weapon", "silhouette_quiz"
        ],
        format_func=lambda x: {
            "guess_name": "🏷️ 이름 맞추기",
            "guess_rarity": "⭐ 희귀도 맞추기", 
            "guess_element": "🔥 속성 맞추기",
            "guess_weapon": "⚔️ 무기 맞추기",
            "silhouette_quiz": "👤 실루엣 퀴즈"
        }[x]
    )
    
    # 점수 표시
    game = st.session_state.quiz_game
    if game.total_questions > 0:
        accuracy = (game.score / game.total_questions) * 100
        st.sidebar.markdown(f"""
        <div class="score-display">
            📊 현재 점수<br>
            {game.score} / {game.total_questions}<br>
            정답률: {accuracy:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    # 새 문제 생성 버튼
    if st.sidebar.button("🎯 새 문제 생성", use_container_width=True):
        st.session_state.current_quiz = game.generate_quiz_question(quiz_type)
        st.session_state.quiz_answered = False
        st.session_state.show_result = False
        st.rerun()
    
    # 점수 초기화 버튼
    if st.sidebar.button("🔄 점수 초기화", use_container_width=True):
        st.session_state.quiz_game = QuizGame(df)
        st.session_state.current_quiz = None
        st.session_state.quiz_answered = False
        st.session_state.show_result = False
        st.rerun()
    
    # 퀴즈 표시
    if st.session_state.current_quiz:
        quiz = st.session_state.current_quiz
        
        st.markdown(f"""
        <div class="quiz-container">
            <div class="quiz-question">{quiz['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 힌트 이미지 표시
        if quiz['hint_image'] and quiz['hint_image'] != "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if quiz_type == "silhouette_quiz":
                    # 실루엣 효과 (CSS 필터 적용)
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="{quiz['hint_image']}" 
                             style="filter: brightness(0) saturate(100%); width: 200px; height: 200px; object-fit: contain;">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="{quiz['hint_image']}" 
                             style="width: 200px; height: 200px; object-fit: contain; border-radius: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
        
        # 선택지 표시
        if not st.session_state.quiz_answered:
            st.markdown("### 답을 선택하세요:")
            cols = st.columns(2)
            
            for i, option in enumerate(quiz['options']):
                col_idx = i % 2
                with cols[col_idx]:
                    if st.button(f"{chr(65+i)}. {option}", key=f"option_{i}", use_container_width=True):
                        st.session_state.quiz_answered = True
                        st.session_state.selected_answer = option
                        st.session_state.show_result = True
                        
                        # 점수 업데이트
                        game.total_questions += 1
                        if option == quiz['correct_answer']:
                            game.score += 1
                            st.session_state.answer_correct = True
                        else:
                            st.session_state.answer_correct = False
                        
                        st.rerun()
        
        # 결과 표시
        if st.session_state.show_result:
            if st.session_state.answer_correct:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 '{quiz['correct_answer']}'입니다.")
            
            # 캐릭터 상세 정보 표시
            char_info = quiz['character_info']
            st.markdown(f"""
            <div class="character-hint">
                <h4>📋 캐릭터 정보</h4>
                <ul>
                    <li><strong>이름:</strong> {char_info.get('캐릭터명', 'N/A')}</li>
                    <li><strong>희귀도:</strong> {char_info.get('희귀도', 'N/A')}</li>
                    <li><strong>속성:</strong> {char_info.get('속성명리스트', 'N/A')}</li>
                    <li><strong>무기:</strong> {char_info.get('무기명리스트', 'N/A')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # 첫 화면
        st.markdown("""
        <div class="quiz-container">
            <h2>🎮 어나더에덴 퀴즈쇼에 오신 것을 환영합니다!</h2>
            <p>사이드바에서 퀴즈 유형을 선택하고 '새 문제 생성' 버튼을 눌러 시작하세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 퀴즈 유형 설명
        st.markdown("### 🎯 퀴즈 유형별 설명")
        
        quiz_descriptions = {
            "🏷️ 이름 맞추기": "캐릭터 이미지를 보고 이름을 맞추는 기본 퀴즈",
            "⭐ 희귀도 맞추기": "캐릭터의 성급(★)을 맞추는 퀴즈",
            "🔥 속성 맞추기": "캐릭터의 속성(불, 물, 땅 등)을 맞추는 퀴즈",
            "⚔️ 무기 맞추기": "캐릭터가 사용하는 무기를 맞추는 퀴즈",
            "👤 실루엣 퀴즈": "캐릭터의 실루엣을 보고 이름을 맞추는 고난도 퀴즈"
        }
        
        for quiz_name, description in quiz_descriptions.items():
            st.markdown(f"- **{quiz_name}**: {description}")
    
    # 저작권 정보
    st.markdown("---")
    st.caption("""
    데이터 출처: [Another Eden Wiki](https://anothereden.wiki/w/Another_Eden_Wiki)  
    모든 캐릭터 이미지의 저작권은 © WFS에 있습니다.
    """)

if __name__ == "__main__":
    main()