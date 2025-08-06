import os
import pandas as pd
import re
import math
import streamlit as st
import subprocess
import sys
import openpyxl # .xlsx 파일 처리를 위해 추가
import unicodedata

# ─────────────────────────────────────────────
# set_page_config는 반드시 맨 위에서 한 번만 호출
st.set_page_config(page_title="에덴 룰렛 런처", layout="centered")

# ─────────────────────────────────────────────
# 1) 매핑 테이블 정의
# ─────────────────────────────────────────────
skillType_map = {
    "Skill_Type_8_0.png": "무",
    "Skill_Type_8_1.png": "불",
    "Skill_Type_8_2.png": "땅",
    "Skill_Type_8_4.png": "물",
    "Skill_Type_8_8.png": "바람",
    "Skill_Type_8_16.png": "뇌",
    "Skill_Type_8_32.png": "그림자",
    "Skill_Type_8_64.png": "수정",
}
weapon_map = {
    "202000000_icon.png": "지팡이",
    "202000001_icon.png": "검",
    "202000002_icon.png": "도", # 예시 데이터에는 없었지만, 일반적인 무기 유형 추가
    "202000003_icon.png": "도끼",
    "202000004_icon.png": "창",
    "202000005_icon.png": "활",
    "202000006_icon.png": "주먹", # 예시 데이터에는 없었지만, 일반적인 무기 유형 추가
    "202000007_icon.png": "망치",
}
armor_map = {
    "216000002_icon.png": "팔찌",
    "216000003_icon.png": "목걸이",
    "216000004_icon.png": "반지",
}

ICON_DIR = os.path.join("character_art", "icons")
EQUIP_DIR = os.path.join("character_art", "elements_equipment")

BUDDY_PATTERN = re.compile(r"Buddy[_ ]equipment\.png", re.IGNORECASE)

# ─────────────────────────────────────────────
# 0) 컬럼명 자동 감지 함수 (Excel용으로 확장)
# ─────────────────────────────────────────────
def pick_col(df, candidates, exact_match=False):
    for c_candidate in candidates:
        if exact_match:
            if c_candidate in df.columns:
                return c_candidate
        else:
            # 부분 문자열 일치 (대소문자, 공백 무시)
            for col in df.columns:
                if str(c_candidate).lower().replace(" ","") in str(col).lower().replace(" ",""):
                    return col
    return None

def clean_html_tags(text):
    if not isinstance(text, str):
        return text
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

# ─────────────────────────────────────────────
# 2) 코어 로직 (Excel 직접 파싱)
# ─────────────────────────────────────────────
def structure_analysis_excel(df, out_csv="structure_analysis_summary.csv"):
    summary = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        samples = df[col].dropna().unique()[:5]
        summary.append({
            "ColumnName": col,
            "DataType": dtype,
            "ExampleValues": ", ".join(map(str, samples))
        })
    pd.DataFrame(summary).to_csv(out_csv, index=False, encoding="utf-8-sig")
    return out_csv

def clean_path_list(lst):
    return [p for p in lst if p and isinstance(p, str) and p.strip() and (not (isinstance(p, float) and math.isnan(p)))]

