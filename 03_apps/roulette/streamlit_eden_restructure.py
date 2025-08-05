"""
Streamlit 애플리케이션 스크립트.
Another Eden 캐릭터 정보를 표시하고, 필터링하며, 룰렛(슬롯머신) 기능을 제공합니다.
"""
import streamlit as st
import pandas as pd
import random
import os
import re
import html
import base64
import unicodedata
import uuid
from pathlib import Path
import streamlit.components.v1 as components

# 프로젝트 루트 및 데이터 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = BASE_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 프로젝트 루트 절대경로 (이 스크립트 기준)
# BASE_DIR = Path(__file__).parent.resolve()

# Streamlit 페이지 설정 (스크립트 최상단으로 이동)
st.set_page_config(page_title="🎲 Another Eden 캐릭터 룰렛", layout="wide")

# CSS 스타일 추가
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .roulette-container {
            padding: 1rem !important;
        }
        
        .filter-container {
            padding: 0.5rem !important;
        }
    }
    
    .roulette-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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
    
    .character-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .character-card:hover {
        border-color: #FFD700;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    }
    
    .winner-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000;
        border: 3px solid #FFD700;
        animation: pulse 0.6s ease-in-out;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .slot-machine {
        background: rgba(0, 0, 0, 0.8);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        text-align: center;
        border: 3px solid #FFD700;
    }
    
    .slot-item {
        display: inline-block;
        margin: 0.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .slot-item img {
        width: 60px;
        height: 60px;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button {
        border-radius: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 전역 디버그 로거 및 안전 아이콘 변환 헬퍼
# ─────────────────────────────────────────────

def log_debug(message: str):
    """디버그 모드 시 session_state 에 로그를 누적 저장."""
    if "debug_logs" not in st.session_state:
        st.session_state["debug_logs"] = []
    st.session_state["debug_logs"].append(message)


def safe_icon_to_data_uri(path: any) -> str:
    """아이콘 경로를 data URI로 안전하게 변환합니다. NaN 값을 포함한 모든 입력을 처리합니다."""
    placeholder = "data:image/gif;base64,R0lGODlhEAAQAIABAP///wAAACH5BAEKAAEALAAAAAAQABAAAAIijI+py+0Po5yUFQA7"

    # 1. NaN 또는 None 값인지 확인
    if pd.isna(path):
        log_debug("[EmptyVal] icon path is NaN or None.")
        return placeholder

    # 2. 문자열로 변환
    path_str = str(path)

    # 3. 경로 정규화 (공백 제거, 유니코드 정규화 등)
    try:
        normalized_path = unicodedata.normalize("NFKC", path_str)
        normalized_path = normalized_path.replace("\\", "/").strip().lstrip("\ufeff").replace("\u00A0", "")
    except TypeError:
        # 혹시 모를 타입 오류 발생 시 안전하게 처리
        log_debug(f"[TypeError] Normalization failed for path: {path_str}")
        return placeholder

    # 4. 정규화 후 경로가 비어있는지 확인
    if not normalized_path:
        log_debug("[EmptyVal] icon path is empty after normalization.")
        return placeholder

    path = normalized_path
    if path.startswith(("http://", "https://", "data:image")):
        return path
    
    if not os.path.isabs(path):
        # 상대 경로인 경우, 정확한 이미지 디렉토리에서 검색
        search_dirs = [
            IMAGE_DIR,  # 메인 이미지 디렉토리
            DATA_DIR / "images",  # 백업 검색 경로
            Path.cwd() / "04_data" / "images" / "character_art",  # 프로젝트 루트 기준
            Path(path).parent if Path(path).parent.exists() else Path.cwd()
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
        log_debug(f"[NoFile] {path}")
        return placeholder
    
    try:
        with open(path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{b64_str}"
    except Exception as exc:
        log_debug(f"[EncodeErr] {path}: {exc}")
        return placeholder

# ─────────────────────────────────────────────
# Streamlit 고급 GUI 구현
# ─────────────────────────────────────────────

def slot_machine_display(items, winner_index, item_display_duration_ms=50, spin_duration_s=3):
    """
    Streamlit HTML 컴포넌트를 사용하여 슬롯머신 형태의 UI를 생성하고 애니메이션을 처리합니다.
    캐릭터 이미지가 빠르게 순환하다가 미리 결정된 당첨자에게 멈추는 효과를 보여줍니다.

    Args:
        items (list): 슬롯머신에 표시될 아이템 리스트.
                      각 아이템은 {'name': str, 'icon_base64': str} 형태의 딕셔너리여야 합니다.
                      'icon_base64'는 이미지의 Base64 인코딩된 데이터입니다.
        winner_index (int): `items` 리스트 내에서 당첨자로 결정된 아이템의 인덱스.
        item_display_duration_ms (int, optional): 스핀 중 각 아이템이 화면에 표시되는 시간 (밀리초).
                                                값이 작을수록 빠르게 지나갑니다. 기본값 50.
        spin_duration_s (int, optional): 전체 스핀 애니메이션이 지속되는 시간 (초).
                                       이 시간 동안 아이템들이 순환한 후 당첨자를 표시합니다. 기본값 3.
    """
    # items: [{'name': ..., 'icon_base64': ...}]
    # winner_index: 당첨자 인덱스
    # item_display_duration_ms: 각 아이템 표시 시간 (밀리초)
    # spin_duration_s: 전체 스핀 지속 시간 (초) - 이 시간 동안 아이템들이 순환한 후 당첨자를 표시합니다.
    
    slot_id = f"slot_machine_{uuid.uuid4().hex[:8]}"
    # 아이템이 없거나 적을 경우 처리
    if not items:
        st.warning("슬롯에 표시할 아이템이 없습니다.")
        return
    
    num_items = len(items)
    # winner_index 유효성 검사
    if not (0 <= winner_index < num_items):
        st.error(f"잘못된 당첨자 인덱스: {winner_index}. 아이템 개수: {num_items}")
        return

    # JavaScript에서 사용할 수 있도록 아이템 리스트 (이미지 데이터만)와 당첨자 이름 준비
    # items는 dict 리스트이므로, icon_base64와 name을 추출
    item_images_js = [item['icon_base64'] for item in items]
    winner_name_js = items[winner_index]['name']

    html_content = f"""
    <style>
        #{slot_id}_container {{
            text-align: center;
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
            max-width: 350px; /* 슬롯머신 최대 너비 */
            margin: 20px auto; /* 페이지 중앙 정렬 */
        }}
        #{slot_id}_image_slot {{
            width: 280px;  /* 이미지 표시 너비 */
            height: 280px; /* 이미지 표시 높이 */
            border: 3px solid #333;
            background-color: #fff;
            margin: 0 auto 20px auto; /* 위아래 마진, 좌우 중앙 */
            overflow: hidden; /* 이미지가 넘칠 경우 숨김 */
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        #{slot_id}_image_slot img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain; /* 이미지 비율 유지하며 맞춤 */
            border-radius: 5px;
        }}
        #{slot_id}_result_name {{
            font-size: 1.2em;
            color: #e74c3c;
            font-weight: bold;
            margin-top: 10px;
            min-height: 1.5em; /* 이름 표시될 공간 확보 */
        }}
    </style>

    <div id="{slot_id}_container">
        <div id="{slot_id}_image_slot">
            <img id="{slot_id}_img_tag" src="{item_images_js[0]}" alt="캐릭터 이미지">
        </div>
        <div id="{slot_id}_result_name"></div>
    </div>

    <!-- Audio Elements -->
    <audio id="{slot_id}_spin_start_sound" src="audio/spin_start.mp3" preload="auto"></audio>
    <audio id="{slot_id}_spin_stop_sound" src="audio/spin_stop.mp3" preload="auto"></audio>
    <audio id="{slot_id}_win_sound" src="audio/win_sound.mp3" preload="auto"></audio>

    <script>
    (function() {{
        const slotImage = document.getElementById("{slot_id}_img_tag");
        const resultNameDisplay = document.getElementById("{slot_id}_result_name");
        const spinStartSound = document.getElementById("{slot_id}_spin_start_sound");
        const spinStopSound = document.getElementById("{slot_id}_spin_stop_sound");
        const winSound = document.getElementById("{slot_id}_win_sound");

        const items = {item_images_js};
        const winnerIdx = {winner_index};
        const winnerName = "{winner_name_js}";
        const displayDuration = {item_display_duration_ms};
        const totalSpinTime = {spin_duration_s * 1000}; // 초를 밀리초로
        const numItems = items.length;

        if (numItems === 0) return;

        let currentIndex = 0;
        let spinInterval;
        let startTime = Date.now();
        
        // 초기 이미지를 당첨자로 설정 (깜빡임 방지용으로 첫 프레임)
        // 또는 첫번째 아이템으로 시작할 수도 있음
        // slotImage.src = items[winnerIdx]; // 기존 코드: 스포일러 문제 발생
        if (numItems > 0) {{
            slotImage.src = items[0]; // 변경: 첫 번째 아이템 이미지로 시작
        }} else {{
            // 아이템이 없을 경우 대비 (이론상 함수 초반에 걸러짐)
            slotImage.src = "https://via.placeholder.com/280?text=NoItems"; 
        }}

        // 스핀 시작 시 사운드 재생 (오류 발생 시 무시)
        spinStartSound.play().catch(e => console.log('Spin start sound not found or failed to play.'));

        function spin() {{
            currentIndex = (currentIndex + 1) % numItems;
            slotImage.src = items[currentIndex];
            
            let elapsedTime = Date.now() - startTime;
            
            // 스핀 종료 조건: 총 스핀 시간을 초과했거나, 특정 아이템에 도달하기 직전
            if (elapsedTime >= totalSpinTime) {{
                clearInterval(spinInterval);
                spinStopSound.play().catch(e => console.log('Spin stop sound not found or failed to play.')); // 스핀 종료 사운드 재생
                slotImage.src = items[winnerIdx]; // 최종 당첨자 이미지로 설정
                resultNameDisplay.innerHTML = "🎉 " + winnerName + " 🎉";
                // 애니메이션을 좀 더 부드럽게 멈추는 효과 (옵션)
                slotImage.style.transition = "transform 0.3s ease-out";
                slotImage.style.transform = "scale(1.05)";
                setTimeout(() => {{ 
                    slotImage.style.transform = "scale(1)"; 
                    winSound.play().catch(e => console.log('Win sound not found or failed to play.')); // 당첨 사운드 재생
                }}, 300);
                return;
            }}
        }}
        
        // 첫 이미지를 잠깐 보여주고 스핀 시작 (선택 사항)
        setTimeout(() => {{
            startTime = Date.now(); // 스핀 시작 시간 재설정
            spinInterval = setInterval(spin, displayDuration);
        }}, 100); // 0.5초 후 스핀 시작 -> 0.1초 후 스핀 시작으로 변경
        
    }})();
    </script>
    """
    components.html(html_content, height=450) # 높이 조절

def get_image_base64(image_path):
    """
    지정된 경로의 이미지를 읽어 Base64로 인코딩된 문자열을 반환합니다.
    Streamlit HTML 컴포넌트 내에 이미지를 직접 삽입할 때 사용됩니다.

    Args:
        image_path (str): Base64로 인코딩할 이미지 파일 경로.

    Returns:
        str | None: Base64로 인코딩된 이미지 문자열 (UTF-8 디코딩됨).
                     파일을 읽거나 인코딩하는 중 오류 발생 시 None 반환.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        # print(f"Error encoding image {image_path}: {e}") # 디버깅용
        return None

@st.cache_data
def load_and_prepare_data(csv_path, personalities_csv_path, column_map_config):
    """
    기본 데이터와 성격 데이터를 로드하고 병합하여 준비합니다.
    """
    if not Path(csv_path).exists() or not Path(personalities_csv_path).exists():
        st.error(f"데이터 파일을 찾을 수 없습니다: {csv_path} 또는 {personalities_csv_path}")
        return None, *(None,)*7

    try:
        df_main = pd.read_csv(csv_path, encoding='utf-8-sig')
        df_pers = pd.read_csv(personalities_csv_path, encoding='utf-8-sig')
        log_debug(f"[CSVLoad] {len(df_main)} records from main, {len(df_pers)} from personalities.")

        # 데이터 병합
        df = pd.merge(df_main, df_pers[['Korean_Name', 'Personalities_List']],
                      left_on='캐릭터명', right_on='Korean_Name', how='left')
        
        # 병합 후 중복 컬럼 제거
        df.drop(columns=['Korean_Name'], inplace=True)
        
        # 'Personalities_List' 컬럼의 NaN 값을 빈 문자열로 대체
        df['Personalities_List'] = df['Personalities_List'].fillna('')
        column_map_config['personalities'] = 'Personalities_List' # 맵에 추가

    except Exception as e:
        st.error(f"데이터 파일을 로드하고 병합하는 중 오류 발생: {e}")
        return None, *(None,)*7

    # 컬럼 존재 유효성 검사
    for internal_key, csv_col_name in column_map_config.items():
        if csv_col_name not in df.columns:
            log_debug(f"[경고] '{csv_col_name}' 컬럼이 없어 무시됩니다.")
            df[csv_col_name] = None

    # 반환할 컬럼명 추출
    name_col = column_map_config.get('이름')
    char_icon_col = column_map_config.get('캐릭터아이콘경로')
    rarity_col = column_map_config.get('희귀도')
    attribute_col = column_map_config.get('속성명') # main에서 사용하는 키는 '속성명'
    weapon_col = column_map_config.get('무기명') # main에서 사용하는 키는 '무기명'
    personality_col = column_map_config.get('성격특성')

    return df, name_col, char_icon_col, rarity_col, attribute_col, weapon_col, personality_col

def create_character_card_html(row: pd.Series, column_map: dict, is_winner: bool = False) -> str:
    """
    캐릭터 데이터 한 행을 받아 스타일링된 HTML 카드 문자열을 생성합니다.

    Args:
        row: 캐릭터 정보가 담긴 pandas Series.
        column_map: 컬럼 이름 매핑.
        is_winner: 룰렛 당첨 여부. True이면 강조 스타일이 적용됩니다.

    Returns:
        생성된 HTML 카드 문자열.
    """
    def build_list(val: str):
        if isinstance(val, str) and val:
            return [item.strip() for item in re.split('[|,]', val) if item.strip()]
        return []

    def create_icon_group_html(names_raw, icons_raw):
        names = build_list(names_raw)
        icon_paths = build_list(icons_raw)
        if not names and not icon_paths:
            return '<div class="icon-container"><span class="no-data">-</span></div>'

        max_len = max(len(names), len(icon_paths))
        names.extend([''] * (max_len - len(names)))
        icon_paths.extend([''] * (max_len - len(icon_paths)))
        
        items_html = ""
        for name, path in zip(names, icon_paths):
            icon_uri = safe_icon_to_data_uri(path)
            if name or "data:image/png;base64," in icon_uri:
                escaped_name = html.escape(name)
                # 아이콘과 텍스트를 함께 표시 (텍스트가 없으면 아이콘만 표시)
                text_html = f'<span class="eden-text">{escaped_name}</span>' if escaped_name else ''
                items_html += (
                    f'<div class="eden-item" title="{escaped_name}">'
                    f'<img src="{icon_uri}" alt="{escaped_name}">{text_html}'
                    f'</div>'
                )
        
        return f'<div class="icon-container">{items_html}</div>'

    try:
        name_col = column_map['이름']
        char_icon_col = column_map['캐릭터아이콘경로']
        rarity_col = column_map['희귀도']
        attr_col, attr_icon_col = column_map['속성명'], column_map['속성아이콘']
        weapon_col, weapon_icon_col = column_map['무기명'], column_map['무기아이콘']
        armor_col, armor_icon_col = column_map['방어구명'], column_map['방어구아이콘']

        char_icon_uri = safe_icon_to_data_uri(row.get(char_icon_col, ''))
        char_name = html.escape(str(row.get(name_col, '')))
        rarity = html.escape(str(row.get(rarity_col, '')))
        
        attr_html = create_icon_group_html(row.get(attr_col, ""), row.get(attr_icon_col, ""))
        weapon_html = create_icon_group_html(row.get(weapon_col, ""), row.get(weapon_icon_col, ""))
        armor_html = create_icon_group_html(row.get(armor_col, ""), row.get(armor_icon_col, ""))

        winner_class = "winner-card" if is_winner else ""

        return f"""
        <div class="eden-card {winner_class}">
            <div class="card-header">
                <img src="{char_icon_uri}" class="char-img" alt="{char_name}">
                <h4>{char_name} <span>({rarity})</span></h4>
            </div>
            <div class="card-body">
                <div class="info-group">{attr_html}</div>
                <div class="info-group">{weapon_html}</div>
                <div class="info-group">{armor_html}</div>
            </div>
        </div>
        """
    except Exception as e:
        log_debug(f"카드 생성 오류: {row.get(name_col, 'N/A')}, 오류: {e}")
        return "<div class='eden-card error-card'><p>카드 표시 오류</p></div>"

def main():
    """메인 애플리케이션 함수"""
    st.markdown("### Another Eden 캐릭터 룰렛")
    
    # 정확한 데이터 파일 경로 사용
    default_csv_path = CSV_DIR / "eden_roulette_data.csv"
    
    if not default_csv_path.exists():
        st.warning(f"데이터 파일을 찾을 수 없습니다: {default_csv_path}")
        st.info("📡 메인 런쳐에서 '데이터 스크래퍼 실행'을 클릭하여 데이터를 생성하세요.")
        return

    # --- 데이터 로드 및 준비 ---
    csv_path = st.sidebar.text_input("CSV 파일 경로", value=str(default_csv_path))
    column_map = {
        '희귀도': '희귀도', '이름': '캐릭터명', '캐릭터아이콘경로': '캐릭터아이콘경로',
        '속성명': '속성명리스트', '속성아이콘': '속성_아이콘경로리스트',
        '무기명': '무기명리스트', '무기아이콘': '무기_아이콘경로리스트',
        '방어구명': '방어구명리스트', '방어구아이콘': '방어구_아이콘경로리스트',
    }
    personalities_csv_path = CSV_DIR / 'character_personalities.csv'
    result = load_and_prepare_data(
        csv_path=csv_path,
        personalities_csv_path=personalities_csv_path,
        column_map_config=column_map
    )
    
    if result[0] is None:
        st.error("데이터 로드에 실패했습니다.")
        return
        
    df, name_col, char_icon_col, rarity_col, element_col, weapon_col, personality_col = result

    # ── 명칭 교정: '주먹' → '권갑' ──
    weapon_col_name = column_map['무기명']
    if weapon_col_name in df.columns:
        df[weapon_col_name] = df[weapon_col_name].astype(str).apply(lambda s: s.replace('주먹', '권갑'))

    # ── 성급(희귀도) 정규화: 복수 표기 시 최고 성급만 남기기 ──
    def normalize_rarity(val: str) -> str:
        if not isinstance(val, str):
            return val
        val = val.strip()
        if not val:
            return val
        # SA 여부
        has_sa = 'SA' in val
        # 모든 숫자 추출
        nums = re.findall(r'(\d)(?=★)', val)
        if nums:
            max_star = max(int(n) for n in nums)
            return f"{max_star}★{' SA' if has_sa else ''}"
        return val

    rarity_col_name = column_map['희귀도']
    if rarity_col_name in df.columns:
        df[rarity_col_name] = df[rarity_col_name].astype(str).apply(normalize_rarity)

    if df is None: return

    # --- 사이드바 필터 --- 
    with st.sidebar.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.header("🔎 필터 및 검색")
        all_attrs = sorted(set(item for sublist in df[column_map['속성명']].dropna().apply(lambda x: re.split('[|,]', x)) for item in sublist if item.strip()))
        
        sel_rarity = st.multiselect("희귀도", sorted(df[column_map['희귀도']].dropna().unique()))
        sel_attr = st.multiselect("속성 (AND 조건)", all_attrs)
        sel_weapon = st.multiselect("무기", sorted(df[column_map['무기명']].dropna().unique()))
        search_name = st.text_input("이름/성격 검색")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 필터링 로직 ---
    filtered_df = df.copy()
    if sel_rarity: filtered_df = filtered_df[filtered_df[column_map['희귀도']].isin(sel_rarity)]
    if sel_weapon: filtered_df = filtered_df[filtered_df[column_map['무기명']].isin(sel_weapon)]
    if sel_attr:
        for attr in sel_attr:
            filtered_df = filtered_df[filtered_df[column_map['속성명']].str.contains(attr, na=False, regex=False)]
    if search_name:
        search_cols = [column_map['이름'], '성격1', '성격2', '성격3', '성격4']
        filtered_df = filtered_df[filtered_df[search_cols].apply(
            lambda row: row.astype(str).str.contains(search_name, case=False, na=False).any(), axis=1
        )]

    # --- 룰렛 기능 ---
    with st.sidebar.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.header("🎰 룰렛")
        if st.button("룰렛 돌리기!", use_container_width=True, key="roulette_button"):
            st.markdown('<div class="roulette-button">', unsafe_allow_html=True)
        if not filtered_df.empty:
            winner_series = filtered_df.sample(1).iloc[0]
            st.session_state['roulette_winner'] = winner_series.to_dict()
            
            # 슬롯머신용 데이터 준비
            roulette_candidates = filtered_df.sample(n=min(len(filtered_df), 50))
            st.session_state['roulette_items'] = [
                {"name": r[column_map['이름']], "icon_base64": safe_icon_to_data_uri(r[column_map['캐릭터아이콘경로']])}
                for _, r in roulette_candidates.iterrows()
            ]
            # 당첨자를 후보 리스트의 특정 위치에 삽입
            winner_item = {"name": winner_series[column_map['이름']], "icon_base64": safe_icon_to_data_uri(winner_series[column_map['캐릭터아이콘경로']])}
            winner_index = random.randint(0, len(st.session_state['roulette_items']) -1)
            st.session_state['roulette_items'][winner_index] = winner_item
            st.session_state['roulette_winner_index'] = winner_index
            st.session_state['roulette_trigger'] = True  # 애니메이션 1회용 트리거
        else:
            st.sidebar.warning("필터링된 캐릭터가 없습니다.")
            st.session_state.pop('roulette_winner', None)

    # <<< 사이드바 하단 저작권 정보 (올바른 위치에 수정 완료) >>>
    st.sidebar.markdown("---") 
    st.sidebar.caption(
        """
        데이터 출처: [Another Eden Wiki](https://anothereden.wiki/w/Another_Eden_Wiki)  
        모든 캐릭터 이미지의 저작권은 © WFS에 있습니다.
        """
    )
    

    # 필터 변경 시 기존 룰렛 데이터 초기화 (선택적)
    current_filter_key = (
        tuple(sorted(sel_rarity)),
        tuple(sorted(sel_attr)),
        tuple(sorted(sel_weapon)),
        search_name.strip().lower()
    )
    if 'prev_filter_key' in st.session_state and st.session_state['prev_filter_key'] != current_filter_key:
        # 필터가 바뀌면 룰렛 결과 초기화
        st.session_state.pop('roulette_items', None)
        st.session_state.pop('roulette_winner_index', None)
        st.session_state.pop('roulette_trigger', None)
    st.session_state['prev_filter_key'] = current_filter_key

    # --- 룰렛 결과 표시 ---
    if st.session_state.get('roulette_trigger'):
        # 버튼 눌린 직후 애니메이션 1회 실행
        slot_machine_display(
            items=st.session_state['roulette_items'],
            winner_index=st.session_state['roulette_winner_index'],
            spin_duration_s=5
        )
        # 트리거 끄기 -> 재실행 시 애니메이션 반복 방지
        st.session_state['roulette_trigger'] = False

    # --- 캐릭터 카드 그리드 표시 ---
    st.markdown(f"#### 총 {len(filtered_df)}명")
    winner_name = st.session_state.get('roulette_winner', {}).get(column_map['이름'])

    card_html_list = [
        create_character_card_html(row, column_map, is_winner=(row[column_map['이름']] == winner_name))
        for _, row in filtered_df.iterrows()
    ]

    if not card_html_list:
        st.info("표시할 캐릭터가 없습니다. 필터 조건을 확인해주세요.")
    else:
        card_grid_html = "<div class='card-grid'>" + "".join(card_html_list) + "</div>"
        # 동적 높이 계산 (카드 한 줄의 높이 ~300px, 카드 사이 gap 20px)
        rows = (len(card_html_list) + 3) // 4 # 한 줄에 4개 카드를 기준으로 줄 수 계산
        container_height = max(320, rows * 300 + (rows - 1) * 20)

        html_with_styles = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
            
            * {{ font-family: 'Noto Sans KR', sans-serif; }}

            /* 메인 룰렛 버튼 스타일 */
            .stButton > button {{
                width: 100%;
                height: 3.8rem;
                font-size: 1.5rem;
                font-weight: 700;
                background: linear-gradient(45deg, #ff6b6b, #f06595);
                color: white;
                border: none;
                border-radius: 15px;
                margin: 1.5rem 0;
                transition: all 0.3s ease;
                box-shadow: 0 5px 20px rgba(240, 101, 149, 0.5);
            }}
            .stButton > button:hover {{
                transform: translateY(-5px);
                box-shadow: 0 9px 30px rgba(240, 101, 149, 0.7);
            }}
            .stButton > button:active {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(240, 101, 149, 0.6);
            }}
            
            .card-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
                gap: 25px; 
                padding: 20px 0;
            }}
            
            .eden-card {{
                display: flex;
                flex-direction: column;
                border: 1px solid #e9ecef;
                border-radius: 20px;
                margin: 12px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.07);
                transition: all 0.3s ease;
                background-color: #ffffff;
                overflow: hidden;
                height: 100%;
            }}
            
            .eden-card:hover {{
                transform: translateY(-6px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border-color: #764ba2;
            }}

            .eden-card.winner-card .card-header {{
                background: linear-gradient(135deg, #fff9e6, #fffbf0);
                border-bottom-color: #FFD700;
            }}
            
            .eden-card .char-img {{
                width: 70px;
                height: 70px; 
                object-fit: contain; 
                margin-right: 18px;
                border-radius: 16px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                background-color: #f8f9fa;
            }}
            
            .eden-card:hover .char-img {{
                transform: scale(1.1) rotate(5deg);
            }}
            
            .eden-card h4 {{
                margin: 0; 
                font-size: 1.3em;
                font-weight: 700; 
                color: #2c3e50;
                line-height: 1.3;
            }}

            /* Other styles from the original f-string... */
            .eden-card.winner-card h4 {{
                color: #b8860b;
                text-shadow: 1px 1px 2px rgba(255, 215, 0, 0.3);
            }}
            
            .eden-card h4 span {{
                font-size: 0.85em; 
                color: #7f8c8d;
                font-weight: 400;
            }}
            
            .eden-card .card-body {{
                padding: 18px; 
                flex-grow: 1;
                background: rgba(255, 255, 255, 0.7);
            }}
            
            .eden-card.winner-card .card-body {{
                background: rgba(255, 249, 230, 0.8);
            }}
            
            .eden-card .info-group {{
                margin-bottom: 12px;
                padding: 8px 0;
            }}
            
            .eden-card .icon-container {{
                display: flex; 
                flex-wrap: wrap; 
                align-items: center; 
                gap: 8px; 
                min-height: 35px;
                padding: 5px 0;
            }}
            
            .eden-card .eden-item {{
                display: flex; 
                align-items: center; 
                gap: 6px;
                background: rgba(102, 126, 234, 0.1);
                padding: 4px 8px;
                border-radius: 12px;
                transition: all 0.3s ease;
            }}
            
            .eden-card .eden-item:hover {{
                background: rgba(102, 126, 234, 0.2);
                transform: scale(1.05);
            }}
            
            .eden-card .eden-item img {{
                width: 28px; 
                height: 28px; 
                object-fit: contain;
                border-radius: 4px;
            }}
            
            .eden-card .eden-text {{
                font-size: 0.9em; 
                color: #495057;
                font-weight: 500;
            }}
            
            .eden-card .no-data {{
                color: #adb5bd; 
                font-style: italic;
                font-size: 0.85em;
            }}
            
            .eden-card.error-card {{
                justify-content: center; 
                align-items: center; 
                color: #e74c3c;
                font-weight: 500;
                background: linear-gradient(145deg, #fdf2f2, #fef5f5);
            }}

        </style>
        {card_grid_html}
        """
        st.components.v1.html(html_with_styles, height=container_height)

if __name__ == "__main__":
    main()