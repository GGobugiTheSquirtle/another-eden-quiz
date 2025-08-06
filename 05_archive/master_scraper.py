#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Another Eden 통합 스크래퍼
웹사이트 구조 변경에 자동 대응하는 통합 데이터 생성기
"""

import os
import sys
import re
import json
import time
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote, parse_qs
from bs4 import BeautifulSoup
import unicodedata
from datetime import datetime

# 스크래핑 설정
BASE_URL = "https://anothereden.wiki"
TARGET_URL = "https://anothereden.wiki/w/Characters"
PERSONALITY_URL = "https://anothereden.wiki/w/Characters/Personality"

# 세션 설정 (리다이렉트 처리)
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

class UnifiedScraper:
    """통합 Another Eden 스크래퍼 (자동 대응형)"""
    
    def __init__(self):
        """초기화"""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.character_data = []
        self.personality_data = {}
        
        # 디렉토리 설정
        self.setup_directories()
        
        # 매핑 데이터 로드
        self.load_name_mapping()
        self.load_personality_mapping()
    
    def setup_directories(self):
        """디렉토리 설정"""
        self.csv_dir = self.project_root / "04_data" / "csv"
        self.image_dir = self.project_root / "04_data" / "images" / "character_art"
        self.icon_dir = self.project_root / "04_data" / "images" / "character_art" / "icons"
        
        # 디렉토리 생성
        for dir_path in [self.csv_dir, self.image_dir, self.icon_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ 디렉토리 설정 완료")
        print(f"   📊 데이터: {self.csv_dir}")
        print(f"   🖼️ 이미지: {self.image_dir}")
    
    def load_name_mapping(self):
        """한글 이름 매핑 로드"""
        mapping_file = self.project_root / "04_data" / "csv" / "Matching_names.csv"
        if mapping_file.exists():
            try:
                df = pd.read_csv(mapping_file)
                # 컬럼명 확인 및 매핑
                if 'English' in df.columns and 'Korean' in df.columns:
                    self.name_mapping = dict(zip(df['English'], df['Korean']))
                elif '캐릭터명 (입력)' in df.columns and '캐릭터명 (매칭)' in df.columns:
                    self.name_mapping = dict(zip(df['캐릭터명 (입력)'], df['캐릭터명 (매칭)']))
                else:
                    # 첫 번째와 두 번째 컬럼 사용
                    self.name_mapping = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
                
                print(f"✅ 한글 매칭 로드: {len(self.name_mapping)}개")
            except Exception as e:
                print(f"⚠️ 매칭 파일 로드 실패: {e}")
                self.name_mapping = {}
        else:
            print("⚠️ 매칭 파일이 없습니다")
            self.name_mapping = {}
    
    def load_personality_mapping(self):
        """퍼스널리티 매핑 로드"""
        mapping_file = self.project_root / "04_data" / "csv" / "personality_matching.csv"
        if mapping_file.exists():
            try:
                df = pd.read_csv(mapping_file)
                self.personality_mapping = dict(zip(df['English'], df['Korean']))
                print(f"✅ 퍼스널리티 매핑 로드: {len(self.personality_mapping)}개")
            except Exception as e:
                print(f"⚠️ 퍼스널리티 매핑 로드 실패: {e}")
                self.personality_mapping = {}
        else:
            print("⚠️ 퍼스널리티 매핑 파일이 없습니다")
            self.personality_mapping = {}
    
    def load_existing_personality_data(self):
        """기존 퍼스널리티 데이터 로드 (레거시 스크래퍼 결과 활용)"""
        personality_file = Path("character_personalities.csv")
        if personality_file.exists():
            try:
                df = pd.read_csv(personality_file)
                personality_data = {}
                
                for _, row in df.iterrows():
                    eng_name = row['English_Name']
                    personalities = row['Personalities_List'].split('|')
                    personality_data[eng_name] = personalities
                
                print(f"✅ 기존 퍼스널리티 데이터 로드: {len(personality_data)}명")
                return personality_data
            except Exception as e:
                print(f"⚠️ 기존 퍼스널리티 데이터 로드 실패: {e}")
                return {}
        else:
            print("⚠️ 기존 퍼스널리티 데이터 파일이 없습니다")
            return {}
    
    def convert_to_korean(self, english_name):
        """영어 이름을 한글로 변환"""
        if english_name in self.name_mapping:
            return self.name_mapping[english_name]
        return english_name
    
    def sanitize_filename(self, name):
        """파일명 정리"""
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = sanitized.replace(' ', '_')
        sanitized = sanitized.replace('&', 'and')
        return sanitized
    
    def get_unique_filename(self, filepath):
        """중복되지 않는 파일명 생성"""
        if not filepath.exists():
            return filepath
        
        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1
        
        while filepath.exists():
            new_name = f"{stem}_{counter}{suffix}"
            filepath = filepath.parent / new_name
            counter += 1
        
        return filepath
    
    def download_image(self, image_url, kor_name="", eng_name=""):
        """이미지 다운로드 (레거시 방식 참조)"""
        if not image_url or image_url.startswith('data:'):
            return ""
        
        try:
            # URL 정규화
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            elif image_url.startswith('/'):
                image_url = BASE_URL + image_url
            
            # 레거시 방식의 파일명 생성 로직
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)
            image_name_from_f = query_params.get('f', [None])[0]
            
            if image_name_from_f:
                image_name = os.path.basename(unquote(image_name_from_f))
            else:
                image_name = os.path.basename(unquote(parsed_url.path.split('?')[0]))

            if not image_name or image_name.lower() in ["thumb.php", "index.php"]:
                temp_name = unquote(image_url.split('/')[-1].split('?')[0])
                image_name = (temp_name[:50] + ".png") if temp_name else "unknown_image.png"

            base_name, ext = os.path.splitext(image_name)
            if not ext or len(ext) > 5:
                try:
                    head_resp = session.head(image_url, timeout=3, allow_redirects=True)
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get('Content-Type')
                    if content_type:
                        import mimetypes
                        guessed_ext = mimetypes.guess_extension(content_type.split(';')[0])
                        image_name = base_name + (guessed_ext if guessed_ext and guessed_ext != '.jpe' else ('.jpg' if guessed_ext == '.jpe' else '.png'))
                    else: 
                        image_name = base_name + ".png" 
                except: 
                    image_name = base_name + ".png"
            
            # 파일명 정리
            image_name = re.sub(r'[<>:"/\\|?*]', '_', image_name)
            image_name = image_name[:200]
            
            # 캐릭터 이미지는 icons 폴더에 저장
            save_path_dir = self.icon_dir
            save_path = save_path_dir / image_name
            save_path = self.get_unique_filename(save_path)
            
            # 이미 존재하는 파일 체크
            if save_path.exists() and save_path.stat().st_size > 0:
                print(f"   ✅ 이미지 이미 존재: {save_path.name}")
                return str(save_path)
            
            # 이미지 다운로드
            response = session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            print(f"   📥 이미지 다운로드: {save_path.name}")
            time.sleep(0.05)  # 서버 부하 방지
            return str(save_path)
            
        except Exception as e:
            print(f"   ⚠️ 이미지 다운로드 실패: {e}")
            return ""
    
    def download_icon(self, icon_url, alt_text, subfolder):
        """아이콘 다운로드 (레거시 방식 참조)"""
        if not icon_url or icon_url.startswith('data:'):
            return ""
        
        try:
            # URL 정규화
            if icon_url.startswith('//'):
                icon_url = 'https:' + icon_url
            elif icon_url.startswith('/'):
                icon_url = BASE_URL + icon_url
            
            # 레거시 방식의 파일명 생성
            parsed_url = urlparse(icon_url)
            query_params = parse_qs(parsed_url.query)
            image_name_from_f = query_params.get('f', [None])[0]
            
            if image_name_from_f:
                image_name = os.path.basename(unquote(image_name_from_f))
            else:
                image_name = os.path.basename(unquote(parsed_url.path.split('?')[0]))

            if not image_name or image_name.lower() in ["thumb.php", "index.php"]:
                temp_name = unquote(icon_url.split('/')[-1].split('?')[0])
                image_name = (temp_name[:50] + ".png") if temp_name else "unknown_icon.png"

            base_name, ext = os.path.splitext(image_name)
            if not ext or len(ext) > 5:
                try:
                    head_resp = session.head(icon_url, timeout=3, allow_redirects=True)
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get('Content-Type')
                    if content_type:
                        import mimetypes
                        guessed_ext = mimetypes.guess_extension(content_type.split(';')[0])
                        image_name = base_name + (guessed_ext if guessed_ext and guessed_ext != '.jpe' else ('.jpg' if guessed_ext == '.jpe' else '.png'))
                    else: 
                        image_name = base_name + ".png" 
                except: 
                    image_name = base_name + ".png"
            
            # 파일명 정리
            image_name = re.sub(r'[<>:"/\\|?*]', '_', image_name)
            image_name = image_name[:200]
            
            # 서브폴더 생성
            subfolder_path = self.icon_dir / subfolder
            subfolder_path.mkdir(parents=True, exist_ok=True)
            
            # 파일 경로
            icon_path = subfolder_path / image_name
            icon_path = self.get_unique_filename(icon_path)
            
            # 이미 존재하는 파일 체크
            if icon_path.exists() and icon_path.stat().st_size > 0:
                print(f"   ✅ 아이콘 이미 존재: {icon_path.name}")
                return str(icon_path)
            
            # 아이콘 다운로드
            response = session.get(icon_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(icon_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            print(f"   📥 아이콘 다운로드: {icon_path.name}")
            time.sleep(0.05)  # 서버 부하 방지
            return str(icon_path)
            
        except Exception as e:
            print(f"   ⚠️ 아이콘 다운로드 실패: {e}")
            return ""
    
    def scrape_character_list_adaptive(self):
        """적응형 캐릭터 목록 스크래핑 (레거시 방식)"""
        print("📡 캐릭터 목록 스크래핑 중...")
        
        try:
            response = session.get(TARGET_URL, timeout=60)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 레거시 방식: chara-table 또는 wikitable 클래스 찾기
            char_table = soup.find('table', class_='chara-table') or soup.find('table', class_='wikitable')
            
            if not char_table:
                print("❌ 캐릭터 테이블을 찾을 수 없습니다")
                return []
            
            print("✅ 캐릭터 테이블 발견. 행 파싱 중...")
            
            characters = []
            rows = char_table.find_all('tr')
            total_rows = len(rows) - 1  # 헤더 제외
            
            print(f"📊 발견된 캐릭터 행: {total_rows}개")
            
            for i, row in enumerate(rows[1:], 1):  # 헤더 제외
                cells = row.find_all('td')
                if len(cells) < 4:
                    continue
                
                try:
                    # 레거시 방식: 아이콘 셀 (첫 번째 셀)
                    icon_cell = cells[0]
                    icon_img_tag = icon_cell.find('img')
                    icon_src = icon_img_tag.get('src', '') if icon_img_tag else ''
                    
                    # 레거시 방식: 이름/희귀도 셀 (두 번째 셀)
                    name_rarity_cell = cells[1]
                    name_tag = name_rarity_cell.find('a')
                    
                    if not name_tag:
                        continue
                    
                    original_name = name_tag.text.strip()
                    detail_url = urljoin(BASE_URL, name_tag.get('href', ''))
                    
                    if not original_name or not detail_url:
                        continue
                    
                    # 레거시 방식: 희귀도 추출
                    rarity = ""
                    lines_in_cell = [line.strip() for line in name_rarity_cell.get_text(separator='\n').splitlines() if line.strip()]
                    for line_text in reversed(lines_in_cell):
                        if "★" in line_text:
                            rarity = line_text
                            break
                    if not rarity:
                        rarity_match = re.search(r'\d(?:~\d)?★(?:\s*\S+)?', name_rarity_cell.get_text(separator=" ").strip())
                        if rarity_match:
                            rarity = rarity_match.group(0).strip()
                    
                    # 레거시 방식: 속성/장비 셀 (세 번째 셀)
                    element_equipment_cell = cells[2]
                    ee_icon_tags = element_equipment_cell.find_all('img')
                    element_equipment_icon_paths = []
                    element_equipment_icon_alts = []
                    
                    for img_tag in ee_icon_tags:
                        ee_src = img_tag.get('src')
                        ee_alt = img_tag.get('alt', "")
                        if ee_src:
                            local_path = self.download_icon(ee_src, ee_alt, "elements_equipment")
                            if local_path:
                                element_equipment_icon_paths.append(local_path)
                                element_equipment_icon_alts.append(ee_alt)
                    
                    # 출시일 셀 (네 번째 셀)
                    release_date = cells[3].text.strip() if len(cells) > 3 else ""
                    
                    characters.append({
                        'english_name': original_name,
                        'detail_url': detail_url,
                        'image_url': icon_src,
                        'rarity': rarity,
                        'element_equipment_icon_paths': element_equipment_icon_paths,
                        'element_equipment_icon_alts': element_equipment_icon_alts,
                        'release_date': release_date
                    })
                    
                    if i % 50 == 0:
                        print(f"   📝 처리 중: {i}/{total_rows}")
                        
                except Exception as e:
                    print(f"   ⚠️ 행 {i} 처리 실패: {e}")
                    continue
            
            print(f"✅ 캐릭터 목록 스크래핑 완료: {len(characters)}개")
            return characters
            
        except Exception as e:
            print(f"⚠️ 스크래핑 실패: {e}")
            return []
    
    def scrape_from_tables(self, soup):
        """테이블에서 캐릭터 추출"""
        characters = []
        
        # 알려진 테이블 클래스들 시도
        table_classes = ['chara-table', 'wikitable', 'sortable', 'character-table']
        
        for class_name in table_classes:
            tables = soup.find_all('table', class_=class_name)
            if tables:
                print(f"✅ {class_name} 클래스 테이블 발견")
                
                for table in tables:
                    rows = table.find_all('tr')[1:]  # 헤더 제외
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue
                        
                        # 이름 및 링크 추출
                        name_cell = cells[1] if len(cells) > 1 else cells[0]
                        name_tag = name_cell.find('a')
                        
                        if not name_tag:
                            continue
                        
                        original_name = name_tag.text.strip()
                        detail_url = urljoin(BASE_URL, name_tag.get('href', ''))
                        
                        if not original_name or not detail_url:
                            continue
                        
                        # 이미지 URL 추출
                        icon_cell = cells[0] if len(cells) > 0 else None
                        image_url = ""
                        if icon_cell:
                            icon_img = icon_cell.find('img')
                            if icon_img:
                                image_url = icon_img.get('src', '')
                        
                        characters.append({
                            'english_name': original_name,
                            'detail_url': detail_url,
                            'image_url': image_url
                        })
                
                if characters:
                    return characters
        
        return []
    
    def scrape_from_links(self, soup):
        """모든 링크에서 캐릭터 찾기"""
        characters = []
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link['href']
            # 캐릭터 페이지 필터링
            if ('/w/' in href and 
                'Character' not in href and 
                'Special:' not in href and
                'Category:' not in href and
                'Template:' not in href and
                'User:' not in href and
                'Talk:' not in href and
                'Help:' not in href and
                'File:' not in href and
                'MediaWiki:' not in href):
                
                title = link.get('title', '') or link.get_text(strip=True)
                if title and len(title) > 2 and len(title) < 50:
                    characters.append({
                        'english_name': title,
                        'detail_url': urljoin(BASE_URL, href),
                        'image_url': ''
                    })
        
        # 중복 제거
        unique_chars = []
        seen = set()
        for char in characters:
            if char['english_name'] not in seen:
                unique_chars.append(char)
                seen.add(char['english_name'])
        
        return unique_chars[:50]  # 최대 50개만
    
    def scrape_direct_characters(self):
        """직접 캐릭터 페이지 스크래핑"""
        # 알려진 캐릭터 이름들로 직접 시도
        known_characters = [
            'Aldo', 'Feinne', 'Riica', 'Cyrus', 'Amy', 'Mariel', 'Bivette',
            'Nagi', 'Mighty', 'Toova', 'Lokido', 'Anabel', 'Suzette', 'Isuka'
        ]
        
        characters = []
        for char_name in known_characters:
            try:
                char_url = f"{BASE_URL}/w/{char_name}"
                response = session.get(char_url, timeout=10)
                if response.status_code == 200:
                    characters.append({
                        'english_name': char_name,
                        'detail_url': char_url,
                        'image_url': ''
                    })
                    print(f"   ✅ {char_name} 페이지 발견")
            except:
                continue
        
        return characters
    
    def scrape_character_details(self, detail_url, eng_name):
        """캐릭터 상세 정보 스크래핑 (레거시 방식 참조)"""
        try:
            response = session.get(detail_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {}
            element_icons = []
            weapon_icons = []
            
            # 레거시 방식: 모든 테이블에서 정보 찾기
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) < 2:
                        continue
                    
                    header_cell = cells[0]
                    value_cell = cells[-1] if len(cells) > 1 else None
                    
                    if not header_cell or not value_cell:
                        continue
                    
                    header_text = header_cell.get_text(strip=True).lower()
                    value_text = value_cell.get_text(strip=True)
                    
                    # 레거시 방식: 희귀도 추출
                    if any(keyword in header_text for keyword in ['rarity', '희귀도', 'star', '별']):
                        # 레거시 방식: ★ 패턴 찾기
                        rarity_match = re.search(r'\d(?:~\d)?★(?:\s*\S+)?', value_text)
                        if rarity_match:
                            data['rarity'] = rarity_match.group(0).strip()
                        elif '★' in value_text:
                            data['rarity'] = value_text
                        elif 'SA' in value_text.upper() or 'Stellar Awakened' in value_text:
                            data['rarity'] = "5★ 성도각성"
                    
                    # 레거시 방식: 속성 추출
                    elif any(keyword in header_text for keyword in ['element', '속성', 'type']):
                        if value_text and value_text.lower() != 'n/a':
                            data['elements'] = value_text
                            
                            # 속성 아이콘 찾기 (레거시 방식)
                            img_tags = value_cell.find_all('img')
                            for img in img_tags:
                                src = img.get('src', '')
                                alt = img.get('alt', '').lower()
                                if src and any(element in alt for element in ['fire', 'water', 'earth', 'wind', 'light', 'dark', 'crystal']):
                                    icon_path = self.download_icon(src, alt, "elements_equipment")
                                    if icon_path:
                                        element_icons.append(icon_path)
                    
                    # 레거시 방식: 무기 추출
                    elif any(keyword in header_text for keyword in ['weapon', '무기', 'arms']):
                        if value_text and value_text.lower() != 'n/a':
                            data['weapons'] = value_text
                            
                            # 무기 아이콘 찾기 (레거시 방식)
                            img_tags = value_cell.find_all('img')
                            for img in img_tags:
                                src = img.get('src', '')
                                alt = img.get('alt', '').lower()
                                if src and any(weapon in alt for weapon in ['sword', 'katana', 'axe', 'hammer', 'spear', 'bow', 'staff', 'fist']):
                                    icon_path = self.download_icon(src, alt, "elements_equipment")
                                    if icon_path:
                                        weapon_icons.append(icon_path)
            
            # 레거시 방식: 고화질 이미지 찾기
            img_tag = soup.find('img', class_='thumbimage') or soup.find('img', class_='infobox-image')
            if img_tag:
                img_src = img_tag.get('src', '')
                if img_src.startswith('http'):
                    data['high_res_image_url'] = img_src
                else:
                    data['high_res_image_url'] = urljoin(BASE_URL, img_src)
            
            # 아이콘 정보 추가
            data['element_icons'] = element_icons
            data['weapon_icons'] = weapon_icons
            
            # 디버그 정보 출력
            if data:
                print(f"  📊 {eng_name}: 희귀도={data.get('rarity', 'N/A')}, 속성={data.get('elements', 'N/A')}, 무기={data.get('weapons', 'N/A')}")
                if element_icons:
                    print(f"    🎯 속성 아이콘: {len(element_icons)}개")
                if weapon_icons:
                    print(f"    ⚔️ 무기 아이콘: {len(weapon_icons)}개")
            
            return data
            
        except Exception as e:
            print(f"⚠️ {eng_name} 상세 정보 스크래핑 실패: {e}")
            return {}
    
    def scrape_personalities(self):
        """퍼스널리티 정보 스크래핑 (레거시 방식 참조)"""
        print("🎭 퍼스널리티 정보 스크래핑 중...")
        try:
            response = session.get(PERSONALITY_URL, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            character_personalities = {}
            
            # 레거시 방식: wikitable 클래스를 가진 테이블들 찾기
            tables = soup.find_all('table', class_='wikitable')
            print(f"📊 발견된 퍼스널리티 테이블 수: {len(tables)}")
            
            personality_count = 0
            character_total = 0
            
            for table_idx, table in enumerate(tables):
                print(f"🔍 퍼스널리티 테이블 {table_idx + 1} 처리 중...")
                
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # 첫 번째 셀: 퍼스널리티 이름
                        personality_cell = cells[0]
                        personality_eng = personality_cell.get_text(strip=True)
                        
                        # 한국어 퍼스널리티명으로 변환
                        personality_kor = self.personality_mapping.get(personality_eng, personality_eng)
                        
                        # 두 번째 셀: 캐릭터 목록
                        characters_cell = cells[1]
                        
                        # 캐릭터 링크들 추출
                        character_links = characters_cell.find_all('a', href=True)
                        characters_found = []
                        
                        for link in character_links:
                            href = link.get('href', '')
                            # 캐릭터 페이지인지 확인 (/w/로 시작하고 특정 패턴 제외)
                            if (href.startswith('/w/') and 
                                'Character' not in href and 
                                'Personality' not in href and
                                'Special:' not in href and
                                'Category:' not in href and
                                'Template:' not in href and
                                'User:' not in href and
                                'Talk:' not in href and
                                'Help:' not in href and
                                'File:' not in href and
                                'MediaWiki:' not in href):
                                
                                char_name = link.get_text(strip=True)
                                if char_name and len(char_name) > 1:
                                    characters_found.append(char_name)
                        
                        if characters_found:
                            personality_count += 1
                            character_total += len(characters_found)
                            
                            print(f"  🎭 {personality_kor} ({personality_eng}): {len(characters_found)}명")
                            
                            # 각 캐릭터에 퍼스널리티 추가
                            for char_name in characters_found:
                                if char_name not in character_personalities:
                                    character_personalities[char_name] = []
                                character_personalities[char_name].append(personality_kor)
                            
                            # 처음 몇 개만 상세 출력
                            if personality_count <= 5:
                                sample_chars = characters_found[:5]
                                print(f"     └─ 샘플: {', '.join(sample_chars)}")
            
            print(f"✅ 퍼스널리티 데이터 스크래핑 완료!")
            print(f"📊 총 퍼스널리티 수: {personality_count}개")
            print(f"🎭 총 캐릭터 수: {len(character_personalities)}명")
            print(f"📈 총 퍼스널리티 연결: {character_total}개")
            
            return character_personalities
            
        except Exception as e:
            print(f"❌ 퍼스널리티 스크래핑 실패: {e}")
            return {}
    
    def create_unified_csv(self, characters, personality_data):
        """통합 CSV 파일 생성"""
        print("📊 통합 CSV 파일 생성 중...")
        
        unified_data = []
        
        for char in characters:
            # 기본 정보
            korean_name = self.convert_to_korean(char.get('english_name', ''))
            
            # 퍼스널리티 정보
            base_eng_name = re.sub(r'\s*\(.*\)$', '', char.get('english_name', '')).strip()
            personalities = personality_data.get(base_eng_name, [])
            korean_personalities = []
            for personality in personalities:
                korean_personality = self.personality_mapping.get(personality, personality)
                korean_personalities.append(korean_personality)
            
            # 아이콘 경로 처리
            element_icons = char.get('element_equipment_icon_paths', [])
            weapon_icons = char.get('weapon_icons', [])
            
            # 통합 데이터 구조
            unified_row = {
                '캐릭터명': korean_name,
                'English_Name': char.get('english_name', ''),
                '캐릭터아이콘경로': char.get('image_url', ''),
                '희귀도': char.get('rarity', ''),
                '속성명리스트': char.get('elements', ''),
                '무기명리스트': char.get('weapons', ''),
                '퍼스널리티리스트': ', '.join(korean_personalities),
                '속성_아이콘경로리스트': '|'.join(element_icons),
                '무기_아이콘경로리스트': '|'.join(weapon_icons),
                '방어구_아이콘경로리스트': ''   # 나중에 추가
            }
            
            unified_data.append(unified_row)
        
        # 통합 CSV 생성
        df = pd.DataFrame(unified_data)
        unified_csv_path = self.csv_dir / "eden_unified_data.csv"
        df.to_csv(unified_csv_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ 통합 CSV 생성 완료: {unified_csv_path}")
        return unified_csv_path
    
    def run_unified_scraping(self):
        """통합 스크래핑 실행"""
        print("🚀 Another Eden 통합 스크래퍼 시작")
        print("=" * 60)
        
        # 1. 적응형 캐릭터 목록 스크래핑
        characters = self.scrape_character_list_adaptive()
        if not characters:
            print("❌ 캐릭터 데이터 없음")
            return False
        
        print(f"📊 발견된 캐릭터: {len(characters)}개")
        
        # 2. 퍼스널리티 정보 로드 (기존 데이터 활용)
        personality_data = self.load_existing_personality_data()
        if not personality_data:
            print("🔄 기존 퍼스널리티 데이터가 없어 새로 스크래핑합니다...")
            personality_data = self.scrape_personalities()
        
        # 3. 상세 정보 스크래핑 (처음 10개만 테스트)
        print(f"📡 {min(10, len(characters))}개 캐릭터 상세 정보 스크래핑 중...")
        
        for i, char in enumerate(characters[:10], 1):
            print(f"[{i}/{min(10, len(characters))}] {char['english_name']}")
            
            # 상세 정보 스크래핑
            details = self.scrape_character_details(char['detail_url'], char['english_name'])
            char.update(details)
            
            # 이미지 다운로드
            image_url = char.get('high_res_image_url') or char.get('image_url')
            if image_url:
                image_path = self.download_image(image_url, char.get('korean_name', ''), char['english_name'])
                char['image_url'] = image_path # image_path를 image_url로 변경
            
            # 한글 이름 추가
            char['korean_name'] = self.convert_to_korean(char['english_name'])
            
            time.sleep(1)  # 서버 부하 방지
        
        # 4. 통합 CSV 생성
        unified_csv_path = self.create_unified_csv(characters, personality_data)
        
        print("\n🎉 통합 스크래핑 완료!")
        print("=" * 60)
        print(f"📊 처리된 캐릭터: {len(characters)}개")
        print(f"💾 통합 CSV: {unified_csv_path}")
        
        return True

def main():
    """메인 실행 함수"""
    scraper = UnifiedScraper()
    success = scraper.run_unified_scraping()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
