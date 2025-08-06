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