def find_image(filename, subdir, character_name=None):
    if not filename or not isinstance(filename, str):
        return ''
    # 유니코드 정규화 및 공백/언더스코어 처리
    norm = unicodedata.normalize('NFKC', filename).strip().replace(' ', '_').lower()
    dir_path = subdir
    # 1. 완전일치
    full_path = os.path.join(dir_path, norm)
    if os.path.exists(full_path):
        return full_path.replace("\\", "/")

    # 1-1. 캐시 사전 이용 (대소문자 무시)
    cache_attr = f"_cache_{dir_path}"
    if not hasattr(find_image, cache_attr):
         cache_dict = {f.lower(): f for f in os.listdir(dir_path)}
         setattr(find_image, cache_attr, cache_dict)
    cache = getattr(find_image, cache_attr)
    if norm in cache:
         return os.path.join(dir_path, cache[norm]).replace("\\", "/")
    # 2. 확장자 무시하고 찾기
    base, ext = os.path.splitext(norm)
    if not ext: # 확장자가 없으면 .png 추가 시도
        full_path_png = os.path.join(dir_path, base + ".png")
        if os.path.exists(full_path_png):
            return full_path_png.replace("\\", "/")

    for f in os.listdir(dir_path):
        f_lower = f.lower()
        fbase, fext = os.path.splitext(f_lower)
        if fbase == base: # 확장자 다른 경우 포함
            return os.path.join(dir_path, f).replace("\\", "/")
        # 아이콘 파일명에 _rank5_command 등이 붙는 경우, 앞부분만 일치하는지 확인
        if norm.startswith(fbase) or fbase.startswith(base):
             # 101050211_rank5_command.png 와 101050211.png 매칭
            if base.split('_')[0] == fbase.split('_')[0]:
                return os.path.join(dir_path, f).replace("\\", "/")

    # 3. 공백/언더스코어/대소문자 무시 fuzzy match
    norm_fuzzy = norm.replace('_','').replace(' ','')
    for f in os.listdir(dir_path):
        f_fuzzy = f.lower().replace('_','').replace(' ','')
        if f_fuzzy == norm_fuzzy:
            return os.path.join(dir_path, f).replace("\\", "/")
        fbase_fuzzy, _ = os.path.splitext(f_fuzzy)
        if fbase_fuzzy == norm_fuzzy: # 확장자 없는 fuzzy match
             return os.path.join(dir_path, f).replace("\\", "/")

    if character_name:
        st.warning(f"[이미지 없음] 파일: {filename} (캐릭터: {character_name}) [경로: {dir_path}]")
    return ''


def make_structure_analysis_from_excel(src_excel="another_eden_characters_detailed.xlsx"):
    try:
        df = pd.read_excel(src_excel, engine='openpyxl')
    except FileNotFoundError:
        st.error(f"입력 파일 없음: {src_excel}. 런처와 동일한 폴더에 위치시켜주세요.")
        return None
    out_csv = structure_analysis_excel(df, out_csv="structure_analysis_excel_summary.csv")
    return out_csv

def make_cleaned_excel_from_excel(src_excel="another_eden_characters_detailed.xlsx"):
    try:
        df = pd.read_excel(src_excel, engine='openpyxl')
    except FileNotFoundError:
        st.error(f"입력 파일 없음: {src_excel}. 런처와 동일한 폴더에 위치시켜주세요.")
        return None
        
    # Buddy equipment.png를 포함하는 행 제외
    # Elem/Equip 컬럼들에서 "Buddy equipment.png" 문자열 확인
    buddy_check_cols = [pick_col(df, [f"Elem/Equip {i} Alt"]) for i in range(1, 6)]
    buddy_check_cols = [c for c in buddy_check_cols if c] # None 제거

    def is_buddy_row(row):
        for col_name in buddy_check_cols:
            val = str(row.get(col_name, ""))
            if BUDDY_PATTERN.search(val):
                return True
        return False

    if buddy_check_cols: # buddy_check_cols가 하나라도 있어야 필터링 의미 있음
        df_clean = df[~df.apply(is_buddy_row, axis=1)].reset_index(drop=True)
    else: # Elem/Equip Alt 컬럼이 없으면 원본 그대로 사용 (경고)
        st.warning("Buddy 장비 필터링을 위한 'Elem/Equip * Alt' 컬럼을 찾지 못했습니다. 전체 데이터가 사용됩니다.")
        df_clean = df.copy()

    out_xlsx = "another_eden_characters_cleaned_from_excel.xlsx"
    df_clean.to_excel(out_xlsx, index=False)
    return out_xlsx


