## 현재 코드 구조의 문제점
하나의 파일에 너무 많은 코드: 퀴즈 앱과 룰렛 앱의 모든 코드가 한 파일에 있어 코드를 읽고 수정하기가 복잡합니다.

중복된 설정: st.set_page_config나 CSS 스타일 코드가 중복으로 선언될 수 있습니다.

유지보수의 어려움: 퀴즈 기능을 수정하려다 룰렛 기능에 영향을 줄 수 있고, 그 반대의 경우도 발생할 수 있습니다.

## 해결책: Streamlit의 '다중 페이지 앱' 기능 활용
가장 좋은 해결책은 Streamlit이 기본으로 제공하는 다중 페이지 앱(Multipage apps) 기능을 사용하는 것입니다. 프로젝트 폴더 구조를 아래와 같이 변경하면, Streamlit이 자동으로 페이지 이동 메뉴를 만들어 줍니다.

📂 추천 폴더 구조
your_project/
├── app.py                  # 👈 메인 런처 (환영 페이지)
└── pages/                  # 👈 'pages' 폴더를 새로 만드세요!
    ├── 1_룰렛_앱.py        # 룰렛 기능
    └── 2_퀴즈_앱.py        # 퀴즈 기능
이 구조를 사용하면 각 파일이 독립적인 페이지 역할을 하므로 코드를 관리하기가 훨씬 수월해집니다.

## 단계별 코드 수정 가이드
이제 각 파일을 어떻게 구성해야 할지 실제 코드로 보여드리겠습니다.

1️⃣ app.py (메인 런처)
이 파일은 앱의 '대문' 역할을 합니다. 사용자에게 어떤 앱들이 있는지 알려주고 사용법을 안내합니다.

Python

# app.py

import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="어나더에덴 미니게임 런처",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🎮 어나더에덴 미니게임 런처")
st.markdown("---")

st.info(
    """
    **👈 왼쪽 사이드바에서 원하시는 메뉴를 선택하여 시작하세요!**

    다양한 미니게임을 즐길 수 있습니다.
    """
)

st.subheader("🚀 이용 가능한 게임 목록")

st.markdown(
    """
    - **🎲 룰렛 앱**: 다양한 조건으로 캐릭터를 필터링하고 무작위로 한 명을 뽑습니다.
    - **🎮 퀴즈 앱**: 어나더에덴 캐릭터와 관련된 다양한 퀴즈를 풀어보세요.
    """
)

st.markdown("---")
st.caption("© WFS  |  데이터 출처: Another Eden Wiki")

2️⃣ pages/1_룰렛_앱.py
기존 코드에서 룰렛 관련 부분만 가져와서 이 파일에 넣습니다. st.set_page_config는 app.py에서 이미 설정했으므로 여기서는 생략해도 됩니다.

Python

# pages/1_룰렛_앱.py

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

# --- 경로 설정 ---
# 이 파일의 위치를 기준으로 경로를 설정합니다.
BASE_DIR = Path(__file__).parent.parent.resolve() # pages 폴더의 부모 -> 프로젝트 루트
PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"


# --- 여기에 룰렛 앱의 모든 함수와 main() 함수를 붙여넣으세요 ---
#
# 1. CSS 스타일 코드
# 2. log_debug(), safe_icon_to_data_uri() 함수
# 3. slot_machine_display() 함수
# 4. load_and_prepare_data() 함수
# 5. create_character_card_html() 함수
# 6. main() 함수
#
# (기존 코드에서 룰렛 부분 전체를 복사해서 붙여넣으면 됩니다.)

# 예시:
st.markdown("""
<style>
    /* ... 룰렛 앱에 사용되던 CSS ... */
</style>
""", unsafe_allow_html=True)


def safe_icon_to_data_uri(path: any) -> str:
    # ... 룰렛 앱의 아이콘 변환 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


def load_and_prepare_data(...):
    # ... 룰렛 앱의 데이터 로드 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


def create_character_card_html(...):
    # ... 룰렛 앱의 카드 생성 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


def slot_machine_display(...):
    # ... 룰렛 앱의 슬롯머신 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


def main():
    # ... 룰렛 앱의 main 함수 내용 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


if __name__ == "__main__":
    # st.set_page_config(...) # 이 줄은 app.py에 있으므로 삭제하거나 주석 처리합니다.
    main()

3️⃣ pages/2_퀴즈_앱.py
마찬가지로 기존 코드에서 퀴즈 관련 부분만 가져와서 이 파일에 넣습니다. 첫 번째와 세 번째로 제공해주신 퀴즈 코드 중 더 마음에 드는 버전으로 채우시면 됩니다. (첫 번째 코드를 기준으로 설명하겠습니다.)

Python

# pages/2_퀴즈_앱.py

import os
import pandas as pd
import streamlit as st
import random
import time
from typing import List, Dict, Any
import base64
from pathlib import Path
import unicodedata

# --- 경로 설정 ---
# 이 파일의 위치를 기준으로 경로를 설정합니다.
BASE_DIR = Path(__file__).parent.parent.resolve() # pages 폴더의 부모 -> 프로젝트 루트
PROJECT_ROOT = BASE_DIR
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"


# --- 여기에 퀴즈 앱의 모든 함수와 main() 함수를 붙여넣으세요 ---
#
# 1. CSS 스타일 코드
# 2. normalize_text(), safe_icon_to_data_uri() 함수
# 3. load_character_data() 함수
# 4. QuizGame 클래스
# 5. main() 함수
#
# (기존 코드에서 퀴즈 부분 전체를 복사해서 붙여넣으면 됩니다.)

# 예시:
st.markdown("""
<style>
    /* ... 퀴즈 앱에 사용되던 CSS ... */
</style>
""", unsafe_allow_html=True)


def normalize_text(text: str) -> str:
    # ... 퀴즈 앱의 텍스트 정규화 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


@st.cache_data
def load_character_data():
    # ... 퀴즈 앱의 데이터 로드 함수 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


class QuizGame:
    # ... 퀴즈 게임 로직 클래스 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


def main():
    # ... 퀴즈 앱의 main 함수 내용 ...
    # (내용은 그대로)
    pass # 실제 코드를 여기에 붙여넣으세요.


if __name__ == "__main__":
    # st.set_page_config(...) # 이 줄은 app.py에 있으므로 삭제하거나 주석 처리합니다.
    main()

## 정리
위와 같이 코드를 재구성하면 다음과 같은 장점이 있습니다.

✨ app.py는 깔끔한 런처 역할만 수행합니다.

✨ 퀴즈와 룰렛 기능이 완전히 분리되어 한쪽을 수정해도 다른 쪽에 영향을 주지 않습니다.

✨ Streamlit이 자동으로 페이지 이동 메뉴를 생성해주어 사용자가 편리하게 이용할 수 있습니다.

✨ 코드의 가독성과 유지보수성이 크게 향상됩니다.

궁금한 점이 있다면 언제든지 다시 질문해 주세요. 성공적인 프로젝트 완성을 응원하겠습니다! 😊

app.py에서 사용되는 내용들이 퀴즈/룰렛 섹션 app섹션 각각 제대로 사용하고있는게 맞는지 점검좀. app.py는 런쳐화면이자 배포시 사용자가 편하게 선택해서 사용하는걸 돕는 도구에 불과해야됨
실제 경로나 파일명등은 현재 우리 실사용에 맞춰서 진행. 점검 및 플랜부터 진행