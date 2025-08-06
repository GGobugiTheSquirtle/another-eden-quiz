#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 공통 UI 컴포넌트 라이브러리
앱 간 일관성을 위한 공통 UI 요소들
"""

import streamlit as st
from pathlib import Path

def load_common_css():
    """공통 CSS 스타일 로드"""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        .stApp {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        /* 브라우저 확장 프로그램 충돌 방지 */
        iframe {
            pointer-events: none !important;
        }
        
        /* contentScript 충돌 방지 */
        div[data-testid="stApp"] {
            isolation: isolate;
        }
        
        /* 공통 그라데이션 배경 */
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            margin: 1rem 0;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        /* 카드 스타일 */
        .card {
            background: rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        /* 버튼 스타일 개선 */
        .stButton > button {
            border-radius: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        }
        
        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .gradient-bg {
                padding: 1rem;
                font-size: 0.9rem;
            }
            
            .card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
        }
        
        /* 통일된 색상 팔레트 */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #FFD700;
            --success-color: #4CAF50;
            --error-color: #f44336;
            --warning-color: #ff9800;
        }
        
        /* 애니메이션 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* 데이터 표시용 테이블 스타일 */
        .data-table {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .data-table th {
            background: var(--primary-color);
            color: white;
            padding: 1rem;
            text-align: left;
        }
        
        .data-table td {
            padding: 0.8rem 1rem;
            border-bottom: 1px solid #eee;
        }
        
        .data-table tr:hover {
            background: #f5f5f5;
        }
        
        /* 상태 메시지 */
        .status-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .status-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
    </style>
    """

def render_header(title: str, subtitle: str = "", icon: str = "🎮"):
    """공통 헤더 렌더링"""
    st.markdown(f"""
    <div class="gradient-bg fade-in-up">
        <h1 style="margin: 0; color: #FFD700; font-size: 2.5rem;">{icon} {title}</h1>
        {f'<p style="margin: 1rem 0; font-size: 1.2rem; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_card(content: str, title: str = "", card_type: str = "default"):
    """카드 컴포넌트 렌더링"""
    card_class = f"card {card_type}-card" if card_type != "default" else "card"
    
    st.markdown(f"""
    <div class="{card_class} fade-in-up">
        {f'<h3 style="margin: 0 0 1rem 0; color: #333;">{title}</h3>' if title else ''}
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_status_message(message: str, message_type: str = "info"):
    """상태 메시지 렌더링"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(message_type, "ℹ️")
    
    st.markdown(f"""
    <div class="status-message status-{message_type}">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)

def render_progress_bar(current: int, total: int, label: str = "진행률"):
    """진행률 표시"""
    progress = current / max(total, 1)
    percentage = progress * 100
    
    st.markdown(f"""
    <div class="card">
        <h4 style="margin: 0 0 1rem 0;">{label}: {current}/{total} ({percentage:.1f}%)</h4>
        <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); 
                        width: {percentage}%; height: 100%; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_statistics(stats: dict):
    """통계 정보 렌더링"""
    cols = st.columns(len(stats))
    
    for i, (label, value) in enumerate(stats.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align: center;">
                <h2 style="margin: 0; color: var(--primary-color);">{value}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #666;">{label}</p>
            </div>
            """, unsafe_allow_html=True)

def render_feature_grid(features: list):
    """기능 소개 그리드"""
    cols = st.columns(min(len(features), 3))
    
    for i, feature in enumerate(features):
        col_idx = i % len(cols)
        with cols[col_idx]:
            icon = feature.get('icon', '🔹')
            title = feature.get('title', '')
            description = feature.get('description', '')
            items = feature.get('items', [])
            
            items_html = ""
            if items:
                items_html = "<ul style='text-align: left; margin: 0.5rem 0;'>"
                for item in items:
                    items_html += f"<li style='margin: 0.3rem 0;'>{item}</li>"
                items_html += "</ul>"
            
            st.markdown(f"""
            <div class="card" style="height: 100%;">
                <h3 style="margin: 0; color: var(--accent-color);">{icon} {title}</h3>
                <p style="margin: 0.5rem 0;">{description}</p>
                {items_html}
            </div>
            """, unsafe_allow_html=True)

def render_data_summary(data_info: dict):
    """데이터 요약 정보"""
    st.markdown(f"""
    <div class="card">
        <h3 style="margin: 0 0 1rem 0; color: var(--primary-color);">📊 데이터 현황</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            {''.join([f'''
            <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.5); border-radius: 10px;">
                <h4 style="margin: 0; color: var(--secondary-color);">{value}</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{key}</p>
            </div>
            ''' for key, value in data_info.items()])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """공통 푸터"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 1rem 0;">
        <p>데이터 출처: <a href="https://anothereden.wiki/w/Another_Eden_Wiki" target="_blank">Another Eden Wiki</a></p>
        <p>모든 캐릭터 이미지의 저작권은 © WFS에 있습니다.</p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">🎮 Another Eden 퀴즈 & 룰렛 앱 v2.0</p>
    </div>
    """, unsafe_allow_html=True)

def apply_common_styles():
    """공통 스타일 적용"""
    st.markdown(load_common_css(), unsafe_allow_html=True)