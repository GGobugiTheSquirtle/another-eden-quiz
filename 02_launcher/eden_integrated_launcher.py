"""
🎮 Another Eden 사용자용 런처
사용자들을 위한 배포용 통합 런처
"""

import streamlit as st
import os
import pandas as pd
import random
import time
import re
import base64
import html
from pathlib import Path
import unicodedata
import streamlit.components.v1 as components
from typing import List, Dict, Any

# 전역 설정
BASE_DIR = Path(__file__).parent.resolve()

# 이미지 캐시
_image_cache = {}

# 페이지 설정
st.set_page_config(
    page_title="🎮 Another Eden 게임 센터",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================================
# 유틸리티 함수들
# ===============================================

def safe_icon_to_data_uri(path: str) -> str:
    """아이콘 경로를 data URI로 안전하게 변환 (캐싱 포함)"""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"
    
    def normalize_path(p: str) -> str:
        if p is None or pd.isna(p):
            return ""
        p = str(p)
        p = unicodedata.normalize("NFKC", p)
        return p.replace("\\", "/").strip().lstrip("\ufeff").replace("\u00A0", "")

    path = normalize_path(path)
    if not path or path == "" or path == "nan":
        return placeholder
    if path.startswith(("http://", "https://", "data:image")):
        return path
    
    # 캐시 확인
    if path in _image_cache:
        return _image_cache[path]
    
    abs_path = BASE_DIR / path
    try:
        if abs_path.exists() and abs_path.is_file():
            with open(abs_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                ext = abs_path.suffix.lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    mime_type = f"image/{ext[1:]}" if ext != '.jpg' else "image/jpeg"
                    result = f"data:{mime_type};base64,{data}"
                    # 캐시에 저장
                    _image_cache[path] = result
                    return result
    except:
        pass
    return placeholder

def get_character_image(char_name: str, char_index: int = None) -> str:
    """캐릭터 이름으로 이미지 경로 찾기 (개선된 버전)"""
    icons_dir = BASE_DIR / "character_art" / "icons"
    if not icons_dir.exists():
        return ""
    
    image_files = list(icons_dir.glob("*.png"))
    if not image_files:
        return ""
    
    # 1. 정확한 이름 매칭 (가장 우선)
    search_name = char_name.replace(" ", "").lower()
    for file in image_files:
        file_name = file.stem.lower()
        if search_name == file_name:
            return str(file)
    
    # 2. 부분 매칭 (포함 관계)
    for file in image_files:
        file_name = file.stem.lower()
        if search_name in file_name or file_name in search_name:
            return str(file)
    
    # 3. 단어별 매칭 (2글자 이상)
    char_words = [word for word in search_name.split() if len(word) >= 2]
    for file in image_files:
        file_name = file.stem.lower()
        for word in char_words:
            if word in file_name:
                return str(file)
    
    # 4. 특수 케이스 매칭 (ES, AS, NS 등)
    if "ES" in char_name or "AS" in char_name or "NS" in char_name:
        base_name = char_name.replace(" ES", "").replace(" AS", "").replace(" NS", "").replace(" ", "").lower()
        for file in image_files:
            file_name = file.stem.lower()
            if base_name in file_name:
                return str(file)
    
    # 5. char_index 기반 할당 (fallback)
    if char_index is not None:
        image_index = char_index % len(image_files)
        return str(image_files[image_index])
    
    # 6. 해시 기반 할당 (최종 fallback)
    import hashlib
    char_hash = hashlib.md5(char_name.encode()).hexdigest()
    hash_int = int(char_hash[:8], 16)
    image_index = hash_int % len(image_files)
    return str(image_files[image_index])

def load_quiz_data():
    """퀴즈용 데이터 로드"""
    csv_file = "eden_roulette_data_with_personalities.csv"
    if not os.path.exists(csv_file):
        csv_file = "eden_roulette_data.csv"
    
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        df['이미지경로'] = df.apply(lambda row: get_character_image(row['캐릭터명'], row.name), axis=1)
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None

def load_roulette_data():
    """룰렛용 데이터 로드"""
    csv_file = "eden_roulette_data_with_personalities.csv"
    if not os.path.exists(csv_file):
        st.error("룰렛 데이터 파일이 없습니다.")
        return None, None
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        df['이미지경로'] = df.apply(lambda row: get_character_image(row['캐릭터명'], row.name), axis=1)
        
        column_map = {
            '이름': '캐릭터명',
            '캐릭터아이콘경로': '이미지경로', 
            '희귀도': '희귀도',
            '속성명': '속성명리스트',
            '속성아이콘': '속성_아이콘경로리스트',
            '무기명': '무기명리스트', 
            '무기아이콘': '무기_아이콘경로리스트',
            '방어구명': '',
            '방어구아이콘': ''
        }
        
        for k_kor, v_eng in column_map.items():
            if v_eng and v_eng not in df.columns:
                st.error(f"필요한 컬럼 '{v_eng}'이 없습니다.")
                return None, None
                
        return df, column_map
    except Exception as e:
        st.error(f"룰렛 데이터 로드 오류: {e}")
        return None, None

# ===============================================
# 퀴즈쇼 함수들
# ===============================================

def create_silhouette_html_fullscreen(image_path: str, char_name: str = "") -> str:
    """캐릭터 실루엣 HTML 생성"""
    icon_data = safe_icon_to_data_uri(image_path)
    return f'''
    <div style="text-align: center; margin: 2rem 0;">
        <div style="width: 300px; height: 300px; margin: 0 auto; position: relative; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 12px 48px rgba(0,0,0,0.4);">
            <img src="{icon_data}" 
                 style="width: 100%; height: 100%; object-fit: contain; filter: brightness(0) contrast(1.5) opacity(0.9);" 
                 alt="{char_name} 실루엣">
        </div>
        <p style="margin-top: 1.5rem; font-style: italic; color: #666; font-size: 1.2rem; font-weight: 500;">실루엣을 보고 캐릭터를 맞춰보세요!</p>
    </div>
    '''

def run_quiz_mode_fullscreen(df: pd.DataFrame, mode: str):
    """퀴즈 모드 실행 (전체 화면 버전)"""
    if df is None or len(df) == 0:
        st.error("퀴즈 데이터가 없습니다.")
        return
    
    if f'quiz_fullscreen_{mode}_data' not in st.session_state:
        st.session_state[f'quiz_fullscreen_{mode}_data'] = {
            'score': 0,
            'total': 0,
            'current_question': None,
            'show_answer': False
        }
    
    quiz_data = st.session_state[f'quiz_fullscreen_{mode}_data']
    
    # 점수 섹션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        accuracy = quiz_data['score']/max(quiz_data['total'], 1)*100 if quiz_data['total'] > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;">
            <h3 style="margin: 0; color: #FFD700;">점수</h3>
            <h2 style="margin: 10px 0; font-size: 2.5rem;">{quiz_data['score']}/{quiz_data['total']}</h2>
            <p style="margin: 0; font-size: 1.5rem;">{accuracy:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🎲 새 문제 시작", key=f"new_fullscreen_{mode}", use_container_width=True, type="primary"):
            char = df.sample(1).iloc[0]
            quiz_data['current_question'] = char
            quiz_data['show_answer'] = False
            
            if mode in ["이름 맞히기", "실루엣 맞히기"]:
                correct_answer = char['캐릭터명']
                wrong_answers = df[df['캐릭터명'] != correct_answer]['캐릭터명'].sample(3).tolist()
                all_options = [correct_answer] + wrong_answers
                random.shuffle(all_options)
                quiz_data['options'] = all_options
            elif mode == "희귀도 맞히기":
                correct_rarity = char.get('희귀도', '')
                all_rarities = df['희귀도'].unique()
                wrong_rarities = [r for r in all_rarities if r != correct_rarity]
                if len(wrong_rarities) >= 3:
                    wrong_rarities = random.sample(wrong_rarities, 3)
                else:
                    wrong_rarities = wrong_rarities + ['3★', '4★', '5★']
                all_options = [correct_rarity] + wrong_rarities[:3]
                random.shuffle(all_options)
                quiz_data['options'] = all_options
            elif mode == "속성 맞히기":
                if char.get('속성명리스트'):
                    correct_attrs = [x.strip() for x in char['속성명리스트'].split('|') if x.strip()]
                    all_attrs = []
                    for attr_list in df['속성명리스트'].dropna():
                        if attr_list:
                            all_attrs.extend([x.strip() for x in attr_list.split('|') if x.strip()])
                    all_attrs = list(set(all_attrs))
                    wrong_attrs = [attr for attr in all_attrs if attr not in correct_attrs]
                    if len(wrong_attrs) >= 3:
                        wrong_attrs = random.sample(wrong_attrs, 3)
                    else:
                        wrong_attrs = ['화', '수', '지', '풍', '빛', '어둠']
                    all_options = correct_attrs + wrong_attrs[:3]
                    random.shuffle(all_options)
                    quiz_data['options'] = all_options[:4]
                    quiz_data['correct_answer'] = correct_attrs[0] if correct_attrs else ""
            elif mode == "무기 맞히기":
                if char.get('무기명리스트'):
                    correct_weapons = [x.strip() for x in char['무기명리스트'].split('|') if x.strip()]
                    all_weapons = []
                    for weapon_list in df['무기명리스트'].dropna():
                        if weapon_list:
                            all_weapons.extend([x.strip() for x in weapon_list.split('|') if x.strip()])
                    all_weapons = list(set(all_weapons))
                    wrong_weapons = [weapon for weapon in all_weapons if weapon not in correct_weapons]
                    if len(wrong_weapons) >= 3:
                        wrong_weapons = random.sample(wrong_weapons, 3)
                    else:
                        wrong_weapons = ['검', '창', '도끼', '활', '지팡이', '단검']
                    all_options = correct_weapons + wrong_weapons[:3]
                    random.shuffle(all_options)
                    quiz_data['options'] = all_options[:4]
                    quiz_data['correct_answer'] = correct_weapons[0] if correct_weapons else ""
            
            st.rerun()
    
    # 문제 섹션
    if quiz_data['current_question'] is not None:
        char = quiz_data['current_question']
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 4rem; border-radius: 20px; margin: 3rem 0; text-align: center; color: white;">
            <h2 style="margin: 0 0 2rem 0; color: #FFD700; font-size: 2.5rem;">문제</h2>
        """, unsafe_allow_html=True)
        
        if mode == "이름 맞히기":
            if char['이미지경로']:
                icon_data = safe_icon_to_data_uri(char['이미지경로'])
                st.markdown(f'<div style="text-align: center; margin: 2rem 0;"><img src="{icon_data}" style="width: 300px; height: 300px; object-fit: contain; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 2rem; font-weight: 600; margin: 2rem 0;">이 캐릭터의 이름은?</p>', unsafe_allow_html=True)
            
        elif mode == "실루엣 맞히기":
            if char['이미지경로']:
                st.markdown(create_silhouette_html_fullscreen(char['이미지경로'], char['캐릭터명']), unsafe_allow_html=True)
            
        elif mode == "희귀도 맞히기":
            st.markdown(f'<p style="font-size: 2rem; font-weight: 600; margin: 2rem 0;"><strong>{char["캐릭터명"]}</strong>의 희귀도는?</p>', unsafe_allow_html=True)
            
        elif mode == "속성 맞히기":
            st.markdown(f'<p style="font-size: 2rem; font-weight: 600; margin: 2rem 0;"><strong>{char["캐릭터명"]}</strong>의 속성은?</p>', unsafe_allow_html=True)
            
        elif mode == "무기 맞히기":
            st.markdown(f'<p style="font-size: 2rem; font-weight: 600; margin: 2rem 0;"><strong>{char["캐릭터명"]}</strong>의 무기는?</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 선택지 섹션
        if not quiz_data['show_answer']:
            if 'options' in quiz_data:
                st.markdown('<h3 style="margin: 2rem 0; color: #333; text-align: center;">정답을 선택하세요:</h3>', unsafe_allow_html=True)
                
                cols = st.columns(2)
                selected = None
                
                for i, option in enumerate(quiz_data['options']):
                    col_idx = i % 2
                    with cols[col_idx]:
                        if st.button(option, key=f"option_fullscreen_{mode}_{i}", use_container_width=True):
                            selected = option
                
                if selected:
                    st.markdown(f'<div style="margin: 2rem 0; padding: 2rem; background: #e3f2fd; border-radius: 15px; border-left: 8px solid #2196F3; text-align: center;"><h4 style="margin: 0; color: #333;">선택한 답: <strong>{selected}</strong></h4></div>', unsafe_allow_html=True)
                    
                    if st.button("✅ 정답 확인", key=f"check_fullscreen_{mode}", use_container_width=True, type="primary"):
                        if mode in ["이름 맞히기", "실루엣 맞히기"]:
                            correct = char['캐릭터명']
                        elif mode == "희귀도 맞히기":
                            correct = char.get('희귀도', '')
                        elif mode == "속성 맞히기":
                            correct = quiz_data.get('correct_answer', '')
                            if not correct:
                                correct = char.get('속성명리스트', '').split('|')[0].strip() if char.get('속성명리스트') else ''
                        elif mode == "무기 맞히기":
                            correct = quiz_data.get('correct_answer', '')
                            if not correct:
                                correct = char.get('무기명리스트', '').split('|')[0].strip() if char.get('무기명리스트') else ''
                        else:
                            correct = ""
                        
                        quiz_data['total'] += 1
                        if selected == correct:
                            quiz_data['score'] += 1
                            st.success("🎉 정답입니다!")
                        else:
                            st.error(f"❌ 오답입니다. 정답: {correct}")
                        
                        quiz_data['show_answer'] = True
                        st.rerun()
        
        else:
            # 정답 후 캐릭터 정보 표시
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center; color: white;">
                <h3 style="margin: 0; color: #FFD700; font-size: 2rem;">🎉 문제 완료!</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if char['이미지경로']:
                    icon_data = safe_icon_to_data_uri(char['이미지경로'])
                    st.markdown(f'<div style="text-align: center;"><img src="{icon_data}" style="width: 250px; height: 250px; object-fit: contain; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0 0 1.5rem 0; color: #333; font-size: 1.5rem;">캐릭터 정보</h4>
                    <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>이름:</strong> {char['캐릭터명']}</p>
                    <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>희귀도:</strong> {char.get('희귀도', '')}</p>
                    <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>속성:</strong> {char.get('속성명리스트', '')}</p>
                    <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>무기:</strong> {char.get('무기명리스트', '')}</p>
                    <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>퍼스널리티:</strong> {char.get('개성(퍼스널리티)', '')}</p>
                </div>
                """, unsafe_allow_html=True)

# ===============================================
# 룰렛 함수들
# ===============================================

def create_character_card_fullscreen(char_data: pd.Series, column_map: dict) -> str:
    """캐릭터 카드 HTML 생성"""
    name = char_data[column_map['이름']]
    rarity = char_data[column_map['희귀도']]
    icon_data = safe_icon_to_data_uri(char_data[column_map['캐릭터아이콘경로']])
    
    return f'''
    <div style="border: 3px solid #ddd; border-radius: 20px; padding: 3rem; margin: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">
        <img src="{icon_data}" style="width: 200px; height: 200px; object-fit: contain; border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        <h3 style="margin: 1rem 0; color: #FFD700; font-size: 2rem;">{name}</h3>
        <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>희귀도:</strong> {rarity}</p>
        <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>속성:</strong> {char_data.get(column_map['속성명'], '')}</p>
        <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>무기:</strong> {char_data.get(column_map['무기명'], '')}</p>
        <p style="margin: 1rem 0; font-size: 1.2rem;"><strong>퍼스널리티:</strong> {char_data.get('개성(퍼스널리티)', '')}</p>
    </div>
    '''

def run_roulette_fullscreen():
    """룰렛 게임 실행 (전체 화면 버전)"""
    df, column_map = load_roulette_data()
    if df is None:
        return
    
    # 필터링 섹션
    st.markdown("""
    <div style="background: white; padding: 3rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 2rem 0; color: #333; font-size: 2rem;">🔍 필터 설정</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        available_rarities = sorted(df[column_map['희귀도']].dropna().unique())
        selected_rarities = st.multiselect("⭐ 희귀도 필터", available_rarities)
    
    with col2:
        available_attrs = []
        for attr_list in df[column_map['속성명']].dropna():
            if attr_list:
                available_attrs.extend([x.strip() for x in str(attr_list).split('|')])
        available_attrs = sorted(set(available_attrs))
        selected_attrs = st.multiselect("🔥 속성 필터", available_attrs)
    
    with col3:
        available_weapons = []
        for weapon_list in df[column_map['무기명']].dropna():
            if weapon_list:
                available_weapons.extend([x.strip() for x in str(weapon_list).split('|')])
        available_weapons = sorted(set(available_weapons))
        selected_weapons = st.multiselect("⚔️ 무기 필터", available_weapons)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 필터링 적용
    filtered_df = df.copy()
    if selected_rarities:
        filtered_df = filtered_df[filtered_df[column_map['희귀도']].isin(selected_rarities)]
    if selected_attrs:
        filtered_df = filtered_df[filtered_df[column_map['속성명']].str.contains('|'.join(selected_attrs), na=False)]
    if selected_weapons:
        filtered_df = filtered_df[filtered_df[column_map['무기명']].str.contains('|'.join(selected_weapons), na=False)]
    
    # 필터 결과 표시
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center; color: white;">
        <h4 style="margin: 0; font-size: 1.5rem;">📊 필터 결과: {len(filtered_df)}명의 캐릭터</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 룰렛 실행 섹션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎲 룰렛 돌리기!", key="roulette_spin_fullscreen", use_container_width=True, type="primary"):
            if len(filtered_df) > 0:
                winner = filtered_df.sample(1).iloc[0]
                st.session_state['roulette_winner_fullscreen'] = winner
                
                with st.spinner("룰렛 돌리는 중..."):
                    time.sleep(1)
                
                st.balloons()
                st.success("🎉 당첨!")
    
    # 당첨 결과 표시
    if 'roulette_winner_fullscreen' in st.session_state:
        winner = st.session_state['roulette_winner_fullscreen']
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 3rem; border-radius: 20px; margin: 3rem 0; text-align: center; color: white;">
            <h3 style="margin: 0; color: #333; font-size: 2.5rem;">🏆 당첨 캐릭터</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(create_character_card_fullscreen(winner, column_map), unsafe_allow_html=True)

# ===============================================
# 페이지 함수들
# ===============================================

def show_home_page():
    """홈 페이지 (개선된 레이아웃)"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 2.5rem; color: #FFD700;">🎮 Another Eden 게임 센터</h1>
        <p style="margin: 1rem 0; font-size: 1.2rem; opacity: 0.9;">캐릭터 퀴즈와 룰렛을 즐겨보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 반응형 3컬럼 레이아웃
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎯 퀴즈쇼 시작", key="quiz_start_button", use_container_width=True, type="primary"):
            st.session_state['selected_game'] = "🎯 퀴즈쇼"
            st.rerun()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; margin: 1rem 0; text-align: center; color: white;">
            <h3 style="margin: 0; color: #FFD700; font-size: 1.8rem;">🎯 퀴즈쇼</h3>
            <p style="margin: 0.5rem 0; font-size: 1rem;">퀴즈를 풀고 캐릭터 지식을 테스트하세요!</p>
            <ul style="text-align: left; margin: 0.5rem 0; font-size: 0.9rem;">
                <li>🏷️ 이름 맞히기</li>
                <li>👤 실루엣 맞히기</li>
                <li>⭐ 희귀도 맞히기</li>
                <li>🔥 속성 맞히기</li>
                <li>⚔️ 무기 맞히기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🎰 캐릭터 룰렛 시작", key="roulette_start_button", use_container_width=True, type="primary"):
            st.session_state['selected_game'] = "🎰 캐릭터 룰렛"
            st.rerun()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 2rem; border-radius: 15px; margin: 1rem 0; text-align: center; color: white;">
            <h3 style="margin: 0; color: #FFD700; font-size: 1.8rem;">🎰 캐릭터 룰렛</h3>
            <p style="margin: 0.5rem 0; font-size: 1rem;">필터를 설정하고 랜덤 캐릭터를 뽑아보세요!</p>
            <ul style="text-align: left; margin: 0.5rem 0; font-size: 0.9rem;">
                <li>🔍 캐릭터 필터링</li>
                <li>🎲 랜덤 뽑기</li>
                <li>🏆 결과 표시</li>
                <li>📊 상세 정보</li>
                <li>🎨 시각적 효과</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin: 1rem 0; text-align: center; color: white;">
            <h3 style="margin: 0; color: #FFD700; font-size: 1.8rem;">📖 사용 가이드</h3>
            <p style="margin: 0.5rem 0; font-size: 1rem;">게임을 즐기는 방법을 알아보세요!</p>
            <ul style="text-align: left; margin: 0.5rem 0; font-size: 0.9rem;">
                <li>🎯 퀴즈 모드 선택</li>
                <li>🎰 룰렛 필터 설정</li>
                <li>🏆 결과 확인</li>
                <li>📊 점수 확인</li>
                <li>🔄 다시 시작</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_quiz_page():
    """퀴즈쇼 페이지"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; text-align: center; color: white;">
        <h1 style="margin: 0; color: #FFD700; font-size: 3rem;">🎯 Another Eden 퀴즈쇼</h1>
        <p style="margin: 1rem 0; font-size: 1.5rem; opacity: 0.9;">퀴즈를 풀고 캐릭터 지식을 테스트하세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 퀴즈 모드 선택
    quiz_modes = ["이름 맞히기", "실루엣 맞히기", "희귀도 맞히기", "속성 맞히기", "무기 맞히기"]
    selected_mode = st.selectbox("퀴즈 모드 선택", quiz_modes, key="quiz_mode_select_fullscreen")
    
    # 퀴즈 데이터 로드 및 실행
    quiz_df = load_quiz_data()
    if quiz_df is not None:
        run_quiz_mode_fullscreen(quiz_df, selected_mode)
    else:
        st.error("퀴즈 데이터를 불러올 수 없습니다. CSV 파일을 확인하세요.")

def show_roulette_page():
    """룰렛 페이지"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; text-align: center; color: white;">
        <h1 style="margin: 0; color: #FFD700; font-size: 3rem;">🎰 캐릭터 룰렛</h1>
        <p style="margin: 1rem 0; font-size: 1.5rem; opacity: 0.9;">필터를 설정하고 랜덤 캐릭터를 뽑아보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    run_roulette_fullscreen()

def show_guide_page():
    """가이드 페이지"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; margin: 2rem 0; text-align: center; color: white;">
        <h1 style="margin: 0; color: #FFD700; font-size: 3rem;">📖 사용 가이드</h1>
        <p style="margin: 1rem 0; font-size: 1.5rem; opacity: 0.9;">게임을 즐기는 방법을 알아보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 1rem 0; color: #333;">🎯 퀴즈쇼 가이드</h3>
            <ul style="text-align: left;">
                <li>5가지 퀴즈 모드 선택</li>
                <li>캐릭터 이미지나 실루엣 확인</li>
                <li>정답을 선택하고 확인</li>
                <li>점수와 정답률 확인</li>
                <li>캐릭터 상세 정보 확인</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 1rem 0; color: #333;">🎰 룰렛 가이드</h3>
            <ul style="text-align: left;">
                <li>희귀도, 속성, 무기 필터 설정</li>
                <li>룰렛 돌리기 버튼 클릭</li>
                <li>당첨 캐릭터 확인</li>
                <li>캐릭터 상세 정보 확인</li>
                <li>다시 룰렛 돌리기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; margin: 2rem 0; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 1rem 0; color: #333;">💡 팁</h3>
        <ul style="text-align: left;">
            <li>퀴즈쇼에서는 다양한 모드를 시도해보세요!</li>
            <li>룰렛에서는 필터를 조합해서 원하는 캐릭터를 찾아보세요!</li>
            <li>캐릭터 정보를 통해 Another Eden의 세계를 더 깊이 알아보세요!</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ===============================================
# 메인 함수
# ===============================================

def main():
    # 메인 헤더
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white;">
        <h1 style="margin: 0; color: #FFD700;">🎮 Another Eden 게임 센터</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">캐릭터 퀴즈와 룰렛을 즐겨보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 간단한 네비게이션
    st.sidebar.header("🎮 게임 메뉴")
    
    # 세션 상태에서 선택된 게임 확인
    if 'selected_game' in st.session_state:
        game_mode = st.session_state['selected_game']
        # 홈으로 돌아가기 버튼
        if st.sidebar.button("🏠 홈으로 돌아가기", use_container_width=True):
            st.session_state.pop('selected_game', None)
            st.rerun()
    else:
        game_mode = st.sidebar.selectbox(
            "게임을 선택하세요",
            ["🏠 홈", "🎯 퀴즈쇼", "🎰 캐릭터 룰렛", "📖 가이드"],
            index=0
        )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 퀴즈 모드")
    st.sidebar.markdown("- 🏷️ 이름 맞히기")
    st.sidebar.markdown("- 👤 실루엣 맞히기") 
    st.sidebar.markdown("- ⭐ 희귀도 맞히기")
    st.sidebar.markdown("- 🔥 속성 맞히기")
    st.sidebar.markdown("- ⚔️ 무기 맞히기")
    
    st.sidebar.markdown("### 🎰 룰렛 기능")
    st.sidebar.markdown("- 🔍 캐릭터 필터링")
    st.sidebar.markdown("- 🎲 랜덤 뽑기")
    st.sidebar.markdown("- 🏆 결과 표시")
    
    # 메인 컨텐츠
    if game_mode == "🏠 홈":
        show_home_page()
    elif game_mode == "🎯 퀴즈쇼":
        show_quiz_page()
    elif game_mode == "🎰 캐릭터 룰렛":
        show_roulette_page()
    elif game_mode == "📖 가이드":
        show_guide_page()

if __name__ == "__main__":
    main() 