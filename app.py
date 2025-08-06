"""
🎮 Another Eden 통합 앱 - 퀴즈 & 룰렛
퀴즈와 룰렛을 모두 포함하는 통합 Streamlit 애플리케이션
"""

import os
import pandas as pd
import streamlit as st
import random
import time
from typing import List, Dict, Any
import base64
from pathlib import Path
import unicodedata
import json
from datetime import datetime

# --- 경로 설정 ---
APP_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = APP_DIR
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images"

# 페이지 설정
st.set_page_config(
    page_title="🎮 Another Eden 통합 앱", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 스타일 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 1.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        animation: slideInDown 0.6s ease-out;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .quiz-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 1.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        animation: slideInDown 0.6s ease-out;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .roulette-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .filter-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .roulette-button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.1rem;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .roulette-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
    }
    
    .quiz-result {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        animation: slideInUp 0.5s ease-out;
    }
    
    .quiz-result.correct {
        background: linear-gradient(135deg, #4CAF50, #45a049); color: white;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    }
    
    .quiz-result.incorrect {
        background: linear-gradient(135deg, #f44336, #d32f2f); color: white;
        box-shadow: 0 8px 25px rgba(244, 67, 54, 0.4);
    }
    
    .quiz-result.partial {
        background: linear-gradient(135deg, #ff9800, #f57c00); color: white;
        box-shadow: 0 8px 25px rgba(255, 152, 0, 0.4);
    }
    
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .quiz-question {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        line-height: 1.6;
        padding: 0 1rem;
    }
    
    .character-hint {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .character-hint h4 {
        margin-top: 0;
        border-bottom: 2px solid #FFD700;
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    .character-hint ul {
        list-style: none;
        padding: 0;
    }
    
    .character-hint li {
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .silhouette-image {
        filter: brightness(0) contrast(0) saturate(0) !important;
        transition: all 1.2s ease-in-out;
        transform: scale(0.95);
        animation: none !important;
    }
    
    .silhouette-revealed {
        filter: brightness(1) contrast(1) saturate(1) !important;
        animation: silhouetteReveal 1.2s ease-in-out !important;
        transform: scale(1) !important;
        transition: all 1.2s ease-in-out !important;
    }
    
    @keyframes silhouetteReveal {
        0% {
            filter: brightness(0) contrast(0) saturate(0);
            transform: scale(0.95);
        }
        50% {
            filter: brightness(0.3) contrast(0.3) saturate(0.3);
            transform: scale(0.98);
        }
        100% {
            filter: brightness(1) contrast(1) saturate(1);
            transform: scale(1);
        }
    }
</style>
""", unsafe_allow_html=True)

def safe_icon_to_data_uri(path: str) -> str:
    """아이콘 경로를 data URI로 안전하게 변환"""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"
    
    if pd.isna(path) or not path:
        return placeholder
    
    path_str = str(path).strip()
    if path_str.startswith(("http://", "https://", "data:image")):
        return path_str
        
    # 절대 경로로 변환
    absolute_path = IMAGE_DIR / Path(path_str).name
    
    if not absolute_path.exists():
        return placeholder
    
    try:
        with open(absolute_path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{b64_str}"
    except Exception as e:
        return placeholder

@st.cache_data
def load_character_data():
    """캐릭터 데이터를 로드하고 캐싱합니다."""
    csv_path = CSV_DIR / "eden_quiz_data.csv"
    
    if not csv_path.exists():
        st.error(f"📋 퀴즈 데이터를 불러올 수 없습니다. '{csv_path}' 파일을 확인해주세요.")
        st.info("💡 프로젝트의 `04_data/csv` 폴더에 `eden_quiz_data.csv` 파일이 있는지 확인하세요.")
        return None

    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig').fillna('')
    except Exception as e:
        st.error(f"❌ 데이터 파일 읽기 실패: {e}")
        st.info("💡 파일 인코딩이 UTF-8이 맞는지 확인해주세요.")
        return None

    required_columns = ['캐릭터명', 'English_Name', '희귀도', '속성명리스트', '무기명리스트', '캐릭터아이콘경로']
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ 데이터 파일에 필수 컬럼이 부족합니다. ({', '.join(required_columns)} 필요)")
        return None

    # 출시일 컬럼이 없으면 빈 값으로 추가
    if '출시일' not in df.columns:
        df['출시일'] = ''
        
    st.success(f"✅ 캐릭터 데이터 로드 완료: {len(df)}명")
    return df

class QuizGame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.score = 0
        self.total_questions = 0
        self.combo_count = 0
        self.max_combo = 0
        self.time_limit = 30
        self.hints_used = 0
        self.session_stats = {
            'correct_answers': 0,
            'wrong_answers': 0,
            'total_time': 0,
            'category_stats': {}
        }
        self.retry_count = 0
        self.max_retries = 2
        self.silhouette_revealed = False
        self.answer_attempted = False
    
    def get_random_characters(self, n: int = 4, use_all_characters: bool = False) -> List[Dict]:
        """랜덤 캐릭터 n명 선택"""
        filtered_df = self.df.copy()
        
        # '캐릭터아이콘경로'가 비어있지 않은 캐릭터만 선택
        filtered_df = filtered_df[filtered_df['캐릭터아이콘경로'].notna() & (filtered_df['캐릭터아이콘경로'] != '')]

        if not use_all_characters:
            # 5성 캐릭터 제외 (난이도 조절)
            filtered_df = filtered_df[~filtered_df['희귀도'].str.contains('5★', na=False)]
        
        if len(filtered_df) < n:
            st.warning("퀴즈를 만들기에 캐릭터 데이터가 부족합니다.")
            return []
            
        return filtered_df.sample(n=n).to_dict('records')

    def generate_quiz_question(self, quiz_type: str) -> Dict[str, Any]:
        """퀴즈 문제 생성"""
        use_all = quiz_type == "silhouette_quiz"
        characters = self.get_random_characters(4, use_all_characters=use_all)
        
        if not characters:
            return {
                'question': "퀴즈 생성 실패", 'options': [], 'correct_answer': '',
                'hint_image': '', 'character_info': {}, 'quiz_type': quiz_type
            }

        correct_char = random.choice(characters)
        options = [char.get('캐릭터명', '') for char in characters]
        correct_answer = correct_char.get('캐릭터명', '')
        hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
        
        question_text = {
            "guess_name": "이 캐릭터의 이름은 무엇일까요?",
            "silhouette_quiz": "실루엣을 보고 캐릭터를 맞춰보세요!",
        }
        question = question_text.get(quiz_type, "캐릭터를 맞춰보세요!")

        random.shuffle(options)
        
        return {
            'question': question, 'options': options, 'correct_answer': correct_answer,
            'hint_image': hint_image, 'character_info': correct_char, 'quiz_type': quiz_type
        }

    def process_answer(self, selected_answer: str, correct_answer: str, quiz_type: str):
        """답안 처리 로직"""
        is_correct = (selected_answer == correct_answer)
        
        if is_correct:
            self.session_stats['correct_answers'] += 1
            self.combo_count += 1
            self.max_combo = max(self.max_combo, self.combo_count)
            self.score += 100 + (self.combo_count * 10) # 콤보 보너스
            self.silhouette_revealed = True
            return {'result': 'correct', 'message': '🎉 정답입니다!', 'show_next': True}
        else:
            self.session_stats['wrong_answers'] += 1
            self.combo_count = 0
            self.retry_count += 1
            self.silhouette_revealed = True # 틀려도 실루엣은 공개

            # 재시도 기회가 남아있는 경우
            if self.retry_count < self.max_retries:
                remaining = self.max_retries - self.retry_count
                return {
                    'result': 'partial', 
                    'message': f'❌ 아쉬워요! 재시도 기회가 {remaining}번 남았습니다.',
                    'show_next': False
                }
            # 모든 기회를 소진한 경우
            else:
                return {
                    'result': 'incorrect',
                    'message': f'💔 정답은 "{correct_answer}" 입니다.',
                    'show_next': True
                }

def show_quiz_page():
    """퀴즈 페이지 표시"""
    st.title("🎮 Another Eden 캐릭터 퀴즈쇼")
    st.markdown("---")

    df = load_character_data()
    if df is None:
        st.stop()

    if 'game' not in st.session_state:
        st.session_state.game = QuizGame(df)
    if 'quiz' not in st.session_state:
        st.session_state.quiz = None
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    if 'result' not in st.session_state:
        st.session_state.result = None

    game = st.session_state.game

    # 사이드바 UI
    st.sidebar.header("🎲 퀴즈 설정")
    quiz_type = st.sidebar.selectbox(
        "퀴즈 유형 선택",
        options=["guess_name", "silhouette_quiz"],
        format_func=lambda x: {
            "guess_name": "🏷️ 이름 맞추기",
            "silhouette_quiz": "👤 실루엣 퀴즈"
        }[x]
    )

    if st.sidebar.button("🎯 새 문제 생성", use_container_width=True):
        st.session_state.quiz = game.generate_quiz_question(quiz_type)
        st.session_state.answered = False
        st.session_state.result = None
        game.retry_count = 0
        game.silhouette_revealed = False
        st.rerun()

    if st.sidebar.button("🔄 게임 초기화", use_container_width=True):
        st.session_state.game = QuizGame(df)
        st.session_state.quiz = None
        st.session_state.answered = False
        st.session_state.result = None
        st.rerun()

    # 점수판
    st.sidebar.header("📊 점수판")
    if game.total_questions > 0:
        accuracy = (game.session_stats['correct_answers'] / game.total_questions) * 100
    else:
        accuracy = 0

    st.sidebar.markdown(f"""
        - **점수:** {game.score}
        - **정답률:** {accuracy:.1f}%
        - **연속 정답:** {game.combo_count} (최대: {game.max_combo})
        - **푼 문제:** {game.total_questions}
    """)
    
    # 메인 퀴즈 화면
    if st.session_state.quiz:
        quiz = st.session_state.quiz
        
        # 퀴즈 생성 실패 시
        if not quiz.get('options'):
            st.error("퀴즈를 생성하는 데 문제가 발생했습니다. 데이터를 확인하거나 앱을 재시작해주세요.")
            st.stop()

        # 퀴즈 컨테이너
        with st.container():
            st.markdown(f'<div class="quiz-container"><div class="quiz-question">{quiz["question"]}</div></div>', unsafe_allow_html=True)
            
            # 실루엣 이미지 처리
            img_class = "silhouette-image"
            if quiz['quiz_type'] == 'silhouette_quiz' and game.silhouette_revealed:
                img_class = "silhouette-revealed"

            # 이미지 표시
            if quiz['hint_image']:
                st.markdown(f'<div style="text-align: center;"><img src="{quiz["hint_image"]}" class="{img_class}" style="max-width: 200px; border-radius: 15px; margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

        # 답변 전: 선택지 버튼 표시
        if not st.session_state.answered:
            cols = st.columns(2)
            for i, option in enumerate(quiz['options']):
                with cols[i % 2]:
                    if st.button(option, key=f"option_{i}", use_container_width=True):
                        game.total_questions += 1
                        st.session_state.result = game.process_answer(option, quiz['correct_answer'], quiz['quiz_type'])
                        st.session_state.answered = True
                        st.rerun()
        
        # 답변 후: 결과 표시
        if st.session_state.answered and st.session_state.result:
            result = st.session_state.result
            st.markdown(f"<div class='quiz-result {result['result']}'>{result['message']}</div>", unsafe_allow_html=True)
            
            # 정답/오답 시 캐릭터 정보 카드 표시
            if result['result'] in ['correct', 'incorrect']:
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

            # 다음 단계 버튼
            if result['show_next']:
                if st.button("⏭️ 다음 문제", use_container_width=True):
                    st.session_state.quiz = None
                    st.session_state.answered = False
                    st.session_state.result = None
                    st.rerun()
            else: # 재시도 기회가 남은 경우
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🔄 다시 시도", use_container_width=True):
                        st.session_state.answered = False
                        st.session_state.result = None
                        st.rerun()
                with c2:
                    if st.button("⏭️ 포기하고 다음 문제", use_container_width=True):
                        st.session_state.quiz = None
                        st.session_state.answered = False
                        st.session_state.result = None
                        st.rerun()

    else:
        # 시작 화면
        st.markdown("""
        <div class="quiz-container">
            <h2>🎮 어나더에덴 퀴즈쇼에 오신 것을 환영합니다!</h2>
            <p>왼쪽 사이드바에서 퀴즈 유형을 선택하고 '새 문제 생성' 버튼을 눌러 시작하세요.</p>
        </div>
        """, unsafe_allow_html=True)

def show_roulette_page():
    """룰렛 페이지 표시"""
    st.title("🎲 Another Eden 캐릭터 룰렛")
    st.markdown("---")
    
    # 룰렛 기능 구현
    st.markdown("""
    <div class="roulette-container">
        <h2>🎲 캐릭터 룰렛</h2>
        <p>랜덤으로 캐릭터를 선택해보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 간단한 룰렛 구현
    df = load_character_data()
    if df is not None:
        if st.button("🎰 룰렛 돌리기", use_container_width=True, key="roulette_spin"):
            # 랜덤 캐릭터 선택
            random_char = df.sample(n=1).iloc[0]
            
            st.markdown(f"""
            <div class="roulette-container">
                <h3>🎉 당첨된 캐릭터!</h3>
                <h2>{random_char['캐릭터명']}</h2>
                <p><strong>희귀도:</strong> {random_char['희귀도']}</p>
                <p><strong>속성:</strong> {random_char['속성명리스트']}</p>
                <p><strong>무기:</strong> {random_char['무기명리스트']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 캐릭터 이미지 표시
            if random_char['캐릭터아이콘경로']:
                image_uri = safe_icon_to_data_uri(random_char['캐릭터아이콘경로'])
                st.markdown(f"""
                <div style="text-align: center;">
                    <img src="{image_uri}" style="max-width: 200px; border-radius: 15px; margin: 1rem 0;">
                </div>
                """, unsafe_allow_html=True)

def main():
    """메인 함수"""
    st.title("🎮 Another Eden 통합 앱")
    st.markdown("---")
    
    # 사이드바에서 페이지 선택
    page = st.sidebar.selectbox(
        "📱 페이지 선택",
        ["🏠 홈", "🎮 퀴즈", "🎲 룰렛"]
    )
    
    if page == "🏠 홈":
        st.markdown("""
        <div class="main-container">
            <h1>🎮 Another Eden 통합 앱에 오신 것을 환영합니다!</h1>
            <p>왼쪽 사이드바에서 원하는 기능을 선택하세요.</p>
            <br>
            <h3>📱 사용 가능한 기능</h3>
            <ul style="text-align: left; display: inline-block;">
                <li>🎮 <strong>퀴즈</strong> - 캐릭터 이름 맞추기 및 실루엣 퀴즈</li>
                <li>🎲 <strong>룰렛</strong> - 랜덤 캐릭터 선택</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    elif page == "🎮 퀴즈":
        show_quiz_page()
        
    elif page == "🎲 룰렛":
        show_roulette_page()

    # 저작권 정보
    st.markdown("---")
    st.caption("데이터 출처: Another Eden Wiki | 모든 캐릭터 이미지의 저작권은 © WFS에 있습니다.")

if __name__ == "__main__":
    main()