def find_best_match_and_translate(english_name, name_map):
    """
    영문 캐릭터 이름을 받아 최적의 한글 이름으로 변환합니다.
    1. 이름 전체가 매칭 테이블에 있는지 먼저 확인합니다.
    2. 없다면, 'AS', 'ES' 등의 접미사를 분리하여 기본 이름으로 매칭을 시도합니다.
    3. 매칭된 한글 이름에 표준화된 접미사('AS' 또는 'ES')를 붙여 반환합니다.
    4. 어떤 경우에도 매칭되지 않으면 원본 영문 이름을 그대로 반환합니다.
    """
    # 1순위: 이름 전체가 매칭되는지 확인 (가장 정확)
    # 예: 'Black Clad Sw.' -> '검은 옷의 칼잡이'
    if english_name in name_map:
        return name_map[english_name]

    # 2순위: 접미사를 분리하여 기본 이름으로 매칭 시도
    base_name = english_name
    suffix_to_append = ""

    # 접미사를 확인하고, 표준 접미사(' AS' 또는 ' ES')를 결정합니다.
    if english_name.endswith(" (Another Style)"):
        base_name = english_name[:-16].strip()
        suffix_to_append = " AS"
    elif english_name.endswith(" (Extra Style)"):
        base_name = english_name[:-14].strip()
        suffix_to_append = " ES"
    elif english_name.endswith(" AS"):
        base_name = english_name[:-3].strip()
        suffix_to_append = " AS"
    elif english_name.endswith(" ES"):
        base_name = english_name[:-3].strip()
        suffix_to_append = " ES"

    # 분리된 기본 이름(base_name)이 매칭 테이블에 있는지 확인
    if base_name in name_map:
        # 매칭이 되면, 한글 이름 + 표준 접미사를 조합하여 반환
        # 예: 'Gariyu' -> '가리유' + ' AS' -> '가리유 AS'
        return name_map[base_name] + suffix_to_append

    # 3순위: 어떤 규칙으로도 매칭되지 않으면 원본 이름 반환
    return english_name


