#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[ARCHIVED] 향상된 Another Eden 캐릭터 스크래퍼
이 스크래퍼는 더 이상 사용되지 않으며, master_scraper.py로 통합되었습니다.
- 한글 매칭 이름 기반 이미지 저장
- 스타일 접미사 처리
- 통합 데이터 생성
"""

import os
import sys
import pandas as pd
import requests
import re
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup

# 경로 설정
BASE_DIR = Path(__file__).parent.resolve()
IMAGE_DIR = BASE_DIR / "character_art"
MATCHING_CSV = BASE_DIR / "Matching_names.csv"
OUTPUT_CSV = BASE_DIR / "eden_quiz_data.csv"

# 디렉토리 생성
IMAGE_DIR.mkdir(exist_ok=True)

# 한글 매핑 로드
def load_korean_mapping():
    """Matching_names.csv에서 한글 매핑 로드"""
    mapping = {}
    if not MATCHING_CSV.exists():
        print(f"[WARN] {MATCHING_CSV} 없음, 영어명만 사용")
        return mapping
    
    try:
        df = pd.read_csv(MATCHING_CSV, encoding='utf-8-sig')
        for _, row in df.iterrows():
            eng = str(row.iloc[0]).strip()
            kor = str(row.iloc[1]).strip()
            if eng and kor and kor != 'nan':
                mapping[eng.lower()] = kor
    except Exception as e:
        print(f"[ERROR] 매핑 파일 읽기 실패: {e}")
    
    return mapping

# 스타일 접미사 처리
def extract_style_suffix(name):
    """AS/ES/NS 등 스타일 접미사 분리"""
    style_patterns = [
        r'\s+(AS)$', r'\s+(ES)$', r'\s+(NS)$',
        r'\s+(Another\s*Style)$', r'\s+(Extra\s*Style)$',
        r'\s+(Manifestation)$', r'\s+(Alter)$',
    ]
    base_name = name
    style_suffix = ""
    
    for pattern in style_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            style_suffix = " " + match.group(1)
            base_name = name[:match.start()]
            break
    return base_name, style_suffix

# 파일명 안전화
def sanitize_filename(name):
    """파일명으로 안전하게 변환"""
    name = unicodedata.normalize('NFKC', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip()
    return name

# 캐릭터 데이터 스크래핑
def scrape_characters():
    """Another Eden Wiki에서 캐릭터 데이터 스크래핑"""
    print("캐릭터 데이터 스크래핑 시작...")
    print("=" * 50)
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매칭 로드: {len(korean_mapping)}개")
    
    # Wiki URL
    url = "https://anothereden.miraheze.org/wiki/Category:%EC%BA%90%EB%A6%AD%ED%84%B0_%EC%95%84%EC%9D%B4%EC%BD%98"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"[ERROR] Wiki 페이지 접근 실패: {e}")
        return []
    
    # 캐릭터 링크 추출
    character_links = []
    gallery_div = soup.find('div', class_='gallery')
    if gallery_div:
        for link in gallery_div.find_all('a', href=True):
            if '/wiki/' in link['href'] and 'File:' not in link['href']:
                full_url = f"https://anothereden.miraheze.org{link['href']}"
                title = link.get('title', '').replace('File:', '')
                character_links.append((full_url, title))
    
    print(f"발견된 캐릭터 수: {len(character_links)}개")
    
    # 캐릭터 데이터 수집
    characters = []
    for i, (char_url, title) in enumerate(character_links[:50]):  # 테스트용 50개만
        try:
            print(f"[{i+1}/{len(character_links[:50])}] {title} 처리 중...")
            char_response = requests.get(char_url)
            char_response.raise_for_status()
            char_soup = BeautifulSoup(char_response.content, 'html.parser')
            
            # 기본 정보 추출
            name = title.replace('_Category', '').strip()
            base_name, style_suffix = extract_style_suffix(name)
            korean_name = korean_mapping.get(base_name.lower(), base_name) + style_suffix
            
            # 이미지 URL 추출
            img_url = None
            img_tag = char_soup.find('img', alt=lambda x: x and name in x)
            if img_tag and img_tag.get('src'):
                img_url = img_tag['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
            
            # 이미지 다운로드 및 저장
            image_path = ""
            if img_url:
                try:
                    img_response = requests.get(img_url, timeout=10)
                    img_response.raise_for_status()
                    
                    # 파일명 생성
                    filename = sanitize_filename(korean_name) + ".png"
                    image_path = str(IMAGE_DIR / filename)
                    
                    # 파일 저장
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"  [OK] 이미지 저장: {filename}")
                except Exception as e:
                    print(f"  [ERROR] 이미지 저장 실패: {e}")
                    image_path = ""
            
            # 캐릭터 데이터 추가
            characters.append({
                '캐릭터명': korean_name,
                '영문명': name,
                '캐릭터아이콘경로': image_path,
                '희귀도': '',
                '속성명리스트': '',
                '무기명리스트': '',
                '성격특성리스트': ''
            })
            
        except Exception as e:
            print(f"  [ERROR] {title} 처리 실패: {e}")
            continue
    
    return characters

# 통합 데이터 생성
def create_integrated_data():
    """통합 데이터 생성 및 저장"""
    characters = scrape_characters()
    
    if not characters:
        print("[ERROR] 캐릭터 데이터 없음")
        return False
    
    # 데이터프레임 생성 및 저장
    df = pd.DataFrame(characters)
    try:
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"\n통합 데이터 저장 완료: {OUTPUT_CSV}")
        print(f"총 {len(df)}개 캐릭터 데이터 저장")
        return True
    except Exception as e:
        print(f"[ERROR] 데이터 저장 실패: {e}")
        return False

if __name__ == "__main__":
    success = create_integrated_data()
    sys.exit(0 if success else 1)
