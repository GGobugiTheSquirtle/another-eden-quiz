#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Another Eden 속성 정보 스크래퍼
캐릭터들의 속성 정보를 완전히 스크래핑하여 데이터를 보완합니다.
"""

import os
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, parse_qs, urlparse
import re
import unicodedata
import json

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 스크래핑 설정
BASE_URL = "https://anothereden.wiki"
TARGET_URL = "https://anothereden.wiki/w/Characters"

class ElementScraper:
    """속성 정보 스크래퍼"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.element_mapping = {
            'Fire': '불',
            'Water': '물', 
            'Earth': '땅',
            'Wind': '바람',
            'Thunder': '번개',
            'Shade': '그림자',
            'Crystal': '결정',
            'Light': '빛',
            'Dark': '어둠'
        }
        self.setup_directories()
        
    def setup_directories(self):
        """필요한 디렉토리 생성"""
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ 디렉토리 설정 완료: {CSV_DIR}")
    
    def load_existing_data(self):
        """기존 데이터 로드"""
        csv_path = CSV_DIR / "eden_unified_data.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            print(f"✅ 기존 데이터 로드: {len(df)}개 캐릭터")
            return df
        else:
            print("⚠️ 기존 데이터 파일이 없습니다.")
            return pd.DataFrame()
    
    def scrape_character_elements(self, character_url, character_name):
        """캐릭터의 속성 정보 스크래핑"""
        try:
            response = requests.get(character_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # infobox에서 속성 정보 추출
            infobox = soup.find('table', class_='infobox')
            if not infobox:
                return None
            
            elements = []
            rows = infobox.find_all('tr')
            
            for row in rows:
                header = row.find(['th', 'td'])
                if not header:
                    continue
                
                header_text = header.get_text(strip=True)
                if any(keyword in header_text for keyword in ['Element', '속성', 'Type']):
                    element_cell = row.find_all(['td', 'th'])[-1]
                    element_text = element_cell.get_text(strip=True)
                    
                    # 영어 속성을 한글로 변환
                    for eng, kor in self.element_mapping.items():
                        if eng.lower() in element_text.lower():
                            elements.append(kor)
                    
                    # 한글 속성 직접 확인
                    for kor in self.element_mapping.values():
                        if kor in element_text:
                            elements.append(kor)
            
            # 중복 제거
            elements = list(set(elements))
            return ', '.join(elements) if elements else None
            
        except Exception as e:
            print(f"⚠️ {character_name} 속성 스크래핑 실패: {e}")
            return None
    
    def scrape_all_character_elements(self):
        """모든 캐릭터의 속성 정보 스크래핑"""
        print("🔥 모든 캐릭터 속성 정보 스크래핑 중...")
        
        try:
            response = requests.get(TARGET_URL, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 캐릭터 링크들 찾기
            character_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if (href.startswith('/w/') and 
                    'Character' not in href and 
                    'Personality' not in href and
                    'Special:' not in href and
                    'Category:' not in href and
                    'Template:' not in href):
                    
                    character_name = link.get_text(strip=True)
                    if character_name and len(character_name) > 1:
                        character_links.append({
                            'name': character_name,
                            'url': urljoin(BASE_URL, href)
                        })
            
            print(f"📋 발견된 캐릭터: {len(character_links)}개")
            
            # 각 캐릭터의 속성 정보 스크래핑
            character_elements = {}
            for i, char in enumerate(character_links, 1):
                print(f"🔍 [{i}/{len(character_links)}] {char['name']} 속성 스크래핑 중...")
                
                elements = self.scrape_character_elements(char['url'], char['name'])
                if elements:
                    character_elements[char['name']] = elements
                
                # 서버 부하 방지
                time.sleep(1)
            
            print(f"✅ 속성 정보 스크래핑 완료: {len(character_elements)}개")
            return character_elements
            
        except Exception as e:
            print(f"❌ 속성 정보 스크래핑 실패: {e}")
            return {}
    
    def update_existing_data(self, element_data):
        """기존 데이터에 속성 정보 업데이트"""
        df = self.load_existing_data()
        if df.empty:
            print("⚠️ 업데이트할 데이터가 없습니다.")
            return
        
        # 영어 이름을 기준으로 매칭
        updated_count = 0
        for index, row in df.iterrows():
            eng_name = row.get('English_Name', '')
            if eng_name and eng_name in element_data:
                df.at[index, '속성명리스트'] = element_data[eng_name]
                updated_count += 1
        
        # 업데이트된 데이터 저장
        output_path = CSV_DIR / "eden_unified_data_updated.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"✅ 데이터 업데이트 완료: {updated_count}개 캐릭터 속성 정보 업데이트")
        print(f"📁 저장된 파일: {output_path}")
        
        # 속성 정보 통계
        element_stats = {}
        for elements in df['속성명리스트'].dropna():
            for element in elements.split(', '):
                element = element.strip()
                if element:
                    element_stats[element] = element_stats.get(element, 0) + 1
        
        print("\n📊 속성 정보 통계:")
        for element, count in sorted(element_stats.items()):
            print(f"   {element}: {count}개 캐릭터")
    
    def run_full_scraping(self):
        """전체 속성 정보 스크래핑 실행"""
        print("🚀 Another Eden 속성 정보 스크래핑 시작")
        print("=" * 50)
        
        # 기존 데이터 로드
        df = self.load_existing_data()
        if df.empty:
            print("❌ 기존 데이터가 없습니다. 먼저 기본 데이터를 생성해주세요.")
            return
        
        # 속성 정보 스크래핑
        element_data = self.scrape_all_character_elements()
        
        if element_data:
            # 데이터 업데이트
            self.update_existing_data(element_data)
        else:
            print("❌ 속성 정보를 가져올 수 없습니다.")
        
        print("=" * 50)
        print("✅ 속성 정보 스크래핑 완료!")

def main():
    """메인 실행 함수"""
    scraper = ElementScraper()
    scraper.run_full_scraping()

if __name__ == "__main__":
    main() 