def make_roulette_csv_from_excel(src_excel="another_eden_characters_detailed.xlsx"):
    try:
        df = pd.read_excel(src_excel, engine='openpyxl')
    except FileNotFoundError:
        st.error(f"입력 파일 없음: {src_excel}. 런처와 동일한 폴더에 위치시켜주세요.")
        return None

    # 이름 매칭용 CSV 파일을 읽고, 변환 규칙(딕셔너리)을 생성합니다.
    try:
        name_map_df = pd.read_csv("Matching_names.csv")
        name_map = dict(zip(name_map_df["캐릭터명 (입력)"], name_map_df["캐릭터명 (매칭)"]))
    except FileNotFoundError:
        st.warning("이름 매칭 파일(Matching_names.csv)을 찾을 수 없습니다. 캐릭터명이 영문으로 표시됩니다.")
        name_map = {}
    except Exception as e:
        st.error(f"이름 매칭 파일(Matching_names.csv) 로드 중 오류 발생: {e}")
        return None

    # Buddy equipment.png 행 제외
    buddy_check_cols = [pick_col(df, [f"Elem/Equip {i} Alt"]) for i in range(1, 6)]
    buddy_check_cols = [c for c in buddy_check_cols if c]

    def is_buddy_row(row):
        for col_name in buddy_check_cols:
            val = str(row.get(col_name, ""))
            if BUDDY_PATTERN.search(val):
                return True
        return False
    
    if buddy_check_cols:
        df_clean = df[~df.apply(is_buddy_row, axis=1)].reset_index(drop=True)
    else:
        st.warning("Buddy 장비 필터링을 위한 'Elem/Equip * Alt' 컬럼을 찾지 못했습니다. 전체 데이터가 사용됩니다.")
        df_clean = df.copy()

    col_icon_filename = pick_col(df_clean, ["Icon Filename", "Icon", "아이콘 파일명"], exact_match=True)
    col_name = pick_col(df_clean, ["Name", "이름"], exact_match=True)
    col_rarity = pick_col(df_clean, ["Rarity", "희귀도"], exact_match=True)
    col_release = pick_col(df_clean, ["Release Date", "출시일"], exact_match=True)

    if not all([col_icon_filename, col_name, col_rarity, col_release]):
        missing_cols = [c_name for c_name, c_val in zip(
            ["아이콘 파일명", "이름", "희귀도", "출시일"],
            [col_icon_filename, col_name, col_rarity, col_release]) if not c_val]
        st.error(f"필수 컬럼 누락: {', '.join(missing_cols)}. Excel 파일을 확인해주세요.")
        return None

    result = []
    for idx, row in df_clean.iterrows():
        # 영문 이름을 가져옵니다.
        name = str(row.get(col_name, "")).strip()
        
        # ✨ 새로 만든 함수를 호출하여 최적의 한글 이름을 찾습니다. ✨
        korean_name = find_best_match_and_translate(name, name_map)
        
        icon_file = str(row.get(col_icon_filename, "")).strip().replace(" ", "_")
        rarity_raw = str(row.get(col_rarity, "")).strip()
        rarity = clean_html_tags(rarity_raw)
        
        release_raw = str(row.get(col_release, "")).strip()
        release = clean_html_tags(release_raw)

        icon_path = find_image(icon_file, ICON_DIR, name)
        if not icon_path and icon_file:
            st.warning(f"[캐릭터 아이콘 없음] 파일: {icon_file} (캐릭터: {name})")

        attr_names, attr_paths = [], []
        weapon_names, weapon_paths = [], []
        armor_names, armor_paths = [], []

        elem_equip_cols = []
        for i in range(1, 6):
            ecol = pick_col(df_clean, [f"Elem/Equip {i} Alt", f"Elem/Equip{i}Alt"], exact_match=False)
            if ecol:
                elem_equip_cols.append(str(row.get(ecol, "")).strip())
        
        valid_equip_files = [e for e in elem_equip_cols if e and isinstance(e, str) and e.endswith(".png")]

        for val in valid_equip_files:
            val_norm = val.strip().replace(" ", "_")
            if val_norm in skillType_map:
                attr_names.append(skillType_map[val_norm])
                attr_paths.append(find_image(val_norm, EQUIP_DIR, name))
            elif val_norm in weapon_map:
                weapon_names.append(weapon_map[val_norm])
                weapon_paths.append(find_image(val_norm, EQUIP_DIR, name))
            elif val_norm in armor_map:
                armor_names.append(armor_map[val_norm])
                armor_paths.append(find_image(val_norm, EQUIP_DIR, name))

        result.append({
            "캐릭터명": korean_name, # 변환된 한글 이름을 사용합니다.
            "희귀도": rarity,
            "캐릭터아이콘경로": icon_path or "",
            "속성명리스트": ",".join(attr_names),
            "속성_아이콘경로리스트": ",".join(clean_path_list(attr_paths)),
            "무기명리스트": ",".join(weapon_names),
            "무기_아이콘경로리스트": ",".join(clean_path_list(weapon_paths)),
            "방어구명리스트": ",".join(armor_names),
            "방어구_아이콘경로리스트": ",".join(clean_path_list(armor_paths)),
            "출시일": release,
        })
        
    re_df = pd.DataFrame(result)
    out_csv = "eden_roulette_data.csv"
    re_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return out_csv
# ─────────────────────────────────────────────
# 런처 첫 화면
# ─────────────────────────────────────────────
st.title("🌱 Another Eden 데이터/룰렛 런처")

st.markdown("""
- **데이터 전처리(GUI)**: `another_eden_characters_detailed.xlsx`에서 직접 데이터를 읽어 캐릭터/이미지 정합성 체크, 구조분석, 앱용 CSV 등을 생성합니다.
- **룰렛/사용자용 앱**: 캐릭터 뽑기/검색/필터 Streamlit 앱 실행 (위 전처리로 생성된 `eden_roulette_data_from_excel.csv` 사용 권장)
""")

