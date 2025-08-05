#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[ARCHIVED] Another Eden 이미지 재스크레이핑 및 한글명 기반 저장 스크립트
이 스크래퍼는 더 이상 사용되지 않으며, master_scraper.py로 통합되었습니다.
- 기존 scraper를 기반으로 한글 matching names 기준으로 이미지 저장
- 매칭 안 되는 경우 영어명으로 저장
"""

import os
import sys
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, parse_qs, urlparse
import unicodedata
import re
import time
from pathlib import Path
import mimetypes

BASE_URL = "https://anothereden.wiki"
TARGET_URL = "https://anothereden.wiki/w/Characters"
IMAGE_DIR = "character_art"

# 한글 매핑 로드
def load_korean_mapping():
    """Matching_names.csv에서 한글 매핑 로드"""
    mapping = {}
    csv_path = "Matching_names.csv"
    if not os.path.exists(csv_path):
        print(f"[WARN] {csv_path} 없음, 영어명만 사용")
        return mapping
    
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    for _, row in df.iterrows():
        eng = str(row.iloc[0]).strip()
        kor = str(row.iloc[1]).strip()
        if eng and kor and kor != 'nan':
            mapping[eng] = kor
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

# 한글명 변환
def convert_to_korean_name(eng_name, mapping):
    """영어 캐릭터명을 한글로 변환"""
    if not eng_name:
        return eng_name
    
    base_name, style_suffix = extract_style_suffix(eng_name)
    korean_base = mapping.get(base_name, base_name)
    return korean_base + style_suffix

# 파일명 안전화
def sanitize_filename(name):
    """파일명으로 안전하게 변환"""
    name = unicodedata.normalize('NFKC', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = name.strip()
    return name

# 이미지 다운로드
def download_image(url, save_path):
    """이미지 다운로드 및 저장"""
    if not url:
        return False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"[ERROR] 다운로드 실패 {url}: {e}")
        return False

# 캐릭터 목록 스크레이핑
def scrape_character_list():
    """캐릭터 목록 페이지에서 데이터 추출"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 테이블 찾기
        tables = soup.find_all('table', class_='wikitable')
        if not tables:
            print("[ERROR] 캐릭터 테이블을 찾을 수 없습니다")
            return []
        
        characters = []
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2:
                    continue
                
                # 캐릭터 링크 및 이름 추출
                char_link = cols[0].find('a')
                if not char_link:
                    continue
                
                eng_name = char_link.get('title', '').strip()
                href = char_link.get('href', '')
                detail_url = urljoin(BASE_URL, href)
                
                # 이미지 URL 추출
                img_tag = char_link.find('img')
                img_url = None
                if img_tag:
                    img_src = img_tag.get('src', '')
                    if img_src.startswith('http'):
                        img_url = img_src
                    else:
                        img_url = urljoin(BASE_URL, img_src)
                
                characters.append({
                    'english_name': eng_name,
                    'detail_url': detail_url,
                    'image_url': img_url
                })
        
        return characters
        
    except Exception as e:
        print(f"[ERROR] 스크레이핑 실패: {e}")
        return []

# 캐릭터 상세 페이지에서 이미지 추출
def scrape_character_images(detail_url, eng_name):
    """상세 페이지에서 고화질 이미지 URL 추출"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(detail_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # infobox에서 이미지 찾기
        infobox = soup.find('table', class_='infobox')
        if infobox:
            img_tag = infobox.find('img')
            if img_tag:
                img_src = img_tag.get('src', '')
                if img_src.startswith('http'):
                    return img_src
                else:
                    return urljoin(BASE_URL, img_src)
        
        return None
        
    except Exception as e:
        print(f"[ERROR] 상세 페이지 스크레이핑 실패 {eng_name}: {e}")
        return None

# 메인 스크레이핑 실행
def main():
    """메인 실행 함수"""
    print("Another Eden 이미지 재스크레이핑 시작...")
    print("=" * 50)
    
    # 한글 매핑 로드
    korean_mapping = load_korean_mapping()
    print(f"한글 매핑 로드: {len(korean_mapping)}개")
    
    # 캐릭터 목록 스크레이핑
    print("캐릭터 목록 스크레이핑 중...")
    characters = scrape_character_list()
    print(f"총 {len(characters)}개 캐릭터 발견")
    
    if not characters:
        print("[ERROR] 캐릭터를 찾을 수 없습니다")
        return
    
    # 이미지 저장 디렉토리 생성
    os.makedirs(IMAGE_DIR, exist_ok=True)
    
    # 결과 데이터 수집
    results = []
    success_count = 0
    
    for i, char in enumerate(characters, 1):
        eng_name = char['english_name']
        
        # 한글명 변환
        kor_name = convert_to_korean_name(eng_name, korean_mapping)
        
        # 파일명 결정 (한글 우선)
        if kor_name != eng_name:
            filename_base = sanitize_filename(kor_name)
            display_name = kor_name
        else:
            filename_base = sanitize_filename(eng_name)
            display_name = eng_name
        
        print(f"[{i}/{len(characters)}] {eng_name} -> {display_name}")
        
        # 이미지 URL 결정
        img_url = char['image_url']
        if not img_url:
            img_url = scrape_character_images(char['detail_url'], eng_name)
        
        if not img_url:
            print(f"  [SKIP] 이미지 URL 없음")
            results.append({
                'english_name': eng_name,
                'korean_name': kor_name,
                'image_path': '',
                'status': 'no_image_url'
            })
            continue
        
        # 이미지 다운로드
        ext = os.path.splitext(img_url)[1] or '.png'
        save_name = f"{filename_base}{ext}"
        save_path = os.path.join(IMAGE_DIR, save_name)
        
        if download_image(img_url, save_path):
            print(f"  [OK] 저장 완료: {save_name}")
            success_count += 1
            status = 'success'
        else:
            print(f"  [FAIL] 다운로드 실패")
            save_path = ''
            status = 'download_failed'
        
        results.append({
            'english_name': eng_name,
            'korean_name': kor_name,
            'image_path': save_path,
            'image_url': img_url,
            'status': status
        })
        
        time.sleep(0.5)  # 서버 부하 방지
    
    # 결과 저장
    df_result = pd.DataFrame(results)
    csv_path = 'eden_roulette_data.csv'
    df_result.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 50)
    print(f"스크레이핑 완료!")
    print(f"총 캐릭터: {len(characters)}")
    print(f"성공: {success_count}")
    print(f"실패: {len(characters) - success_count}")
    print(f"데이터 저장: {csv_path}")
    
    # 통계 출력
    status_counts = df_result['status'].value_counts()
    print("\n상태별 통계:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

if __name__ == "__main__":
    main()
