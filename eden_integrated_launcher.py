"""
🚀 Another Eden 통합 런처
데이터 수집부터 퀴즈쇼까지 모든 기능을 하나의 앱에서 관리
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

# 페이지 설정
st.set_page_config(
    page_title="🎮 Another Eden 통합 런처",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================================
# 유틸리티 함수들
# ===============================================

def safe_icon_to_data_uri(path: str) -> str:
    """아이콘 경로를 data URI로 안전하게 변환"""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"
    
    def normalize_path(p: str) -> str:
        # numpy.float64나 다른 숫자 타입을 문자열로 변환
        if p is None or pd.isna(p):
            return ""
        p = str(p)  # 모든 타입을 문자열로 변환
        p = unicodedata.normalize("NFKC", p)
        return p.replace("\\", "/").strip().lstrip("\ufeff").replace("\u00A0", "")

    path = normalize_path(path)
    if not path or path == "" or path == "nan":
        return placeholder
    if path.startswith(("http://", "https://", "data:image")):
        return path
    
    # 이미지 파일 경로 처리
    abs_path = BASE_DIR / path
    try:
        if abs_path.exists() and abs_path.is_file():
            with open(abs_path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                ext = abs_path.suffix.lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    mime_type = f"image/{ext[1:]}" if ext != '.jpg' else "image/jpeg"
                    return f"data:{mime_type};base64,{data}"
    except:
        pass
    return placeholder

def get_character_image(char_name: str, char_index: int = None) -> str:
    """캐릭터 이름으로 이미지 경로 찾기 (개선된 버전)"""
    # character_art/icons 폴더에서 캐릭터 이미지 찾기
    icons_dir = BASE_DIR / "character_art" / "icons"
    if not icons_dir.exists():
        return ""
    
    # 모든 이미지 파일 검색
    image_files = list(icons_dir.glob("*.png"))
    if not image_files:
        return ""
    
    # 캐릭터 인덱스 기반 이미지 할당 (중복 방지)
    if char_index is not None:
        # 캐릭터 인덱스를 이미지 파일 수로 나눈 나머지로 고유 이미지 할당
        image_index = char_index % len(image_files)
        return str(image_files[image_index])
    
    # 캐릭터명 정규화 (공백 제거, 소문자)
    search_name = char_name.replace(" ", "").lower()
    
    # 1. 정확한 매칭 시도
    for file in image_files:
        file_name = file.stem.lower()
        if search_name in file_name or file_name in search_name:
            return str(file)
    
    # 2. 부분 매칭 시도 (캐릭터명의 일부가 파일명에 포함)
    for file in image_files:
        file_name = file.stem.lower()
        # 캐릭터명의 각 단어를 확인
        char_words = search_name.split()
        for word in char_words:
            if len(word) > 2 and word in file_name:
                return str(file)
    
    # 3. 해시 기반 고유 이미지 할당
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
        # 빈 값들을 문자열로 변환하여 안전하게 처리
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        # 이미지 경로 추가 (캐릭터 인덱스 기반)
        df['이미지경로'] = df.apply(lambda row: get_character_image(row['캐릭터명'], row.name), axis=1)
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return None

def load_roulette_data():
    """룰렛용 데이터 로드"""
    csv_file = "eden_roulette_data_with_personalities.csv"
    if not os.path.exists(csv_file):
        st.error("룰렛 데이터 파일이 없습니다. eden_roulette_data_with_personalities.csv 파일을 확인하세요.")
        return None, None
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # 빈 값들을 문자열로 변환하여 안전하게 처리
        for col in df.columns:
            df[col] = df[col].fillna('').astype(str)
        
        # 이미지 경로 추가 (캐릭터 인덱스 기반)
        df['이미지경로'] = df.apply(lambda row: get_character_image(row['캐릭터명'], row.name), axis=1)
        
        # 컬럼 매핑
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
        
        # 필요한 컬럼들 확인
        for k_kor, v_eng in column_map.items():
            if v_eng and v_eng not in df.columns:
                st.error(f"필요한 컬럼 '{v_eng}'이 없습니다.")
                return None, None
                
        return df, column_map
    except Exception as e:
        st.error(f"룰렛 데이터 로드 오류: {e}")
        return None, None

# ===============================================
# 퀴즈쇼 관련 함수들
# ===============================================

def create_silhouette_html(image_path: str, char_name: str = "") -> str:
    """캐릭터 실루엣 HTML 생성 (개선된 버전)"""
    icon_data = safe_icon_to_data_uri(image_path)
    return f'''
    <div style="text-align: center; margin: 20px 0;">
        <div style="width: 200px; height: 200px; margin: 0 auto; position: relative; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 15px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
            <img src="{icon_data}" 
                 style="width: 100%; height: 100%; object-fit: contain; filter: brightness(0) contrast(1.5) opacity(0.9);" 
                 alt="{char_name} 실루엣">
        </div>
        <p style="margin-top: 15px; font-style: italic; color: #666; font-size: 16px; font-weight: 500;">실루엣을 보고 캐릭터를 맞춰보세요!</p>
    </div>
    '''

def run_quiz_mode(df: pd.DataFrame, mode: str):
    """퀴즈 모드 실행 (개선된 GUI)"""
    if df is None or len(df) == 0:
        st.error("퀴즈 데이터가 없습니다.")
        return
    
    # 세션 상태 초기화
    if f'quiz_{mode}_data' not in st.session_state:
        st.session_state[f'quiz_{mode}_data'] = {
            'score': 0,
            'total': 0,
            'current_question': None,
            'show_answer': False
        }
    
    quiz_data = st.session_state[f'quiz_{mode}_data']
    
    # 헤더 섹션
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white;">
        <h2 style="margin: 0; color: #FFD700;">🎯 {mode} 퀴즈</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">캐릭터 지식을 테스트해보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 점수 및 컨트롤 섹션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # 점수 카드
        accuracy = quiz_data['score']/max(quiz_data['total'], 1)*100 if quiz_data['total'] > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 1.5rem; border-radius: 10px; text-align: center; color: white; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: #FFD700;">점수</h3>
            <h2 style="margin: 10px 0;">{quiz_data['score']}/{quiz_data['total']}</h2>
            <p style="margin: 0; font-size: 18px;">{accuracy:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # 새 문제 버튼
        if st.button("🎲 새 문제", key=f"new_{mode}", use_container_width=True):
            # 새 문제 생성
            char = df.sample(1).iloc[0]
            quiz_data['current_question'] = char
            quiz_data['show_answer'] = False
            
            # 모드별 선택지 생성
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
                    correct_attrs = char['속성명리스트'].split('|')
                    all_attrs = []
                    for attr_list in df['속성명리스트'].dropna():
                        if attr_list:
                            all_attrs.extend([x.strip() for x in attr_list.split('|')])
                    all_attrs = list(set(all_attrs))
                    wrong_attrs = [attr for attr in all_attrs if attr not in correct_attrs]
                    if len(wrong_attrs) >= 3:
                        wrong_attrs = random.sample(wrong_attrs, 3)
                    else:
                        wrong_attrs = ['화', '수', '지', '풍', '빛', '어둠']
                    all_options = correct_attrs + wrong_attrs[:3]
                    random.shuffle(all_options)
                    quiz_data['options'] = all_options[:4]
            elif mode == "무기 맞히기":
                if char.get('무기명리스트'):
                    correct_weapons = char['무기명리스트'].split('|')
                    all_weapons = []
                    for weapon_list in df['무기명리스트'].dropna():
                        if weapon_list:
                            all_weapons.extend([x.strip() for x in weapon_list.split('|')])
                    all_weapons = list(set(all_weapons))
                    wrong_weapons = [weapon for weapon in all_weapons if weapon not in correct_weapons]
                    if len(wrong_weapons) >= 3:
                        wrong_weapons = random.sample(wrong_weapons, 3)
                    else:
                        wrong_weapons = ['검', '창', '도끼', '활', '지팡이', '단검']
                    all_options = correct_weapons + wrong_weapons[:3]
                    random.shuffle(all_options)
                    quiz_data['options'] = all_options[:4]
            
            st.rerun()
        
        if quiz_data['current_question'] is not None:
            char = quiz_data['current_question']
            
            # 문제 카드
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center; color: white;">
                <h3 style="margin: 0 0 1rem 0; color: #FFD700;">문제</h3>
            """, unsafe_allow_html=True)
            
            # 모드별 문제 출제
            if mode == "이름 맞히기":
                if char['이미지경로']:
                    icon_data = safe_icon_to_data_uri(char['이미지경로'])
                    st.markdown(f'<div style="text-align: center; margin: 1rem 0;"><img src="{icon_data}" style="width: 200px; height: 200px; object-fit: contain; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size: 18px; font-weight: 600; margin: 1rem 0;">이 캐릭터의 이름은?</p>', unsafe_allow_html=True)
                
            elif mode == "실루엣 맞히기":
                if char['이미지경로']:
                    st.markdown(create_silhouette_html(char['이미지경로'], char['캐릭터명']), unsafe_allow_html=True)
                
            elif mode == "희귀도 맞히기":
                st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin: 1rem 0;"><strong>{char["캐릭터명"]}</strong>의 희귀도는?</p>', unsafe_allow_html=True)
                
            elif mode == "속성 맞히기":
                st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin: 1rem 0;"><strong>{char["캐릭터명"]}</strong>의 속성은?</p>', unsafe_allow_html=True)
                
            elif mode == "무기 맞히기":
                st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin: 1rem 0;"><strong>{char["캐릭터명"]}</strong>의 무기는?</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 선택지 표시
            if not quiz_data['show_answer']:
                if 'options' in quiz_data:
                    st.markdown('<h4 style="margin: 1rem 0; color: #333;">정답을 선택하세요:</h4>', unsafe_allow_html=True)
                    
                    # 선택지를 그리드로 표시
                    cols = st.columns(2)
                    selected = None
                    
                    for i, option in enumerate(quiz_data['options']):
                        col_idx = i % 2
                        with cols[col_idx]:
                            if st.button(option, key=f"option_{mode}_{i}", use_container_width=True):
                                selected = option
                    
                    if selected:
                        st.markdown(f'<p style="margin: 1rem 0; padding: 1rem; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196F3;"><strong>선택한 답:</strong> {selected}</p>', unsafe_allow_html=True)
                        
                        if st.button("✅ 정답 확인", key=f"check_{mode}", use_container_width=True):
                            if mode in ["이름 맞히기", "실루엣 맞히기"]:
                                correct = char['캐릭터명']
                            elif mode == "희귀도 맞히기":
                                correct = char.get('희귀도', '')
                            elif mode == "속성 맞히기":
                                correct = char.get('속성명리스트', '').split('|')[0] if char.get('속성명리스트') else ''
                            elif mode == "무기 맞히기":
                                correct = char.get('무기명리스트', '').split('|')[0] if char.get('무기명리스트') else ''
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
                <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 1.5rem; border-radius: 10px; margin: 1rem 0; text-align: center; color: white;">
                    <h3 style="margin: 0; color: #FFD700;">🎉 문제 완료!</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # 캐릭터 정보 카드
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if char['이미지경로']:
                        icon_data = safe_icon_to_data_uri(char['이미지경로'])
                        st.markdown(f'<div style="text-align: center;"><img src="{icon_data}" style="width: 150px; height: 150px; object-fit: contain; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);"></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                        <h4 style="margin: 0 0 1rem 0; color: #333;">캐릭터 정보</h4>
                        <p style="margin: 0.5rem 0;"><strong>이름:</strong> {char['캐릭터명']}</p>
                        <p style="margin: 0.5rem 0;"><strong>희귀도:</strong> {char.get('희귀도', '')}</p>
                        <p style="margin: 0.5rem 0;"><strong>속성:</strong> {char.get('속성명리스트', '')}</p>
                        <p style="margin: 0.5rem 0;"><strong>무기:</strong> {char.get('무기명리스트', '')}</p>
                        <p style="margin: 0.5rem 0;"><strong>퍼스널리티:</strong> {char.get('개성(퍼스널리티)', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ===============================================
# 룰렛 관련 함수들
# ===============================================

def create_character_card(char_data: pd.Series, column_map: dict) -> str:
    """캐릭터 카드 HTML 생성"""
    name = char_data[column_map['이름']]
    rarity = char_data[column_map['희귀도']]
    icon_data = safe_icon_to_data_uri(char_data[column_map['캐릭터아이콘경로']])
    
    return f'''
    <div style="border: 2px solid #ddd; border-radius: 15px; padding: 20px; margin: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">
        <img src="{icon_data}" style="width: 100px; height: 100px; object-fit: contain; border-radius: 10px; margin-bottom: 10px;">
        <h3 style="margin: 10px 0; color: #FFD700;">{name}</h3>
        <p style="margin: 5px 0;"><strong>희귀도:</strong> {rarity}</p>
        <p style="margin: 5px 0;"><strong>속성:</strong> {char_data.get(column_map['속성명'], '')}</p>
        <p style="margin: 5px 0;"><strong>무기:</strong> {char_data.get(column_map['무기명'], '')}</p>
        <p style="margin: 5px 0;"><strong>퍼스널리티:</strong> {char_data.get('개성(퍼스널리티)', '')}</p>
    </div>
    '''

def run_roulette():
    """룰렛 게임 실행 (개선된 GUI)"""
    df, column_map = load_roulette_data()
    if df is None:
        return
    
    # 헤더 섹션
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white;">
        <h2 style="margin: 0; color: #FFD700;">🎰 캐릭터 룰렛</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">필터를 설정하고 랜덤 캐릭터를 뽑아보세요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 필터링 섹션
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 1rem 0; color: #333;">🔍 필터 설정</h3>
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
    <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 1rem; border-radius: 10px; margin-bottom: 2rem; text-align: center; color: white;">
        <h4 style="margin: 0;">📊 필터 결과: {len(filtered_df)}명의 캐릭터</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 룰렛 실행 섹션
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎲 룰렛 돌리기!", key="roulette_spin", use_container_width=True):
            if len(filtered_df) > 0:
                winner = filtered_df.sample(1).iloc[0]
                st.session_state['roulette_winner'] = winner
                
                # 애니메이션 효과
                with st.spinner("룰렛 돌리는 중..."):
                    time.sleep(1)
                
                st.balloons()
                st.success("🎉 당첨!")
    
    # 당첨 결과 표시
    if 'roulette_winner' in st.session_state:
        winner = st.session_state['roulette_winner']
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0; text-align: center; color: white;">
            <h3 style="margin: 0; color: #333;">🏆 당첨 캐릭터</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(create_character_card(winner, column_map), unsafe_allow_html=True)

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
    
    .quiz-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_file_status():
    """프로젝트 파일들의 상태를 체크"""
    files_status = {}
    
    # 필수 파일들
    essential_files = {
        "eden_roulette_data_with_personalities.csv": "룰렛/퀴즈 데이터",
        "Matching_names.csv": "캐릭터명 매핑",
        "another_eden_characters_detailed.xlsx": "상세 캐릭터 데이터",
        "character_art/": "캐릭터 이미지 폴더"
    }
    
    # 앱 파일들
    app_files = {
        "eden_quiz_app.py": "퀴즈쇼 앱",
        "streamlit_eden_restructure.py": "룰렛 앱"
    }
    
    all_files = {**essential_files, **app_files}
    
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
    
    # 사이드바 - 빠른 네비게이션
    st.sidebar.header("🚀 빠른 네비게이션")
    
    if st.sidebar.button("🎯 퀴즈쇼 게임", use_container_width=True):
        st.sidebar.success("🎮 게임 센터의 퀴즈쇼 탭으로 이동하세요!")
        st.sidebar.info("탭 2: 게임 센터 > 퀴즈쇼에서 바로 플레이할 수 있습니다.")
    
    if st.sidebar.button("🎰 캐릭터 룰렛", use_container_width=True):
        st.sidebar.success("🎰 게임 센터의 룰렛 탭으로 이동하세요!")
        st.sidebar.info("탭 2: 게임 센터 > 캐릭터 룰렛에서 바로 플레이할 수 있습니다.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 퀴즈 모드")
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 프로젝트 상태", "🎮 게임 센터", "📱 배포 정보", "📖 가이드"])
    
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
        st.header("🎮 Another Eden 게임 센터")
        
        # 게임 선택 탭
        game_tab1, game_tab2 = st.tabs(["🎯 퀴즈쇼", "🎰 캐릭터 룰렛"])
        
        with game_tab1:
            st.markdown("""
            <div class="quiz-container">
                <h2>🎯 Another Eden 퀴즈쇼</h2>
                <p>다양한 모드로 캐릭터 지식을 테스트해보세요!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 퀴즈 모드 선택
            quiz_modes = ["이름 맞히기", "실루엣 맞히기", "희귀도 맞히기", "속성 맞히기", "무기 맞히기"]
            selected_mode = st.selectbox("퀴즈 모드 선택", quiz_modes, key="quiz_mode_select")
            
            # 퀴즈 데이터 로드
            quiz_df = load_quiz_data()
            if quiz_df is not None:
                run_quiz_mode(quiz_df, selected_mode)
            else:
                st.error("퀴즈 데이터를 불러올 수 없습니다. CSV 파일을 확인하세요.")
        
        with game_tab2:
            st.markdown("""
            <div class="quiz-container">
                <h2>🎰 캐릭터 룰렛</h2>
                <p>필터를 설정하고 랜덤 캐릭터를 뽑아보세요!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 룰렛 실행
            run_roulette()
    
    with tab3:
        st.header("📱 배포 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌐 웹 배포")
            
            st.markdown("""
            **Streamlit Community Cloud 배포**
            - 무료 호스팅 서비스
            - GitHub 연동으로 자동 배포
            - 실시간 코드 업데이트 반영
            """)
            
            if st.button("배포 가이드 보기", use_container_width=True):
                st.info("""
                **배포 단계:**
                1. GitHub 저장소 확인
                2. Streamlit Community Cloud 접속
                3. 저장소 연결 및 앱 배포
                4. 공개 URL 생성 완료
                """)
        
        with col2:
            st.subheader("📊 프로젝트 정보")
            
            project_info = {
                "프로젝트명": "Another Eden Quiz Show",
                "개발 언어": "Python 3.9+",
                "웹 프레임워크": "Streamlit",
                "주요 라이브러리": "pandas, requests, openpyxl",
                "데이터 소스": "anothereden.wiki"
            }
            
            for key, value in project_info.items():
                st.write(f"**{key}**: {value}")
                
            st.markdown("---")
            
            st.subheader("✨ 주요 기능")
            st.markdown("- 🎯 5가지 퀴즈 모드")
            st.markdown("- 🎰 캐릭터 룰렛")
            st.markdown("- 🔍 캐릭터 검색 및 필터링")
            st.markdown("- 📊 퍼스널리티 데이터")
            st.markdown("- 🖼️ 캐릭터 이미지 표시")
    
    with tab4:
        st.header("📖 사용 가이드")
        
        st.markdown("""
        ## 🚀 빠른 시작 가이드
        
        ### 앱 실행 방법
        1. **퀴즈쇼 앱**: 
           ```bash
           streamlit run eden_quiz_app.py --server.port 8502
           ```
        2. **룰렛 앱**: 
           ```bash
           streamlit run streamlit_eden_restructure.py --server.port 8503
           ```
        
        ### 즐기기!
        - 🎯 다양한 퀴즈 모드로 캐릭터 지식 테스트
        - 🎰 룰렛으로 랜덤 캐릭터 뽑기
        - 🔍 필터링으로 원하는 캐릭터 찾기
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ## 🎮 앱 기능들
        
        ### 🎯 퀴즈쇼 앱
        - **5가지 퀴즈 모드**: 이름, 희귀도, 속성, 무기, 실루엣
        - **실시간 점수 시스템**: 정답률 추적
        - **시각적 힌트**: 캐릭터 이미지 및 실루엣
        - **상세 정보 표시**: 정답 후 캐릭터 정보 제공
        
        ### 🎰 룰렛 앱
        - **슬롯머신 스타일**: 시각적인 룰렛 애니메이션
        - **캐릭터 필터링**: 희귀도, 속성, 무기별 필터
        - **캐릭터 카드**: 상세 정보 표시
        - **퍼스널리티 데이터**: 캐릭터별 성격 특성
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ## 🛠️ 트러블슈팅
        
        ### 자주 발생하는 문제들
        
        **Q: 앱이 실행되지 않습니다.**
        A: Python과 필요한 라이브러리가 설치되어 있는지 확인하세요.
        
        **Q: 캐릭터 이미지가 표시되지 않습니다.**
        A: character_art 폴더와 하위 이미지들이 있는지 확인하세요.
        
        **Q: 데이터가 로드되지 않습니다.**
        A: 필요한 CSV/Excel 파일들이 있는지 확인하세요.
        
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