# 입력 파일 선택 옵션 추가 (기본은 Excel)
# input_file_option = st.selectbox(
# "기준 입력 파일을 선택하세요:",
# ("another_eden_characters_detailed.xlsx", "structure_analysis.csv")
# )
# st.caption(f"선택된 입력 파일: {input_file_option}")


mode = st.radio("실행할 앱을 선택하세요:", ["데이터 전처리(GUI)", "룰렛/사용자용 앱"], index=0)

if mode == "룰렛/사용자용 앱":
    st.info("룰렛/사용자용 앱을 실행합니다. 아래 명령어를 복사해 터미널에 붙여넣으세요:")
    st.code("streamlit run streamlit_eden_restructure.py", language="bash")
    
    # 사용자 편의를 위해 클립보드 복사 기능 추가 (streamlit-nightly 필요 또는 JavaScript 사용)
    # if st.button("명령어 복사"):
    # import pyperclip # pyperclip은 로컬에 설치되어 있어야 함
    # try:
    # pyperclip.copy("streamlit run streamlit_eden_restructure.py")
    # st.success("명령어가 클립보드에 복사되었습니다!")
    # except Exception as e:
    # st.warning(f"클립보드 복사 실패: {e}. 직접 복사해주세요.")
    st.stop()

# ─────────────────────────────────────────────
# 데이터 전처리(GUI)만 아래에 표시
# ─────────────────────────────────────────────
st.header("에덴 룰렛 데이터 전처리 (Excel 기반)") # 제목 변경
st.markdown(f"""
- 원하는 산출물만 체크해서 생성할 수 있습니다.
- **기준 입력 파일**: `another_eden_characters_detailed.xlsx` (런처와 동일 폴더에 위치해야 함)
- 생성된 파일은 작업 폴더에 저장되며, 다운로드 링크가 제공됩니다.
""")

st.subheader("1. 생성할 산출물 선택") # subheader로 변경
do_structure = st.checkbox("Excel 구조분석 파일 (structure_analysis_excel_summary.csv)", value=True)
do_cleaned = st.checkbox("Excel 정제본 (another_eden_characters_cleaned_from_excel.xlsx)", value=True)
do_roulette = st.checkbox("룰렛/앱용 CSV (eden_roulette_data.csv)", value=True)

if st.button("선택한 작업 실행"):
    with st.spinner("작업 실행 중... (Excel 파일 크기에 따라 시간이 소요될 수 있습니다)"):
        if do_structure:
            try:
                out1 = make_structure_analysis_from_excel()
                if out1:
                    st.success(f"Excel 구조분석 파일 생성 완료: {out1}")
                    with open(out1, "rb") as f:
                        st.download_button("구조분석 파일 다운로드", f, file_name=out1, mime="text/csv")
            except Exception as e:
                st.error(f"Excel 구조분석 파일 생성 실패: {e}")
        if do_cleaned:
            try:
                out2 = make_cleaned_excel_from_excel()
                if out2:
                    st.success(f"Excel 정제본 생성 완료: {out2}")
                    with open(out2, "rb") as f:
                        st.download_button("정제본 Excel 다운로드", f, file_name=out2, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Excel 정제본 생성 실패: {e}")
        if do_roulette:
            try:
                out3 = make_roulette_csv_from_excel()
                if out3:
                    st.success(f"룰렛/앱용 CSV 생성 완료: {out3}")
                    with open(out3, "rb") as f:
                        st.download_button("룰렛/앱용 CSV 다운로드", f, file_name=out3, mime="text/csv")
            except Exception as e:
                st.error(f"룰렛/앱용 CSV 생성 실패: {e}")
    st.info("작업이 모두 완료되었습니다.") 