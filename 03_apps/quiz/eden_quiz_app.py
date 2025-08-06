#!/usr/bin/env python3
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
import base64
from pathlib import Path
import unicodedata
import json
from datetime import datetime

# --- 경로 설정 ---
APP_DIR = Path(__file__).parent.parent.parent.resolve()
PROJECT_ROOT = APP_DIR
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 페이지 설정
st.set_page_config(
    page_title="🎮 Another Eden 퀴즈쇼", 
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
    
    /* 모바일 반응형 개선 */
    @media (max-width: 768px) {
        .quiz-container {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        .quiz-options {
            grid-template-columns: 1fr !important;
            gap: 1rem !important;
        }
        .quiz-question {
            font-size: 1.4rem !important;
        }
        .quiz-option {
            padding: 1rem !important;
            font-size: 1rem !important;
        }
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
    
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .silhouette-image {
        filter: brightness(0);
        transition: filter 0.5s ease-in-out;
    }
    
    .silhouette-image.revealed {
        filter: brightness(1);
    }
    
    .quiz-options {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .quiz-option {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .quiz-option:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
    }
    
    .quiz-option.correct {
        background: rgba(76, 175, 80, 0.3);
        border-color: #4CAF50;
        animation: pulse 0.6s ease-in-out;
    }
    
    .quiz-option.incorrect {
        background: rgba(244, 67, 54, 0.3);
        border-color: #F44336;
        animation: shake 0.6s ease-in-out;
    }
    
    .quiz-question {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .character-hint {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .character-hint h4 {
        color: #FFD700;
        margin-bottom: 1rem;
    }
    
    .character-hint ul {
        list-style: none;
        padding: 0;
    }
    
    .character-hint li {
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    .score-display {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .timer-display {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .stat-card h3 {
        color: #FFD700;
        margin-bottom: 0.5rem;
    }
    
    .stat-card p {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True) 

# --- 유틸리티 함수들 ---
def normalize_text(text: str) -> str:
    """텍스트 정규화 (한글/영문 혼용 지원)"""
    if pd.isna(text):
        return ""
    
    # 유니코드 정규화
    normalized = unicodedata.normalize('NFKC', str(text))
    
    # 공백 제거 및 소문자 변환
    cleaned = normalized.strip().lower()
    
    return cleaned

def safe_icon_to_data_uri(path: str) -> str:
    """안전한 아이콘 경로를 data URI로 변환"""
    if pd.isna(path) or not path:
        return ""
    
    try:
        # 경로 정규화
        icon_path = Path(path)
        
        # 상대 경로인 경우 절대 경로로 변환
        if not icon_path.is_absolute():
            icon_path = IMAGE_DIR / icon_path.name
        
        if icon_path.exists():
            with open(icon_path, 'rb') as f:
                image_data = f.read()
                mime_type = 'image/png' if icon_path.suffix.lower() == '.png' else 'image/jpeg'
                encoded = base64.b64encode(image_data).decode()
                return f"data:{mime_type};base64,{encoded}"
        else:
            # 파일이 없으면 기본 이미지 반환
            return ""
    except Exception as e:
        print(f"이미지 로딩 오류: {e}")
        return ""

@st.cache_data
def load_character_data():
    """캐릭터 데이터 로드 (개선된 경로 처리)"""
    # 다양한 경로 시도
    possible_paths = [
        CSV_DIR / "eden_quiz_data.csv",
        CSV_DIR / "eden_roulette_data.csv", 
        CSV_DIR / "character_personalities.csv",
        PROJECT_ROOT / "04_data" / "csv" / "eden_quiz_data.csv",
        PROJECT_ROOT / "04_data" / "csv" / "eden_roulette_data.csv",
        Path("04_data/csv/eden_quiz_data.csv"),
        Path("04_data/csv/eden_roulette_data.csv"),
        Path("eden_quiz_data.csv"),
        Path("eden_roulette_data.csv"),
        Path("character_personalities.csv")
    ]
    
    # Streamlit Cloud 환경 감지
    is_cloud = os.environ.get('STREAMLIT_SHARING', False) or '/app' in str(Path.cwd())
    
    if is_cloud:
        cloud_paths = [
            Path("/app/04_data/csv/eden_quiz_data.csv"),
            Path("/app/04_data/csv/eden_roulette_data.csv"),
            Path("/app/csv/eden_quiz_data.csv"),
            Path("/app/csv/eden_roulette_data.csv"),
            Path("/tmp/04_data/csv/eden_quiz_data.csv"),
            Path("/tmp/04_data/csv/eden_roulette_data.csv")
        ]
        possible_paths.extend(cloud_paths)
    
    # 파일 찾기
    csv_path = None
    for path in possible_paths:
        if path.exists():
            csv_path = path
            break
    
    if not csv_path:
        st.error("📋 데이터 파일을 찾을 수 없습니다.")
        st.info("💡 다음 중 하나의 파일이 필요합니다:")
        st.info("- eden_quiz_data.csv")
        st.info("- eden_roulette_data.csv") 
        st.info("- character_personalities.csv")
        st.info("📡 메인 런쳐에서 '데이터 스크래퍼 실행'을 클릭하여 데이터를 생성하세요.")
        st.stop()
    
    try:
        # CSV 파일 로드
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # 필수 컬럼 확인
        required_columns = ['캐릭터명', 'English_Name', '희귀도', '속성명리스트', '무기명리스트']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ 필수 컬럼이 누락되었습니다: {missing_columns}")
            st.info("💡 스크래퍼를 다시 실행하여 올바른 형식의 데이터를 생성하세요.")
            st.stop()
        
        # 출시일 컬럼이 없는 경우 대비
        if '출시일' not in df.columns:
            df['출시일'] = ''
        
        # 퍼스널리티 컬럼이 없는 경우 대비
        if '퍼스널리티리스트' not in df.columns:
            df['퍼스널리티리스트'] = ''
        
        st.success(f"✅ 캐릭터 데이터 로드 완료: {len(df)}명의 캐릭터")
        return df
        
    except Exception as e:
        st.error(f"❌ 데이터 로딩 중 오류 발생: {str(e)}")
        st.info("💡 파일 형식을 확인하거나 스크래퍼를 다시 실행하세요.")
        st.stop() 

class QuizGame:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.score = 0
        self.total_questions = 0
        self.current_question = None
        self.combo_count = 0
        self.max_combo = 0
        self.start_time = None
        self.question_start_time = None
        self.time_limit = 30  # 30초 제한
        self.hints_used = 0
        self.session_stats = {
            'correct_answers': 0,
            'wrong_answers': 0,
            'total_time': 0,
            'category_stats': {}
        }
        # 개선된 시스템 변수들
        self.retry_count = 0
        self.max_retries = 2  # 최대 2회 재시도
        self.partial_score = 0.5  # 부분 점수 (50%)
        self.retry_penalty = 0.3  # 재시도 페널티 (30% 감점)
        self.silhouette_revealed = False
        self.current_question_data = None
        self.answer_attempted = False
        # 틀린 문제 추적
        self.wrong_questions = []
        self.correct_questions = []
        self.question_history = []
        # 현재 퀴즈 유형 추적
        self.current_quiz_type = None

    def get_random_characters(self, n: int = 4, max_rarity: int = 5, use_all_characters: bool = False) -> List[Dict]:
        """랜덤 캐릭터 n명 선택 (희귀도 제한 가능)"""
        filtered_df = self.df.copy()
        
        if use_all_characters:
            # 실루엣 퀴즈는 전체 캐릭터 사용
            pass
        elif max_rarity <= 4:
            # 3-4성 최대 캐릭터만 필터링
            filtered_df = filtered_df[filtered_df['희귀도'].str.contains(r'[1-4]★', na=False)]
        elif max_rarity <= 3:
            # 3성 이하 캐릭터만 필터링 (레거시 지원)
            filtered_df = filtered_df[filtered_df['희귀도'].str.contains(r'[1-3]★', na=False)]
        
        # 필터링된 결과가 없으면 전체 데이터에서 선택
        if len(filtered_df) == 0:
            print(f"⚠️ 해당 희귀도 캐릭터가 없어서 전체 캐릭터에서 선택합니다. (max_rarity: {max_rarity})")
            filtered_df = self.df.copy()
        
        if len(filtered_df) < n:
            return filtered_df.to_dict('records')
        return filtered_df.sample(n=n).to_dict('records') 

    def generate_quiz_question(self, quiz_type: str) -> Dict[str, Any]:
        """퀴즈 문제 생성 (새 구조)"""
        
        # 퀴즈 유형별 캐릭터 필터링
        if quiz_type == "silhouette_quiz":
            # 실루엣 퀴즈는 전체 캐릭터 대상
            characters = self.get_random_characters(4, use_all_characters=True)
        elif quiz_type in ["guess_name", "guess_element", "guess_weapon"]:
            # 이름/속성/무기 맞추기는 3-4성 최대
            characters = self.get_random_characters(4, max_rarity=4)
        else:
            # 새로운 퀴즈 모드들은 전체 캐릭터 사용
            characters = self.get_random_characters(4, use_all_characters=True)
        
        # 캐릭터가 없으면 에러 처리
        if not characters:
            return {
                'question': "데이터가 부족합니다. 스크래퍼를 실행해주세요.",
                'options': ['데이터 없음'],
                'correct_answer': '데이터 없음',
                'hint_image': '',
                'character_info': {},
                'quiz_type': quiz_type
            }
        
        correct_char = random.choice(characters)
        
        if quiz_type == "guess_name":
            question = "이 캐릭터의 이름은 무엇일까요? (3-4성 최대)"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
            
        elif quiz_type == "guess_rarity":
            question = "이 캐릭터의 희귀도는 무엇일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('희귀도', '') for char in characters]
            correct_answer = correct_char.get('희귀도', '')
            
        elif quiz_type == "guess_element":
            question = "이 캐릭터의 속성은 무엇일까요? (3-4성 최대)"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('속성명리스트', '') for char in characters]
            correct_answer = correct_char.get('속성명리스트', '')
            
        elif quiz_type == "guess_weapon":
            question = "이 캐릭터가 사용하는 무기는 무엇일까요? (3-4성 최대)"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('무기명리스트', '') for char in characters]
            correct_answer = correct_char.get('무기명리스트', '')
            
        elif quiz_type == "guess_personality":
            question = "이 캐릭터의 퍼스널리티는 무엇일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('퍼스널리티리스트', '') for char in characters]
            correct_answer = correct_char.get('퍼스널리티리스트', '')
            
        elif quiz_type == "guess_release_date":
            question = "이 캐릭터의 출시일은 언제일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('출시일', '') for char in characters]
            correct_answer = correct_char.get('출시일', '')
            
        elif quiz_type == "silhouette_quiz":
            question = "이 실루엣의 캐릭터는 누구일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
            
        else:
            # 기본 이름 맞추기
            question = "이 캐릭터의 이름은 무엇일까요?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'hint_image': hint_image,
            'character_info': correct_char,
            'quiz_type': quiz_type
        }

    def process_answer(self, selected_answer: str, correct_answer: str, quiz_type: str):
        """답안 처리 및 점수 계산"""
        is_correct = normalize_text(selected_answer) == normalize_text(correct_answer)
        
        # 시간 계산
        if self.question_start_time:
            time_taken = time.time() - self.question_start_time
        else:
            time_taken = 0
        
        # 점수 계산 (시간 보너스 포함)
        base_score = 10
        time_bonus = max(0, (self.time_limit - time_taken) / self.time_limit * 5)
        total_score = base_score + time_bonus
        
        if is_correct:
            # 정답인 경우
            self.score += total_score
            self.combo_count += 1
            self.max_combo = max(self.max_combo, self.combo_count)
            self.session_stats['correct_answers'] += 1
            
            # 카테고리별 통계 업데이트
            if quiz_type not in self.session_stats['category_stats']:
                self.session_stats['category_stats'][quiz_type] = {'correct': 0, 'total': 0}
            self.session_stats['category_stats'][quiz_type]['correct'] += 1
            self.session_stats['category_stats'][quiz_type]['total'] += 1
            
            # 정답 문제 기록
            self.correct_questions.append({
                'question': self.current_question_data['question'],
                'correct_answer': correct_answer,
                'user_answer': selected_answer,
                'quiz_type': quiz_type,
                'time_taken': time_taken,
                'score': total_score
            })
            
        else:
            # 오답인 경우
            self.combo_count = 0
            self.session_stats['wrong_answers'] += 1
            
            # 카테고리별 통계 업데이트
            if quiz_type not in self.session_stats['category_stats']:
                self.session_stats['category_stats'][quiz_type] = {'correct': 0, 'total': 0}
            self.session_stats['category_stats'][quiz_type]['total'] += 1
            
            # 틀린 문제 기록
            self.wrong_questions.append({
                'question': self.current_question_data['question'],
                'correct_answer': correct_answer,
                'user_answer': selected_answer,
                'quiz_type': quiz_type,
                'time_taken': time_taken
            })
        
        self.total_questions += 1
        self.session_stats['total_time'] += time_taken
        
        return {
            'is_correct': is_correct,
            'score': total_score,
            'time_taken': time_taken,
            'combo': self.combo_count,
            'show_answer': True
        } 

def main():
    """메인 앱 함수"""
    st.title("🎮 Another Eden 퀴즈쇼")
    
    # 데이터 로드
    df = load_character_data()
    
    # 세션 상태 초기화
    if 'game' not in st.session_state:
        st.session_state.game = QuizGame(df)
    
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = None
    
    if 'quiz_answered' not in st.session_state:
        st.session_state.quiz_answered = False
    
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    
    if 'show_wrong_questions' not in st.session_state:
        st.session_state.show_wrong_questions = False
    
    game = st.session_state.game
    
    # 사이드바 - 퀴즈 설정
    with st.sidebar:
        st.header("🎯 퀴즈 설정")
        
        # 퀴즈 유형 선택
        quiz_types = {
            "🏷️ 이름 맞추기": "guess_name",
            "⭐ 희귀도 맞추기": "guess_rarity", 
            "🔥 속성 맞추기": "guess_element",
            "⚔️ 무기 맞추기": "guess_weapon",
            "🎭 퍼스널리티 맞추기": "guess_personality",
            "📅 출시일 맞추기": "guess_release_date",
            "👤 실루엣 퀴즈": "silhouette_quiz"
        }
        
        selected_quiz_type = st.selectbox(
            "퀴즈 유형 선택",
            list(quiz_types.keys()),
            index=0
        )
        
        quiz_type = quiz_types[selected_quiz_type]
        
        # 타이머 설정
        enable_timer = st.checkbox("⏱️ 타이머 사용", value=True)
        if enable_timer:
            game.time_limit = st.slider("제한 시간 (초)", 10, 60, 30)
        
        # 새 문제 생성 버튼
        if st.button("🔄 새 문제 생성", use_container_width=True):
            st.session_state.current_quiz = game.generate_quiz_question(quiz_type)
            st.session_state.quiz_answered = False
            st.session_state.show_result = False
            game.silhouette_revealed = False
            game.retry_count = 0
            game.current_question_data = st.session_state.current_quiz
            game.current_quiz_type = quiz_type
            if enable_timer:
                game.question_start_time = time.time()
            st.rerun()
        
        # 통계 표시
        st.markdown("---")
        st.header("📊 통계")
        
        if game.total_questions > 0:
            accuracy = (game.session_stats['correct_answers'] / game.total_questions) * 100
            st.metric("정확도", f"{accuracy:.1f}%")
            st.metric("총 점수", f"{game.score:.0f}")
            st.metric("최대 콤보", f"{game.max_combo}")
            st.metric("총 문제 수", game.total_questions)
        
        # 틀린 문제 보기 버튼
        if game.wrong_questions:
            if st.button("❌ 틀린 문제 보기", use_container_width=True):
                st.session_state.show_wrong_questions = True
                st.rerun()
    
    # 메인 콘텐츠
    if st.session_state.current_quiz:
        quiz = st.session_state.current_quiz
        
        # 퀴즈 컨테이너
        with st.container():
            st.markdown(f"""
            <div class="quiz-container">
                <h2 class="quiz-question">{quiz['question']}</h2>
            """, unsafe_allow_html=True)
            
            # 이미지 표시
            if quiz['hint_image']:
                if quiz_type == "silhouette_quiz" and not game.silhouette_revealed:
                    # 실루엣 모드
                    st.markdown(f"""
                    <img src="{quiz['hint_image']}" 
                         class="silhouette-image" 
                         style="max-width: 200px; height: auto; margin: 1rem auto; display: block;">
                    """, unsafe_allow_html=True)
                    
                    if st.button("👁️ 실루엣 보기", use_container_width=True):
                        game.silhouette_revealed = True
                        st.rerun()
                else:
                    # 일반 모드
                    st.markdown(f"""
                    <img src="{quiz['hint_image']}" 
                         style="max-width: 200px; height: auto; margin: 1rem auto; display: block;">
                    """, unsafe_allow_html=True)
            
            # 타이머 표시
            if enable_timer and game.question_start_time:
                elapsed = time.time() - game.question_start_time
                remaining = max(0, game.time_limit - elapsed)
                
                if remaining <= 0:
                    st.error("⏰ 시간 초과!")
                    st.session_state.quiz_answered = True
                    st.session_state.show_result = True
                    result = game.process_answer("", quiz['correct_answer'], quiz_type)
                    st.rerun()
                else:
                    st.markdown(f"""
                    <div class="timer-display">
                        ⏱️ 남은 시간: {remaining:.1f}초
                    </div>
                    """, unsafe_allow_html=True)
            
            # 답안 선택
            if not st.session_state.quiz_answered:
                st.markdown('<div class="quiz-options">', unsafe_allow_html=True)
                
                # 답안 섞기
                options = quiz['options'].copy()
                random.shuffle(options)
                
                cols = st.columns(2)
                for i, option in enumerate(options):
                    col = cols[i % 2]
                    if col.button(option, key=f"option_{i}", use_container_width=True):
                        st.session_state.quiz_answered = True
                        st.session_state.show_result = True
                        result = game.process_answer(option, quiz['correct_answer'], quiz_type)
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 결과 표시
            if st.session_state.show_result:
                if 'result' in locals():
                    if result['is_correct']:
                        st.success(f"✅ 정답입니다! +{result['score']:.1f}점")
                        if result['combo'] > 1:
                            st.info(f"🔥 콤보: {result['combo']}연속 정답!")
                    else:
                        st.error(f"❌ 틀렸습니다. 정답: {quiz['correct_answer']}")
                    
                    st.info(f"⏱️ 소요 시간: {result['time_taken']:.1f}초")
                
                # 다음 문제 버튼들
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 다음 문제", key="next_btn", use_container_width=True):
                        game.retry_count = 0
                        game.silhouette_revealed = False
                        st.session_state.current_quiz = game.generate_quiz_question(quiz_type)
                        st.session_state.quiz_answered = False
                        st.session_state.show_result = False
                        game.current_question_data = st.session_state.current_quiz
                        game.current_quiz_type = quiz_type
                        if enable_timer:
                            game.question_start_time = time.time()
                        st.rerun()
                
                with col2:
                    if st.button("🎯 자동 다음 문제", key="auto_next_btn", use_container_width=True):
                        game.retry_count = 0
                        game.silhouette_revealed = False
                        st.session_state.current_quiz = game.generate_quiz_question(quiz_type)
                        st.session_state.quiz_answered = False
                        st.session_state.show_result = False
                        game.current_question_data = st.session_state.current_quiz
                        game.current_quiz_type = quiz_type
                        if enable_timer:
                            game.question_start_time = time.time()
                        st.rerun()
            
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
                    <li><strong>퍼스널리티:</strong> {char_info.get('퍼스널리티리스트', 'N/A')}</li>
                    <li><strong>출시일:</strong> {char_info.get('출시일', 'N/A')}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 틀린 문제 표시
    if st.session_state.get('show_wrong_questions', False) and game.wrong_questions:
        st.markdown("## ❌ 틀린 문제 목록")
        st.info(f"총 {len(game.wrong_questions)}개의 문제를 틀렸습니다.")
        
        for i, wrong_q in enumerate(game.wrong_questions, 1):
            with st.expander(f"문제 {i}: {wrong_q['question']}", expanded=False):
                st.markdown(f"""
                **문제:** {wrong_q['question']}  
                **정답:** {wrong_q['correct_answer']}  
                **내 답:** {wrong_q['user_answer']}  
                **퀴즈 유형:** {wrong_q['quiz_type']}  
                **소요 시간:** {wrong_q['time_taken']:.1f}초
                """)
        
        if st.button("🔙 퀴즈로 돌아가기", use_container_width=True):
            st.session_state.show_wrong_questions = False
            st.rerun()
    
    elif not st.session_state.current_quiz:
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
            "🎭 퍼스널리티 맞추기": "캐릭터의 특성이나 성격을 맞추는 퀴즈",
            "📅 출시일 맞추기": "캐릭터의 출시 연도를 맞추는 새로운 퀴즈 (NEW!)",
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