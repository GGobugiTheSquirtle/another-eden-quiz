#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Another Eden 마스터 스크래퍼
스크래핑 → 이미지 정리 → CSV 생성 → 데이터 정리까지 모든 작업을 통합 처리
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
import mimetypes
import base64
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
import shutil

# 레거시 방식 매핑 테이블 추가
ELEMENT_MAPPING = {
    # 속성 아이콘 매핑 (실제 파일명 → 한글 속성명)
    "Skill_Type_8_0.png": "무속성",
    "Skill_Type_8_1.png": "불",
    "Skill_Type_8_2.png": "땅",
    "Skill_Type_8_4.png": "물", 
    "Skill_Type_8_8.png": "바람",
    "Skill_Type_8_16.png": "번개",
    "Skill_Type_8_32.png": "그림자",
    "Skill_Type_8_64.png": "수정",
    # 추가 패턴들
    "St_attack_element_change1.png": "불",
    "St_attack_element_change2.png": "땅", 
    "St_attack_element_change4.png": "물",
    "St_attack_element_change8.png": "바람",
    "St_attack_element_change16.png": "번개",
    "St_attack_element_change32.png": "그림자",
    "St_attack_element_change64.png": "수정",
    # Light/Shadow 아이콘들
    "Guiding_Light_Icon.png": "빛",
    "Luring_Shadow_Icon.png": "그림자",
}

# ALT 텍스트 기반 매핑 추가
ALT_TEXT_MAPPING = {
    # ALT 텍스트 → 분류 및 한글명
    "Luring Shadow Icon.png": ("element", "그림자"),
    "Guiding Light Icon.png": ("element", "빛"),
    "Skill Type 8 0.png": ("element", "무속성"),
    "Skill Type 8 1.png": ("element", "불"),
    "Skill Type 8 2.png": ("element", "땅"),
    "Skill Type 8 4.png": ("element", "물"),
    "Skill Type 8 8.png": ("element", "바람"),
    "Skill Type 8 16.png": ("element", "번개"),
    "Skill Type 8 32.png": ("element", "그림자"),
    "Skill Type 8 64.png": ("element", "수정"),
    # 무기 ALT 텍스트들 (예시 - 실제 웹에서 확인 후 업데이트)
    "202000000 icon.png": ("weapon", "지팡이"),
    "202000001 icon.png": ("weapon", "검"),
    "202000002 icon.png": ("weapon", "도"),
    "202000003 icon.png": ("weapon", "도끼"),
    "202000004 icon.png": ("weapon", "창"),
    "202000005 icon.png": ("weapon", "활"),
    "202000006 icon.png": ("weapon", "주먹"),
    "202000007 icon.png": ("weapon", "망치"),
}

WEAPON_MAPPING = {
    # 무기 아이콘 매핑 (실제 파일명 → 한글 무기명)
    "202000000_icon.png": "지팡이",
    "202000001_icon.png": "검",
    "202000002_icon.png": "도",
    "202000003_icon.png": "도끼",
    "202000004_icon.png": "창",
    "202000005_icon.png": "활",
    "202000006_icon.png": "주먹",
    "202000007_icon.png": "망치",
}

ARMOR_MAPPING = {
    # 방어구 아이콘 매핑
    "216000002_icon.png": "팔찌",
    "216000003_icon.png": "목걸이", 
    "216000004_icon.png": "반지",
}

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRAPING_DIR = PROJECT_ROOT / "01_scraping"
DATA_DIR = PROJECT_ROOT / "04_data"
CSV_DIR = DATA_DIR / "csv"
IMAGE_DIR = DATA_DIR / "images" / "character_art"

# 스크래핑 설정
BASE_URL = "https://anothereden.wiki"
TARGET_URL = "https://anothereden.wiki/w/Characters"
PERSONALITY_URL = "https://anothereden.wiki/w/Characters/Personality"


