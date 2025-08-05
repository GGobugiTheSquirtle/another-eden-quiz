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
import json
from datetime import datetime

# 프로젝트 루트 절대경로
BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

st.set_page_config(
    page_title="🎮 Another Eden 퀴즈쇼", 
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
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
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
    
    .quiz-question {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        line-height: 1.6;
        padding: 0 1rem;
    }
    
    .quiz-options {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 2rem;
        margin: 3rem 0;
        padding: 0 1rem;
    }
    
    .quiz-option {
        background: rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 3px solid transparent;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        font-size: 1.1rem;
        font-weight: 500;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .quiz-option::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .quiz-option:hover::before {
        left: 100%;
    }
    
    .quiz-option:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: #FFD700;
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(255, 215, 0, 0.4);
    }
    
    .correct-answer {
        background: rgba(76, 175, 80, 0.9) !important;
        border-color: #4CAF50 !important;
        animation: pulse 0.6s ease-in-out;
    }
    
    .wrong-answer {
        background: rgba(244, 67, 54, 0.9) !important;
        border-color: #F44336 !important;
        animation: shake 0.6s ease-in-out;
    }
    
    .quiz-image {
        max-width: 200px;
        max-height: 200px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        margin: 1rem auto;
        display: block;
    }
    
    .timer-container {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .timer-bar {
        height: 8px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .timer-progress {
        height: 100%;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        transition: width 1s linear;
        border-radius: 4px;
    }
    
    .stats-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .hint-button {
        background: rgba(255, 193, 7, 0.8);
        color: #000;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    
    .hint-button:hover {
        background: rgba(255, 193, 7, 1);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.4);
    }
    
    .game-mode-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
        font-size: 1rem;
    }
    
    .game-mode-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .game-mode-button.active {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
    }
</style>
""", unsafe_allow_html=True)

def safe_icon_to_data_uri(path: str) -> str:
    """아이콘 경로를 data URI로 안전하게 변환"""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"
    
    if pd.isna(path) or not path:
        return placeholder
    
    def normalize_path(p: str) -> str:
        p = unicodedata.normalize("NFKC", str(p))
        return p.replace("\\", "/").strip().lstrip("\ufeff").replace("\u00A0", "")
    
    path = normalize_path(path)
    if not path:
        return placeholder
    if path.startswith(("http://", "https://", "data:image")):
        return path
    
    # 상대 경로를 절대 경로로 변환
    if not os.path.isabs(path):
        # 실제 프로젝트 구조에 맞춘 검색 경로들
        search_dirs = [
            IMAGE_DIR,  # 메인 이미지 디렉토리
            DATA_DIR / "images" / "character_art",  # 정확한 이미지 경로
            BASE_DIR / "04_data" / "images" / "character_art",  # 프로젝트 루트 기준
            Path.cwd() / "04_data" / "images" / "character_art"  # 현재 작업 디렉토리 기준
        ]
        
        file_name = os.path.basename(path)
        for search_dir in search_dirs:
            if search_dir.exists():
                potential_path = search_dir / file_name
                if potential_path.exists():
                    path = str(potential_path)
                    break
                # 대소문자 구분 없이 검색
                try:
                    for f in os.listdir(search_dir):
                        if f.lower() == file_name.lower():
                            path = str(search_dir / f)
                            break
                except Exception:
                    continue
    
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
    csv_path = CSV_DIR / "eden_quiz_data_fixed.csv"  # 정확한 경로 사용
    if not csv_path.exists():
        st.error(f"eden_quiz_data_fixed.csv 파일이 없습니다. 먼저 데이터 생성 스크립트를 실행해주세요.\n경로: {csv_path}")
        st.info("📡 메인 런쳐에서 '데이터 스크래퍼 실행'을 클릭하여 데이터를 생성하세요.")
        st.stop()
    
    df = pd.read_csv(csv_path, encoding='utf-8-sig').fillna('')
    return df

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
            rarities = []
            for char in self.df.to_dict('records'):
                rarity = char.get('희귀도', '')
                if rarity and rarity not in rarities:
                    rarities.append(rarity)
            
            # 옵션 리스트가 비어있지 않은지 확인
            if not rarities:
                rarities = ['5★', '4★', '3★', '2★']
            
            # 최소 2개 이상의 옵션이 있는지 확인
            if len(rarities) < 2:
                rarities.extend(['5★', '4★', '3★', '2★'])
                rarities = list(set(rarities))  # 중복 제거
            
            # 안전한 옵션 생성
            if len(rarities) >= 4:
                options = random.sample(rarities, 4)
            else:
                options = rarities.copy()
                # 부족한 옵션은 기본값으로 채움
                while len(options) < 4:
                    options.append(random.choice(['5★', '4★', '3★', '2★']))
            
            if correct_char.get('희귀도', '') not in options and options:
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
            unique_elements = []
            for elem in all_elements:
                if elem not in unique_elements:
                    unique_elements.append(elem)
            
            # 옵션 리스트가 비어있지 않은지 확인
            if not unique_elements:
                unique_elements = ['Fire', 'Water', 'Earth', 'Wind', 'Thunder', 'Crystal', 'Shade']
            
            # 최소 2개 이상의 옵션이 있는지 확인
            if len(unique_elements) < 2:
                unique_elements.extend(['Fire', 'Water', 'Earth', 'Wind', 'Thunder', 'Crystal', 'Shade'])
                unique_elements = list(set(unique_elements))  # 중복 제거
            
            # 안전한 옵션 생성
            if len(unique_elements) >= 4:
                options = random.sample(unique_elements, 4)
            else:
                options = unique_elements.copy()
                # 부족한 옵션은 기본값으로 채움
                while len(options) < 4:
                    options.append(random.choice(['Fire', 'Water', 'Earth', 'Wind', 'Thunder', 'Crystal', 'Shade']))
            
            char_elements = str(correct_char.get('속성명리스트', '')).split(',')
            char_elements = [elem.strip() for elem in char_elements if elem.strip()]
            if char_elements and char_elements[0] not in options and options:
                options[0] = char_elements[0]
            correct_answer = char_elements[0] if char_elements else ''
            
        elif quiz_type == "guess_rarity":
            question = f"{correct_char.get('캐릭터명', '')}의 희귀도는?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            # 희귀도 리스트에서 선택 (SA 포함)
            all_rarities = []
            for char in self.df.to_dict('records'):
                rarity = str(char.get('희귀도', ''))
                if rarity and rarity != 'nan':
                    all_rarities.append(rarity)
            unique_rarities = []
            for rarity in all_rarities:
                if rarity not in unique_rarities:
                    unique_rarities.append(rarity)
            
            # 옵션 리스트가 비어있지 않은지 확인
            if not unique_rarities:
                unique_rarities = ['5★', '4★', '3★', '5★ 성도각성']
            
            # 최소 2개 이상의 옵션이 있는지 확인
            if len(unique_rarities) < 2:
                unique_rarities.extend(['5★', '4★', '3★', '5★ 성도각성'])
                unique_rarities = list(set(unique_rarities))  # 중복 제거
            
            # 안전한 옵션 생성
            if len(unique_rarities) >= 4:
                options = random.sample(unique_rarities, 4)
            else:
                options = unique_rarities.copy()
                # 부족한 옵션은 기본값으로 채움
                while len(options) < 4:
                    options.append(random.choice(['5★', '4★', '3★', '5★ 성도각성']))
            
            char_rarity = str(correct_char.get('희귀도', ''))
            if char_rarity and char_rarity != 'nan' and char_rarity not in options and options:
                options[0] = char_rarity
            correct_answer = char_rarity if char_rarity and char_rarity != 'nan' else ''
            
        elif quiz_type == "guess_weapon":
            question = f"{correct_char.get('캐릭터명', '')}의 무기는?"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            # 무기 리스트에서 선택
            all_weapons = []
            for char in self.df.to_dict('records'):
                weapons = str(char.get('무기명리스트', '')).split(',')
                all_weapons.extend([weapon.strip() for weapon in weapons if weapon.strip()])
            unique_weapons = []
            for weapon in all_weapons:
                if weapon not in unique_weapons:
                    unique_weapons.append(weapon)
            
            # 옵션 리스트가 비어있지 않은지 확인
            if not unique_weapons:
                unique_weapons = ['Sword', 'Katana', 'Axe', 'Hammer', 'Lance', 'Bow', 'Staff', 'Fists']
            
            # 최소 2개 이상의 옵션이 있는지 확인
            if len(unique_weapons) < 2:
                unique_weapons.extend(['Sword', 'Katana', 'Axe', 'Hammer', 'Lance', 'Bow', 'Staff', 'Fists'])
                unique_weapons = list(set(unique_weapons))  # 중복 제거
            
            # 안전한 옵션 생성
            if len(unique_weapons) >= 4:
                options = random.sample(unique_weapons, 4)
            else:
                options = unique_weapons.copy()
                # 부족한 옵션은 기본값으로 채움
                while len(options) < 4:
                    options.append(random.choice(['Sword', 'Katana', 'Axe', 'Hammer', 'Lance', 'Bow', 'Staff', 'Fists']))
            
            char_weapons = str(correct_char.get('무기명리스트', '')).split(',')
            char_weapons = [weapon.strip() for weapon in char_weapons if weapon.strip()]
            if char_weapons and char_weapons[0] not in options and options:
                options[0] = char_weapons[0]
            correct_answer = char_weapons[0] if char_weapons else ''
        
        else:  # silhouette_quiz
            question = "실루엣을 보고 캐릭터를 맞춰보세요!"
            hint_image = safe_icon_to_data_uri(correct_char.get('캐릭터아이콘경로', ''))
            options = [char.get('캐릭터명', '') for char in characters]
            correct_answer = correct_char.get('캐릭터명', '')
        
        random.shuffle(options)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'hint_image': hint_image,
            'character_info': correct_char,
            'quiz_type': quiz_type
        }
    
    def start_timer(self):
        """타이머 시작"""
        self.question_start_time = time.time()
        if self.start_time is None:
            self.start_time = time.time()
    
    def get_remaining_time(self):
        """남은 시간 반환"""
        if self.question_start_time is None:
            return self.time_limit
        elapsed = time.time() - self.question_start_time
        return max(0, self.time_limit - elapsed)
    
    def is_time_up(self):
        """시간 초과 여부 확인"""
        return self.get_remaining_time() <= 0
    
    def use_hint_fifty_fifty(self, options, correct_answer):
        """50:50 힌트 사용"""
        if self.hints_used >= 2:  # 최대 2개 힌트만 사용 가능
            return options
        
        self.hints_used += 1
        wrong_options = [opt for opt in options if opt != correct_answer]
        # 틀린 선택지 중 2개만 남기고 제거
        if len(wrong_options) > 2:
            keep_wrong = random.sample(wrong_options, 2)
            return [correct_answer] + keep_wrong
        return options
    
    def add_time_bonus(self):
        """시간 보너스 힌트 사용"""
        if self.hints_used >= 2:
            return False
        
        self.hints_used += 1
        self.time_limit += 15  # 15초 추가
        return True
    
    def update_stats(self, is_correct, quiz_type, time_taken):
        """통계 업데이트"""
        if is_correct:
            self.session_stats['correct_answers'] += 1
            self.combo_count += 1
            self.max_combo = max(self.max_combo, self.combo_count)
        else:
            self.session_stats['wrong_answers'] += 1
            self.combo_count = 0
        
        self.session_stats['total_time'] += time_taken
        
        # 카테고리별 통계
        if quiz_type not in self.session_stats['category_stats']:
            self.session_stats['category_stats'][quiz_type] = {'correct': 0, 'total': 0}
        
        self.session_stats['category_stats'][quiz_type]['total'] += 1
        if is_correct:
            self.session_stats['category_stats'][quiz_type]['correct'] += 1
    
    def get_combo_bonus(self):
        """콤보 보너스 점수 계산"""
        if self.combo_count >= 5:
            return 50
        elif self.combo_count >= 3:
            return 20
        elif self.combo_count >= 2:
            return 10
        return 0
    
    def save_session_stats(self):
        """세션 통계 저장"""
        stats_file = DATA_DIR / "quiz_stats.json"
        stats_file.parent.mkdir(exist_ok=True)
        
        try:
            # 기존 통계 로드
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {'sessions': [], 'total_stats': {}}
            
            # 현재 세션 추가
            session_data = {
                'date': datetime.now().isoformat(),
                'score': self.score,
                'total_questions': self.total_questions,
                'max_combo': self.max_combo,
                'hints_used': self.hints_used,
                **self.session_stats
            }
            
            all_stats['sessions'].append(session_data)
            
            # 전체 통계 업데이트
            if 'total_stats' not in all_stats:
                all_stats['total_stats'] = {}
            
            total = all_stats['total_stats']
            total['total_games'] = total.get('total_games', 0) + 1
            total['total_correct'] = total.get('total_correct', 0) + self.session_stats['correct_answers']
            total['total_questions'] = total.get('total_questions', 0) + self.total_questions
            total['best_combo'] = max(total.get('best_combo', 0), self.max_combo)
            
            # 파일 저장
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            st.error(f"통계 저장 실패: {e}")

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
    
    # 게임 설정
    st.sidebar.subheader("⚙️ 게임 설정")
    enable_timer = st.sidebar.checkbox("⏰ 타이머 사용", value=False)
    if enable_timer:
        time_limit = st.sidebar.slider("시간 제한 (초)", 10, 60, 30)
        game.time_limit = time_limit
    
    # 점수 및 통계 표시
    game = st.session_state.quiz_game
    if game.total_questions > 0:
        accuracy = (game.score / game.total_questions) * 100
        combo_bonus = game.get_combo_bonus()
        
        st.sidebar.markdown(f"""
        <div class="score-display">
            📊 현재 점수: {game.score} / {game.total_questions}<br>
            정답률: {accuracy:.1f}%<br>
            🔥 연속 정답: {game.combo_count}개<br>
            💎 최대 콤보: {game.max_combo}개<br>
            💡 힌트 사용: {game.hints_used}/2개
        </div>
        """, unsafe_allow_html=True)
        
        # 진행률 표시
        if game.total_questions > 0:
            progress = game.total_questions / 20  # 20문제 기준
            st.sidebar.progress(min(progress, 1.0))
            st.sidebar.caption(f"진행률: {min(game.total_questions, 20)}/20 문제")
    
    # 새 문제 생성 버튼
    if st.sidebar.button("🎯 새 문제 생성", use_container_width=True):
        st.session_state.current_quiz = game.generate_quiz_question(quiz_type)
        st.session_state.quiz_answered = False
        st.session_state.show_result = False
        st.session_state.answer_correct = False
        st.session_state.selected_answer = None
        if enable_timer:
            game.start_timer()
        st.rerun()
    
    # 게임 종료 및 통계 저장 버튼
    if st.sidebar.button("📊 게임 종료 & 통계 저장", use_container_width=True):
        if game.total_questions > 0:
            game.save_session_stats()
            st.sidebar.success("통계가 저장되었습니다!")
        st.session_state.quiz_game = QuizGame(df)
        st.session_state.current_quiz = None
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
        
        # 타이머 표시
        if enable_timer and not st.session_state.quiz_answered:
            remaining_time = game.get_remaining_time()
            if remaining_time > 0:
                timer_color = "#FF6B6B" if remaining_time <= 10 else "#4ECDC4"
                timer_class = "timer-warning" if remaining_time <= 10 else "timer-display"
                progress_width = (remaining_time / game.time_limit) * 100
                
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <div class="{timer_class}" style="background: {timer_color}; color: white; padding: 0.8rem 1.5rem; 
                                border-radius: 25px; display: inline-block; font-weight: bold;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.2); position: relative; overflow: hidden;">
                        <div style="position: absolute; top: 0; left: 0; height: 100%; width: {progress_width}%;
                                    background: rgba(255,255,255,0.2); transition: width 0.1s linear;"></div>
                        <span style="position: relative; z-index: 1;">
                            ⏰ 남은 시간: {remaining_time:.1f}초
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⏰ 시간 초과! 다음 문제로 넘어갑니다.")
                st.session_state.quiz_answered = True
                st.session_state.show_result = True
                st.session_state.answer_correct = False
                game.total_questions += 1
                game.update_stats(False, quiz.get('quiz_type', ''), game.time_limit)
                st.rerun()
        
        st.markdown(f"""
        <div class="quiz-container">
            <div class="quiz-question">{quiz['question']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 힌트 버튼들
        if not st.session_state.quiz_answered and game.hints_used < 2:
            hint_col1, hint_col2, hint_col3 = st.columns([1, 1, 2])
            
            with hint_col1:
                if st.button("💡 50:50 힌트", disabled=game.hints_used >= 2):
                    quiz['options'] = game.use_hint_fifty_fifty(quiz['options'], quiz['correct_answer'])
                    st.rerun()
            
            with hint_col2:
                if enable_timer and st.button("⏰ 시간 추가", disabled=game.hints_used >= 2):
                    if game.add_time_bonus():
                        st.success("15초가 추가되었습니다!")
                        st.rerun()
        
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
                        # 시간 계산
                        time_taken = 0
                        if enable_timer and game.question_start_time:
                            time_taken = time.time() - game.question_start_time
                        
                        st.session_state.quiz_answered = True
                        st.session_state.selected_answer = option
                        st.session_state.show_result = True
                        
                        # 점수 및 통계 업데이트
                        game.total_questions += 1
                        is_correct = option == quiz['correct_answer']
                        
                        if is_correct:
                            # 기본 점수 + 콤보 보너스 + 시간 보너스
                            base_score = 10
                            combo_bonus = game.get_combo_bonus()
                            time_bonus = max(0, int((game.time_limit - time_taken) / 2)) if enable_timer else 0
                            total_points = base_score + combo_bonus + time_bonus
                            game.score += total_points
                            st.session_state.answer_correct = True
                            st.session_state.points_earned = total_points
                        else:
                            st.session_state.answer_correct = False
                            st.session_state.points_earned = 0
                        
                        # 통계 업데이트
                        game.update_stats(is_correct, quiz.get('quiz_type', ''), time_taken)
                        
                        st.rerun()
        
        # 결과 표시
        if st.session_state.show_result:
            if st.session_state.answer_correct:
                points_earned = st.session_state.get('points_earned', 10)
                combo_msg = f" (🔥 {game.combo_count}연속!)" if game.combo_count > 1 else ""
                
                # 성공 메시지를 더 화려하게 표시
                st.markdown(f"""
                <div class="success-message" style="
                    background: linear-gradient(45deg, #4CAF50, #8BC34A);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    margin: 1rem 0;
                    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
                    animation: pulse 0.6s ease-in-out;
                ">
                    <h3 style="margin: 0; font-size: 1.5rem;">🎉 정답입니다!{combo_msg}</h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: bold;">+{points_earned}점 획득!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 콤보 표시
                if game.combo_count > 1:
                    st.markdown(f"""
                    <div class="combo-display">
                        🔥 {game.combo_count}연속 정답! 🔥
                    </div>
                    """, unsafe_allow_html=True)
                
                # 보너스 점수 상세 표시
                if points_earned > 10:
                    bonus_details = []
                    if game.get_combo_bonus() > 0:
                        bonus_details.append(f"🔥 콤보 보너스: +{game.get_combo_bonus()}점")
                    if enable_timer and game.question_start_time:
                        time_taken = time.time() - game.question_start_time
                        time_bonus = max(0, int((game.time_limit - time_taken) / 2))
                        if time_bonus > 0:
                            bonus_details.append(f"⚡ 시간 보너스: +{time_bonus}점")
                    
                    if bonus_details:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(45deg, #FFD700, #FFA500);
                            color: #333;
                            padding: 1rem;
                            border-radius: 15px;
                            text-align: center;
                            margin: 1rem 0;
                            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                        ">
                            <strong>💎 보너스 점수</strong><br>
                            {' | '.join(bonus_details)}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                # 오답 메시지를 더 부드럽게 표시
                st.markdown(f"""
                <div class="error-message" style="
                    background: linear-gradient(45deg, #F44336, #E57373);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    margin: 1rem 0;
                    box-shadow: 0 8px 25px rgba(244, 67, 54, 0.4);
                ">
                    <h3 style="margin: 0; font-size: 1.3rem;">❌ 아쉽네요!</h3>
                    <p style="margin: 0.5rem 0 0 0;">정답은 <strong>'{quiz['correct_answer']}'</strong>입니다.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 콤보 끊김 알림
                if game.combo_count > 0:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(45deg, #FF9800, #FFC107);
                        color: #333;
                        padding: 1rem;
                        border-radius: 15px;
                        text-align: center;
                        margin: 1rem 0;
                        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
                    ">
                        💔 {game.combo_count}연속 기록이 끊어졌습니다.
                    </div>
                    """, unsafe_allow_html=True)
            
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