class MasterScraper:
    """통합 마스터 스크래퍼"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.resolve()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.character_data = []
        self.name_mapping = {}
        self.personality_mapping = {}
        self.setup_directories()
        
    def setup_directories(self):
        """필요한 디렉토리 생성"""
        for directory in [CSV_DIR, IMAGE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 이미지 하위 폴더
        (IMAGE_DIR / "icons").mkdir(exist_ok=True)
        (IMAGE_DIR / "elements_equipment").mkdir(exist_ok=True)
        
        print(f"✅ 디렉토리 설정 완료")
        print(f"   📊 데이터: {CSV_DIR}")
        print(f"   🖼️ 이미지: {IMAGE_DIR}")
    
    def load_name_mapping(self):
        """한글 이름 매핑 로드"""
        mapping_file = CSV_DIR / "Matching_names.csv"
        if mapping_file.exists():
            try:
                df = pd.read_csv(mapping_file, encoding='utf-8-sig')
                for _, row in df.iterrows():
                    if len(row) >= 2:
                        eng_name = str(row.iloc[0]).strip()
                        kor_name = str(row.iloc[1]).strip()
                        if eng_name and kor_name and kor_name != 'nan':
                            self.name_mapping[eng_name.lower()] = kor_name
                print(f"✅ 한글 매칭 로드: {len(self.name_mapping)}개")
            except Exception as e:
                print(f"⚠️ 매핑 로드 실패: {e}")
        else:
            print("⚠️ Matching_names.csv 파일이 없습니다.")
    
    def load_personality_mapping(self):
        """퍼스널리티 매핑 로드"""
        mapping_file = CSV_DIR / "personality_matching.csv"
        if mapping_file.exists():
            try:
                df = pd.read_csv(mapping_file)
                for _, row in df.iterrows():
                    if 'English' in row and 'Korean' in row:
                        self.personality_mapping[row['English']] = row['Korean']
                print(f"✅ 퍼스널리티 매핑 로드: {len(self.personality_mapping)}개")
            except Exception as e:
                print(f"⚠️ 퍼스널리티 매핑 로드 실패: {e}")
        else:
            print("⚠️ personality_matching.csv 파일이 없습니다.")
    
    def convert_to_korean(self, english_name):
        """영어 이름을 한글로 변환 (스타일 접미사 고려)"""
        if not english_name:
            return english_name

        # 스타일과 축약형 매핑
        style_map = {
            'Another Style': 'AS',
            'Extra Style': 'ES',
            'AS': 'AS',
            'ES': 'ES',
            'Alter': 'Alter',
            'Manifestation': 'M',
            'NS': 'NS'
        }

        base_name = english_name.strip()
        style_suffix = ""

        # 정규식 패턴 생성
        pattern_str = r'\s*\(?(' + '|'.join(re.escape(k) for k in style_map.keys()) + r')\)?$'
        
        match = re.search(pattern_str, base_name, re.IGNORECASE)
        
        if match:
            matched_style_key = match.group(1)
            for key, abbreviation in style_map.items():
                if key.lower() == matched_style_key.lower():
                    style_suffix = " " + abbreviation
                    break
            
            base_name = base_name[:match.start()].strip()

        # 기본 이름을 한글로 변환
        korean_base = self.name_mapping.get(base_name.lower(), base_name)
        
        return korean_base + style_suffix
    
    def sanitize_filename(self, name):
        """파일명으로 안전하게 변환"""
        name = unicodedata.normalize('NFKC', name)
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip()
        return name
    
    def normalize_image_filename(self, korean_name, english_name):
        """이미지 파일명 정규화"""
        # 한글 이름을 우선 사용하되, 특수문자 처리
        if korean_name and korean_name.strip():
            base_name = korean_name.strip()
        else:
            base_name = english_name.strip()
        
        # 파일명 정규화
        normalized = self.sanitize_filename(base_name)
        return f"{normalized}.png"
    
    def get_unique_filename(self, filepath):
        """중복 방지를 위한 고유 파일명 생성"""
        if not os.path.exists(filepath):
            return filepath
        base, ext = os.path.splitext(filepath)
        counter = 1
        while True:
            new_filepath = f"{base} ({counter}){ext}"
            if not os.path.exists(new_filepath):
                return new_filepath
            counter += 1
    
    def download_image(self, image_url, kor_name="", eng_name=""):
        """이미지 다운로드"""
        if not image_url:
            return None

        full_image_url = urljoin(BASE_URL, image_url)
        try:
            # 파일 이름 및 확장자 결정
            parsed_url = urlparse(full_image_url)
            query_params = parse_qs(parsed_url.query)
            image_name_from_f = query_params.get('f', [None])[0]

            if image_name_from_f:
                image_name = os.path.basename(unquote(image_name_from_f))
            else:
                image_name = os.path.basename(unquote(parsed_url.path.split('?')[0]))

            if not image_name or image_name.lower() in ["thumb.php", "index.php"]:
                image_name = (eng_name or kor_name or "unknown") + ".png"

            base_name, ext = os.path.splitext(image_name)
            if not ext or len(ext) > 5:
                try:
                    head_resp = requests.head(full_image_url, timeout=5, allow_redirects=True)
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get('Content-Type')
                    if content_type:
                        guessed_ext = mimetypes.guess_extension(content_type.split(';')[0])
                        ext = guessed_ext if guessed_ext and guessed_ext != '.jpe' else ('.jpg' if guessed_ext == '.jpe' else '.png')
                    else:
                        ext = ".png"
                except requests.exceptions.RequestException:
                    ext = ".png"

            # 최종 파일 이름 생성 (정규화된 한글명 우선)
            final_name = self.normalize_image_filename(kor_name, eng_name)
            final_filename = final_name

            # 저장 경로 설정 및 중복 확인
            save_path = IMAGE_DIR / final_filename
            save_path.parent.mkdir(parents=True, exist_ok=True)

            if save_path.exists() and save_path.stat().st_size > 0:
                return str(save_path.relative_to(self.project_root).as_posix())

            # 이미지 다운로드
            img_response = requests.get(full_image_url, headers=self.headers, timeout=20, stream=True)
            img_response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in img_response.iter_content(8192):
                    f.write(chunk)
            
            return str(save_path.relative_to(self.project_root).as_posix())

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 네트워크 오류로 이미지 다운로드 실패: {full_image_url} ({e})")
            return None
        except Exception as e:
            print(f"⚠️ 알 수 없는 오류로 이미지 다운로드 실패: {full_image_url} ({e})")
            return None
    
    def download_character_image(self, image_url, kor_name, eng_name):
        """캐릭터 이미지 다운로드 및 저장 (중복 방지 개선)"""
        if not image_url:
            return None
        
        try:
            # URL 정규화
            if not image_url.startswith('http'):
                full_image_url = urljoin(BASE_URL, image_url)
            else:
                full_image_url = image_url
            
            # 파일명 정규화
            final_name = self.normalize_image_filename(kor_name, eng_name)
            final_filename = final_name

            # 저장 경로 설정 및 중복 확인
            save_path = IMAGE_DIR / final_filename
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # 중복 파일 체크 강화 (파일이 이미 존재하고 크기가 적절하면 스킵)
            if save_path.exists() and save_path.stat().st_size > 1000:  # 최소 1KB
                print(f"  ✅ 이미지 이미 존재: {save_path.name}")
                return str(save_path.relative_to(self.project_root).as_posix())

            # 이미지 다운로드
            print(f"  📥 이미지 다운로드 중: {save_path.name}")
            img_response = requests.get(full_image_url, headers=self.headers, timeout=20, stream=True)
            img_response.raise_for_status()

            # 파일 크기 체크
            content_length = img_response.headers.get('content-length')
            if content_length and int(content_length) < 1000:
                print(f"  ⚠️ 이미지 파일이 너무 작음: {content_length}바이트")
                return None

            # 파일 저장
            with open(save_path, 'wb') as f:
                for chunk in img_response.iter_content(8192):
                    f.write(chunk)
            
            # 저장된 파일 크기 재확인
            if save_path.stat().st_size < 1000:
                print(f"  ⚠️ 저장된 이미지 파일이 너무 작음")
                save_path.unlink()  # 작은 파일 삭제
                return None
            
            print(f"  ✅ 이미지 저장 완료: {save_path.name} ({save_path.stat().st_size}바이트)")
            return str(save_path.relative_to(self.project_root).as_posix())

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ 네트워크 오류로 이미지 다운로드 실패: {full_image_url} ({e})")
            return None
        except Exception as e:
            print(f"  ⚠️ 알 수 없는 오류로 이미지 다운로드 실패: {full_image_url} ({e})")
            return None
    
    def download_icon(self, icon_url, alt_text, subfolder):
        """아이콘 다운로드 및 저장 (중복 방지)"""
        if not icon_url:
            return ""
        
        try:
            # URL 정규화
            if not icon_url.startswith('http'):
                icon_url = urljoin(BASE_URL, icon_url)
            
            # alt_text 안전 처리
            if alt_text is None:
                alt_text = "unknown"
            elif not isinstance(alt_text, str):
                try:
                    alt_text = str(alt_text)
                except:
                    alt_text = "unknown"
            
            # URL에서 파일명 추출
            parsed_url = urlparse(icon_url)
            query_params = parse_qs(parsed_url.query)
            icon_name_from_f = query_params.get('f', [None])[0]
            
            # 원본 파일명 기반으로 저장 파일명 생성
            if icon_name_from_f:
                original_name = os.path.basename(unquote(icon_name_from_f))
                base_name, ext = os.path.splitext(original_name)
            else:
                original_name = os.path.basename(unquote(parsed_url.path.split('?')[0]))
                base_name, ext = os.path.splitext(original_name)
            
            # 확장자 처리
            if not ext or ext.lower() in ['.php'] or len(ext) > 5:
                ext = ".png"
            
            # 파일명 정리 (원본 파일명 우선 사용)
            if base_name and base_name.lower() not in ["thumb", "index"]:
                clean_name = self.sanitize_filename(base_name)
            else:
                # alt_text를 파일명으로 사용
                clean_name = re.sub(r'[^\w\-_]', '', alt_text.replace(' ', '_').lower())
                if not clean_name:
                    clean_name = "unknown"
            
            icon_filename = f"{clean_name}{ext}"
            
            # 저장 경로 설정
            icon_dir = IMAGE_DIR / subfolder
            icon_dir.mkdir(exist_ok=True)
            save_path = icon_dir / icon_filename
            
            # 중복 파일 체크 (파일이 이미 존재하고 크기가 0보다 크면 스킵)
            if save_path.exists() and save_path.stat().st_size > 0:
                return str(save_path.relative_to(self.project_root).as_posix())
            
            # 중복 파일명 처리 (필요시)
            save_path = self.get_unique_filename(save_path)
            
            # 아이콘 다운로드
            response = requests.get(icon_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # 파일 크기 체크 (최소 100바이트)
            if len(response.content) < 100:
                print(f"  ⚠️ 파일 크기가 너무 작음: {icon_url}")
                return ""
            
            # 파일 저장
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  🎯 아이콘 저장: {save_path.name}")
            return str(save_path.relative_to(self.project_root).as_posix())
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ 네트워크 오류로 아이콘 다운로드 실패 ({icon_url}): {e}")
            return ""
        except Exception as e:
            print(f"  ⚠️ 아이콘 다운로드 실패 ({icon_url}): {e}")
            return ""
    
    def scrape_character_list(self):
        """캐릭터 목록 페이지 스크래핑 (출시일 포함)"""
        print("📡 캐릭터 목록 스크래핑 중...")
        try:
            response = requests.get(TARGET_URL, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 캐릭터 테이블 찾기 (다양한 클래스명 시도)
            char_table = soup.find('table', class_='chara-table') or soup.find('table', class_='wikitable')
            if not char_table:
                print("❌ 캐릭터 테이블을 찾을 수 없습니다")
                return []
            
            characters = []
            rows = char_table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 4:  # 최소 4개 컬럼 필요 (아이콘, 이름, 속성/장비, 출시일)
                    continue
                
                try:
                    # 캐릭터 링크 및 이름 추출
                    char_link = cols[1].find('a')  # 이름은 보통 두 번째 컬럼
                    if not char_link:
                        continue
                    
                    eng_name = char_link.get('title', '').strip()
                    detail_url = urljoin(BASE_URL, char_link.get('href', ''))
                    
                    if not eng_name or not detail_url:
                        continue
                    
                    # 이미지 URL 추출 (첫 번째 컬럼)
                    img_tag = cols[0].find('img')
                    img_url = img_tag.get('src', '') if img_tag else ''
                    
                    # 출시일 추출 (네 번째 컬럼, 레거시 로직 적용)
                    release_date = ""
                    if len(cols) >= 4:
                        release_date = cols[3].get_text(strip=True)
                        # 날짜 형식 정규화 (YYYY/MM/DD)
                        if release_date and len(release_date) > 5:
                            # 다양한 날짜 형식 처리
                            date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', release_date)
                            if date_match:
                                year, month, day = date_match.groups()
                                release_date = f"{year}/{int(month):02d}/{int(day):02d}"
                    
                    characters.append({
                        'english_name': eng_name,
                        'detail_url': detail_url,
                        'image_url': img_url,
                        'release_date': release_date
                    })
                    
                except Exception as e:
                    print(f"⚠️ 행 파싱 오류: {e}")
                    continue
            
            print(f"✅ 캐릭터 목록 스크래핑 완료: {len(characters)}개")
            return characters
            
        except Exception as e:
            print(f"❌ 캐릭터 목록 스크래핑 실패: {e}")
            return []
    
    def clean_scraped_data(self, data):
        """스크래핑된 데이터 정리 및 표준화 (완전 자동화)"""
        cleaned_data = {}
        
        # 기본 데이터 복사
        for key, value in data.items():
            cleaned_data[key] = value
        
        # 파일명 안전화 함수
        def safe_filename(name):
            if not name:
                return "unknown"
            unsafe_chars = r'<>:"/\|?*'
            safe_name = str(name)
            for char in unsafe_chars:
                safe_name = safe_name.replace(char, '_')
            safe_name = safe_name.replace(' ', '_')
            safe_name = re.sub(r'_+', '_', safe_name)
            return safe_name.strip('_')
        
        # 희귀도 표준화 및 3-4성 여부 확인
        def normalize_rarity_and_check(rarity_str):
            if not isinstance(rarity_str, str):
                return str(rarity_str), False
            
            rarity_str = rarity_str.strip()
            has_sa = 'SA' in rarity_str.upper() or '성도각성' in rarity_str or 'Stellar Awakened' in rarity_str
            
            nums = re.findall(r'(\d)(?=★)', rarity_str)
            if nums:
                max_star = max(int(n) for n in nums)
                normalized = f"{max_star}★{' SA' if has_sa else ''}".strip()
                is_3_4_star = max_star in [3, 4]
                return normalized, is_3_4_star
            
            return rarity_str, False
        
        # 퍼스널리티 정리 (속성/무기 키워드 제외)
        def clean_personalities(personality_str):
            if not isinstance(personality_str, str) or not personality_str:
                return []
            
            personalities = [p.strip() for p in personality_str.split(',') if p.strip()]
            
            element_keywords = [
                'fire', 'water', 'earth', 'wind', 'light', 'dark', 'crystal', 'thunder', 'shade',
                '땅', '불', '바람', '물', '빛', '어둠', '번개', '크리스탈', '화', '수', '지', '풍'
            ]
            weapon_keywords = [
                'sword', 'katana', 'axe', 'hammer', 'spear', 'bow', 'staff', 'fist', 'lance',
                '검', '도', '도끼', '망치', '창', '활', '지팡이', '주먹', '랜스', '권갑'
            ]
            
            clean_personalities = []
            for personality in personalities:
                personality_lower = personality.lower()
                is_element = any(keyword in personality_lower for keyword in element_keywords)
                is_weapon = any(keyword in personality_lower for keyword in weapon_keywords)
                
                if not is_element and not is_weapon and len(personality) > 1:
                    clean_personalities.append(personality)
            
            return clean_personalities
        
        # 출시일 표준화 함수
        def standardize_release_date(date_str):
            if not date_str or not isinstance(date_str, str):
                return ""
            
            date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
            if date_match:
                year, month, day = date_match.groups()
                return f"{year}/{int(month):02d}/{int(day):02d}"
            return date_str
        
        # 1. 희귀도 정리 (3-4성 여부 확인)
        if 'rarity' in cleaned_data:
            normalized_rarity, is_3_4_star = normalize_rarity_and_check(cleaned_data['rarity'])
            cleaned_data['rarity'] = normalized_rarity
            cleaned_data['is_3_4_star'] = is_3_4_star
        
        # 2. 퍼스널리티 정리
        if 'personality' in cleaned_data:
            clean_pers = clean_personalities(cleaned_data['personality'])
            cleaned_data['personality'] = ', '.join(clean_pers) if clean_pers else ""
            cleaned_data['personality_list'] = clean_pers
        
        # 3. 출시일 표준화
        if 'release_date' in cleaned_data:
            cleaned_data['release_date'] = standardize_release_date(cleaned_data['release_date'])
        
        # 4. 안전한 파일명 생성
        if 'korean_name' in cleaned_data:
            cleaned_data['safe_filename'] = safe_filename(cleaned_data['korean_name'])
        elif 'english_name' in cleaned_data:
            cleaned_data['safe_filename'] = safe_filename(cleaned_data['english_name'])
        else:
            cleaned_data['safe_filename'] = "unknown_character"
        
        # 5. 데이터 검증 및 완성도 확인
        required_fields = ['korean_name', 'english_name', 'element', 'weapon']
        completeness_score = sum(1 for field in required_fields if cleaned_data.get(field))
        cleaned_data['data_completeness'] = completeness_score / len(required_fields)
        
        return cleaned_data

    def scrape_character_details(self, detail_url, eng_name):
        """캐릭터 상세 페이지 스크래핑 (아이콘 포함)"""
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {}
            element_icons = []
            weapon_icons = []
            
            # 다양한 테이블에서 데이터 찾기
            tables = soup.find_all('table')
            
            # 위치 기반 파싱 (레거시 방식) - 완전 복원
            element_icons = []
            element_alts = []  # ALT 텍스트도 저장
            weapon_icons = []
            
            # 메인 캐릭터 정보 테이블 찾기 (anotherTable, wikitable, infobox)
            main_tables = soup.find_all('table', class_=['anotherTable', 'wikitable', 'infobox'])
            print(f"    🔍 {len(main_tables)}개 메인 테이블 발견")
            
            for table_idx, table in enumerate(main_tables):
                rows = table.find_all('tr')
                table_class = table.get('class', ['없음'])
                print(f"      📋 테이블 {table_idx} (class={table_class}): {len(rows)}개 행")
                
                # 각 행을 확인하여 3번째 셀(인덱스 2)에 이미지가 있는 행 처리
                for row_idx, row in enumerate(rows):
                    cells = row.find_all(['th', 'td'])
                    
                    # 3개 이상의 셀이 있는 행에서 3번째 셀 확인
                    if len(cells) >= 3:
                        element_equipment_cell = cells[2]
                        ee_icon_tags = element_equipment_cell.find_all('img')
                        
                        if ee_icon_tags:  # 이미지가 있는 행만 처리
                            print(f"        🎯 테이블 {table_idx}, 행 {row_idx}: 3번째 셀에서 {len(ee_icon_tags)}개 이미지 발견")
                            
                            for img_tag in ee_icon_tags:
                                src = img_tag.get('src', '')
                                alt = img_tag.get('alt', '')
                                
                                if src:
                                    # 레거시 방식: 조건 없이 모든 아이콘 다운로드
                                    icon_path = self.download_icon(src, alt, "elements_equipment")
                                    if icon_path:
                                        # 중복 방지 (레거시 방식: 경로와 ALT를 함께 저장)
                                        if icon_path not in element_icons:
                                            element_icons.append(icon_path)
                                            element_alts.append(alt)  # ALT 텍스트도 함께 저장
                                            print(f"          ✅ 아이콘 추가: {os.path.basename(icon_path)} (ALT: {alt})")
                                        else:
                                            print(f"          🔄 중복 아이콘 스킵: {os.path.basename(icon_path)}")
            
            # 무기 아이콘은 element_icons에서 복사 (레거시 방식)
            weapon_icons = element_icons.copy()
            
            # 레거시 방식: 다운로드된 아이콘을 매핑 테이블로 분류
            classified_elements = []
            classified_element_icons = []
            classified_weapons = []
            classified_weapon_icons = []
            classified_armors = []
            classified_armor_icons = []
            
            print(f"    🔍 {len(element_icons)}개 다운로드된 아이콘 분류 중...")
            
            for i, (icon_path, alt_text) in enumerate(zip(element_icons, element_alts)):
                filename = os.path.basename(icon_path)
                print(f"      🔍 분류 중: {filename} (ALT: {alt_text})")
                
                # 1순위: ALT 텍스트 기반 분류 (레거시 방식)
                if alt_text in ALT_TEXT_MAPPING:
                    category, name = ALT_TEXT_MAPPING[alt_text]
                    if category == "element":
                        classified_elements.append(name)
                        classified_element_icons.append(icon_path)
                        print(f"        ✅ 속성 (ALT): {name}")
                    elif category == "weapon":
                        classified_weapons.append(name)
                        classified_weapon_icons.append(icon_path)
                        print(f"        ⚔️ 무기 (ALT): {name}")
                
                # 2순위: 파일명 기반 분류 (ALT가 매핑에 없는 경우)
                elif filename in ELEMENT_MAPPING:
                    element_name = ELEMENT_MAPPING[filename]
                    classified_elements.append(element_name)
                    classified_element_icons.append(icon_path)
                    print(f"        ✅ 속성 (파일명): {element_name}")
                
                elif filename in WEAPON_MAPPING:
                    weapon_name = WEAPON_MAPPING[filename]
                    classified_weapons.append(weapon_name)
                    classified_weapon_icons.append(icon_path)
                    print(f"        ⚔️ 무기 (파일명): {weapon_name}")
                
                elif filename in ARMOR_MAPPING:
                    armor_name = ARMOR_MAPPING[filename]
                    classified_armors.append(armor_name)
                    classified_armor_icons.append(icon_path)
                    print(f"        🛡️ 방어구 (파일명): {armor_name}")
                    
                else:
                    print(f"        ❓ 미분류: {filename} (ALT: {alt_text})")
                    # 미분류 아이콘은 컨텍스트에 따라 추가 처리
                    if any(keyword in alt_text.lower() for keyword in ['light', 'shadow', 'dark']):
                        # Light/Shadow 관련은 속성으로 분류
                        element_name = alt_text.replace(' Icon.png', '').replace('_', ' ')
                        classified_elements.append(element_name)
                        classified_element_icons.append(icon_path)
                        print(f"        ✅ 속성(추론): {element_name}")
            
            # 분류 결과로 데이터 업데이트
            element_icons = classified_element_icons
            weapon_icons = classified_weapon_icons
            
            # 텍스트 정보도 분류된 결과로 업데이트
            if classified_elements:
                data['elements'] = ', '.join(classified_elements)
            if classified_weapons:
                data['weapons'] = ', '.join(classified_weapons)
            else:
                # 무기가 없으면 기본값
                data['weapons'] = 'Obtain'
            
            # 헤더 기반 텍스트 파싱 (희귀도 등 추가 정보)
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['th', 'td'])
                    if len(cells) < 2:
                        continue
                    
                    # 헤더와 값 분리
                    header_cell = cells[0]
                    value_cell = cells[-1] if len(cells) > 1 else None
                    
                    if not header_cell or not value_cell:
                        continue
                    
                    header_text = header_cell.get_text(strip=True).lower()
                    value_text = value_cell.get_text(strip=True)
                    
                    # 희귀도 찾기
                    if any(keyword in header_text for keyword in ['rarity', '희귀도', 'star', '별']):
                        if '★' in value_text or 'star' in value_text.lower():
                            data['rarity'] = value_text
                        elif 'SA' in value_text.upper() or 'Stellar Awakened' in value_text:
                            data['rarity'] = "5★ SA"
            
            # 기본값 설정
            if 'rarity' not in data or not data['rarity']:
                data['rarity'] = '5★'
            if 'elements' not in data or not data['elements']:
                data['elements'] = 'N/A'
            if 'weapons' not in data or not data['weapons']:
                data['weapons'] = 'Obtain'
            
            # 고화질 이미지 추출 및 다운로드
            img_tag = soup.find('img', class_='thumbimage') or soup.find('img', class_='infobox-image')
            if img_tag:
                img_src = img_tag.get('src', '')
                if img_src.startswith('http'):
                    data['high_res_image_url'] = img_src
                else:
                    data['high_res_image_url'] = urljoin(BASE_URL, img_src)
                
                # 이미지 다운로드
                kor_name = data.get('korean_name', eng_name)
                image_path = self.download_character_image(data['high_res_image_url'], kor_name, eng_name)
                if image_path:
                    data['image_path'] = image_path
            
            # 데이터 정리
            cleaned_data = self.clean_scraped_data(data)
            
            # 아이콘 정보 추가
            cleaned_data['element_icons'] = element_icons
            cleaned_data['weapon_icons'] = weapon_icons
            
            # 디버그 정보 출력
            if cleaned_data:
                print(f"  📊 {eng_name}: 희귀도={cleaned_data.get('rarity', 'N/A')}, 속성={cleaned_data.get('elements', 'N/A')}, 무기={cleaned_data.get('weapons', 'N/A')}")
                if element_icons:
                    print(f"    🎯 속성 아이콘: {len(element_icons)}개")
                if weapon_icons:
                    print(f"    ⚔️ 무기 아이콘: {len(weapon_icons)}개")
                if cleaned_data.get('image_path'):
                    print(f"    🖼️ 이미지: {cleaned_data['image_path']}")
            
            return cleaned_data
            
        except Exception as e:
            print(f"⚠️ {eng_name} 상세 페이지 스크래핑 실패: {e}")
            return {}
    
    def scrape_all_personalities(self):
        """전체 퍼스널리티 데이터 스크래핑"""
        print("🎭 퍼스널리티 데이터 스크래핑 중...")
        try:
            response = requests.get(PERSONALITY_URL, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # wikitable 클래스를 가진 테이블들 찾기
            tables = soup.find_all('table', class_='wikitable')
            character_personalities = {}
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # 퍼스널리티 이름
                        personality_cell = cells[0]
                        personality_eng = personality_cell.get_text(strip=True)
                        personality_kor = self.personality_mapping.get(personality_eng, personality_eng)
                        
                        # 캐릭터 목록
                        characters_cell = cells[1]
                        character_links = characters_cell.find_all('a')
                        characters_found = []
                        
                        for link in character_links:
                            href = link.get('href', '')
                            if (href.startswith('/w/') and 
                                'Character' not in href and 
                                'Personality' not in href and
                                'Special:' not in href and
                                'Category:' not in href):
                                
                                char_name = link.get_text(strip=True)
                                if char_name and len(char_name) > 1:
                                    characters_found.append(char_name)
                        
                        # 각 캐릭터에 퍼스널리티 추가
                        for char_name in characters_found:
                            if char_name not in character_personalities:
                                character_personalities[char_name] = []
                            character_personalities[char_name].append(personality_kor)
            
            print(f"✅ 퍼스널리티 데이터 스크래핑 완료: {len(character_personalities)}명")
            return character_personalities
            
        except Exception as e:
            print(f"❌ 퍼스널리티 데이터 스크래핑 실패: {e}")
            return {}
    
    def create_excel_with_images(self, characters):
        """이미지 포함 엑셀 파일 생성"""
        print("📊 엑셀 파일 생성 중...")
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Characters"
            
            headers = ['English Name', 'Korean Name', 'Rarity', 'Elements', 'Weapons', 'Personalities', 'Image Path']
            ws.append(headers)
            
            for char in characters:
                row = [
                    char.get('english_name', ''),
                    char.get('korean_name', ''),
                    char.get('rarity', ''),
                    char.get('elements', ''),
                    char.get('weapons', ''),
                    char.get('personalities', ''),
                    char.get('image_path', '')
                ]
                ws.append(row)
            
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            excel_path = CSV_DIR / "another_eden_characters_detailed.xlsx"
            wb.save(excel_path)
            print(f"✅ 엑셀 파일 저장 완료: {excel_path}")
            return excel_path
        except Exception as e:
            print(f"❌ 엑셀 파일 생성 실패: {e}")
            return None

    def generate_csv_files(self, characters, personality_data):
        """통일된 CSV 파일들 생성 (퀴즈용 + 룰렛용 + 출시일 포함)"""
        print("📋 통일된 CSV 파일들 생성 중...")
        
        # 1. 퀴즈용 데이터 (출시일 추가)
        quiz_data = []
        for char in characters:
            # 퍼스널리티 정보 가져오기
            base_eng_name = re.sub(r'\s*\(.*\)$', '', char.get('english_name', '')).strip()
            personalities = personality_data.get(base_eng_name, [])
            
            # 퍼스널리티 한글 변환
            korean_personalities = []
            for personality in personalities:
                korean_personality = self.personality_mapping.get(personality, personality)
                korean_personalities.append(korean_personality)
            
            quiz_data.append({
                '캐릭터명': char.get('korean_name', ''),
                'English_Name': char.get('english_name', ''),
                '캐릭터아이콘경로': char.get('image_path', ''),
                '희귀도': char.get('rarity', '5★'),
                '속성명리스트': char.get('elements', ''),
                '무기명리스트': char.get('weapons', 'Obtain'),
                '퍼스널리티리스트': ', '.join(korean_personalities),
                '출시일': char.get('release_date', '')
            })
        
        quiz_df = pd.DataFrame(quiz_data)
        quiz_csv_path = CSV_DIR / "eden_quiz_data.csv"
        quiz_df.to_csv(quiz_csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 퀴즈 데이터 저장: {quiz_csv_path}")

        # 2. 룰렛용 데이터 (아이콘 포함 확장 구조 + 출시일)
        roulette_data = []
        for char in characters:
            # 퍼스널리티 정보 가져오기
            base_eng_name = re.sub(r'\s*\(.*\)$', '', char.get('english_name', '')).strip()
            personalities = personality_data.get(base_eng_name, [])
            
            # 퍼스널리티 한글 변환
            korean_personalities = []
            for personality in personalities:
                korean_personality = self.personality_mapping.get(personality, personality)
                korean_personalities.append(korean_personality)
            
            # 아이콘 경로 생성 (실제 스크래핑된 아이콘 사용)
            element_icons = char.get('element_icons', [])
            weapon_icons = char.get('weapon_icons', [])
            armor_icons = []
            
            # 레거시 방식: 실제 다운로드된 아이콘만 사용 (가상 경로 생성 제거)
            # 가상 경로 생성하지 않음 - 실제 다운로드된 파일만 CSV에 포함
            
            roulette_data.append({
                '캐릭터명': char.get('korean_name', ''),
                'English_Name': char.get('english_name', ''),
                '캐릭터아이콘경로': char.get('image_path', ''),
                '희귀도': char.get('rarity', '5★'),
                '속성명리스트': char.get('elements', ''),
                '속성_아이콘경로리스트': '|'.join(element_icons) if element_icons else '',
                '무기명리스트': char.get('weapons', 'Obtain'),
                '무기_아이콘경로리스트': '|'.join(weapon_icons) if weapon_icons else '',
                '방어구명리스트': '',  # 현재 스크래퍼에서 방어구 정보 없음
                '방어구_아이콘경로리스트': '|'.join(armor_icons) if armor_icons else '',
                '퍼스널리티리스트': ', '.join(korean_personalities),
                '출시일': char.get('release_date', '')
            })
        
        roulette_df = pd.DataFrame(roulette_data)
        roulette_csv_path = CSV_DIR / "eden_roulette_data.csv"
        roulette_df.to_csv(roulette_csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 룰렛 데이터 저장: {roulette_csv_path}")
        
        # 3. 퍼스널리티 전용 CSV (룰렛 앱용)
        personality_data_list = []
        for char in characters:
            base_eng_name = re.sub(r'\s*\(.*\)$', '', char.get('english_name', '')).strip()
            personalities = personality_data.get(base_eng_name, [])
            
            korean_personalities = []
            for personality in personalities:
                korean_personality = self.personality_mapping.get(personality, personality)
                korean_personalities.append(korean_personality)
            
            personality_data_list.append({
                'Korean_Name': char.get('korean_name', ''),
                'English_Name': char.get('english_name', ''),
                'Personalities_List': ', '.join(korean_personalities)
            })
        
        personality_df = pd.DataFrame(personality_data_list)
        personality_csv_path = CSV_DIR / "character_personalities.csv"
        personality_df.to_csv(personality_csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 퍼스널리티 데이터 저장: {personality_csv_path}")

        # 4. 통합 퍼스널리티 데이터 (중복 제거된 버전)
        personality_list = []
        for char_name, personalities in personality_data.items():
            personality_list.append({
                'Character': self.convert_to_korean(char_name),
                'Personalities_Count': len(personalities),
                'Personalities_List': '|'.join(personalities)
            })
        
        personality_summary_df = pd.DataFrame(personality_list)
        personality_summary_df.sort_values('Personalities_Count', ascending=False, inplace=True)
        personality_summary_csv_path = CSV_DIR / "character_personalities_summary.csv"
        personality_summary_df.to_csv(personality_summary_csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 퍼스널리티 요약 데이터 저장: {personality_summary_csv_path}")
        
        return quiz_csv_path, roulette_csv_path, personality_csv_path

    def organize_scraped_images(self, characters):
        """스크래핑된 이미지 자동 정리 (레거시 기능 복원)"""
        from .image_organizer import ImageOrganizer
        
        print("🗂️ 이미지 자동 정리 시작...")
        try:
            organizer = ImageOrganizer(self.project_root)
            
            # 1. 백업 이미지들 복사
            organizer.copy_backup_images()
            
            # 2. CSV 기반 이미지 정리 
            csv_path = CSV_DIR / "eden_quiz_data.csv"
            if csv_path.exists():
                organizer.create_organized_folders(csv_path)
            else:
                print("⚠️ 퀴즈 데이터 CSV가 없어 이미지 정리를 건너뜁니다.")
                
        except Exception as e:
            print(f"⚠️ 이미지 정리 중 오류 발생: {e}")
    
    def run_full_scraping(self):
        """전체 스크래핑 실행 (이미지 정리 포함)"""
        print("🚀 Another Eden 통합 스크래퍼 시작")
        print("=" * 60)
        
        self.load_name_mapping()
        self.load_personality_mapping()
        
        characters = self.scrape_character_list()
        if not characters:
            print("❌ 캐릭터 데이터 없음")
            return False
        
        # 전체 캐릭터 처리 (테스트 완료)
        print("🚀 전체 캐릭터 처리 모드: 372개 캐릭터를 모두 처리합니다.")
        # characters = characters[:10]  # 테스트 모드 비활성화
        
        personality_data = self.scrape_all_personalities()
        
        # 기존 데이터 로드 (중복 체크용)
        existing_data = {}
        quiz_csv_path = CSV_DIR / "eden_quiz_data.csv"
        if quiz_csv_path.exists():
            try:
                existing_df = pd.read_csv(quiz_csv_path, encoding='utf-8-sig')
                for _, row in existing_df.iterrows():
                    existing_data[row['English_Name']] = True
                print(f"📋 기존 데이터 로드: {len(existing_data)}개 캐릭터")
            except Exception as e:
                print(f"⚠️ 기존 데이터 로드 실패: {e}")
        
        # --- Phase 1: Scrape all data ---
        print("\n--- Phase 1: 모든 데이터 스크래핑 ---")
        all_details = []
        print("�� 캐릭터 상세 정보 일괄 스크래핑 중...")
        
        skipped_count = 0
        scraped_count = 0
        
        for i, char in enumerate(characters, 1):
            eng_name = char['english_name']
            
            # 중복 체크 (기존 데이터가 있고 이미지도 존재하면 스킵)
            if eng_name in existing_data:
                # 이미지 파일도 체크
                normalized_name = self.normalize_image_filename(char.get('korean_name', ''), eng_name)
                image_path = IMAGE_DIR / normalized_name
                
                if image_path.exists() and image_path.stat().st_size > 0:
                    print(f"[{i}/{len(characters)}] {eng_name} - 이미 처리됨, 스킵")
                    skipped_count += 1
                    # 기존 데이터 사용
                    existing_char_data = {
                        'english_name': eng_name,
                        'korean_name': char.get('korean_name', ''),
                        'image_path': str(image_path.relative_to(self.project_root).as_posix())
                    }
                    all_details.append(existing_char_data)
                    continue
            
            print(f"[{i}/{len(characters)}] {eng_name} 상세 정보 가져오는 중...")
            details = self.scrape_character_details(char['detail_url'], eng_name)
            all_details.append(details)
            scraped_count += 1
            
            # 진행 상황 출력
            if i % 50 == 0:
                print(f"  📊 진행률: {i}/{len(characters)} ({i/len(characters)*100:.1f}%) - 스킵: {skipped_count}, 스크래핑: {scraped_count}")
            
            time.sleep(0.5)  # 서버 부하 방지를 위해 대기 시간 증가

        # --- Phase 2: Process all data ---
        print("\n--- Phase 2: 모든 데이터 처리 ---")
        processed_characters = []
        for i, char_data in enumerate(characters):
            eng_name = char_data['english_name']
            kor_name = self.convert_to_korean(eng_name)
            details = all_details[i]

            # Get personalities - 스타일 접미사 제거 후 매칭
            base_eng_name = re.sub(r'\s*\(.*\)$', '', eng_name).strip()
            personalities = personality_data.get(base_eng_name, [])
            
            # 퍼스널리티 한글 변환
            korean_personalities = []
            for personality in personalities:
                korean_personality = self.personality_mapping.get(personality, personality)
                korean_personalities.append(korean_personality)

            processed_char = {
                **char_data,
                'korean_name': kor_name,
                'rarity': details.get('rarity', ''),
                'elements': details.get('elements', ''),
                'weapons': details.get('weapons', ''),
                'personalities': ', '.join(korean_personalities),
                'high_res_image_url': details.get('high_res_image_url', ''),
                'image_path': ''  # Initialize path
            }
            processed_characters.append(processed_char)

        # --- Phase 3: Download images ---
        print("\n--- Phase 3: 모든 이미지 다운로드 ---")
        for i, char in enumerate(processed_characters, 1):
            kor_name = char['korean_name']
            eng_name = char['english_name']
            image_url = char.get('high_res_image_url') or char.get('image_url')
            
            print(f"[{i}/{len(processed_characters)}] {kor_name} ({eng_name}) 이미지 다운로드 중...")
            if image_url:
                image_path = self.download_character_image(image_url, kor_name=kor_name, eng_name=eng_name)
                char['image_path'] = image_path or ''
            else:
                print(f"  ❌ 이미지 URL 없음")
        
        # Replace original characters list with the fully processed one
        characters = processed_characters
        
        excel_path = self.create_excel_with_images(characters)
        csv_paths = self.generate_csv_files(characters, personality_data)
        
        # --- Phase 4: 이미지 자동 정리 (레거시 기능 복원) ---
        print("\n--- Phase 4: 이미지 자동 정리 ---")
        self.organize_scraped_images(characters)
        
        print("\n🎉 통합 스크래핑 완료!")
        print("=" * 60)
        print(f"📊 총 캐릭터 수: {len(characters)}")
        if excel_path:
            print(f"💾 엑셀 파일: {excel_path}")
        if csv_paths:
            print(f"💾 CSV 파일들: {', '.join(map(str, csv_paths))}")
        print(f"🗂️ 정리된 이미지: {IMAGE_DIR.parent}/organized_character_art")
        
        return True


def main():
    """메인 실행 함수"""
    scraper = MasterScraper()
    success = scraper.run_full_scraping()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
