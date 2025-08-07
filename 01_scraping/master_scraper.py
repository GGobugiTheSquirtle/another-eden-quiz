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
from openpyxl import Workbook
import traceback
import urllib3
import ssl


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
        
        print("디렉토리 설정 완료")
        print(f"   데이터: {CSV_DIR}")
        print(f"   이미지: {IMAGE_DIR}")
    
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
                print(f"한글 매칭 로드: {len(self.name_mapping)}개")
            except Exception as e:
                print(f"매핑 로드 실패: {e}")
        else:
            print("Matching_names.csv 파일이 없습니다.")
    
    def load_personality_mapping(self):
        """퍼스널리티 매핑 로드"""
        mapping_file = CSV_DIR / "personality_matching.csv"
        if mapping_file.exists():
            try:
                df = pd.read_csv(mapping_file)
                for _, row in df.iterrows():
                    if 'English' in row and 'Korean' in row:
                        self.personality_mapping[row['English']] = row['Korean']
                print(f"퍼스널리티 매핑 로드: {len(self.personality_mapping)}개")
            except Exception as e:
                print(f"퍼스널리티 매핑 로드 실패: {e}")
        else:
            print("personality_matching.csv 파일이 없습니다.")
    
    def convert_to_korean(self, english_name):
        """영어 이름을 한글로 변환 (스타일 접미사 고려)"""
        if not english_name:
            return english_name
        
        # 스타일 접미사 분리
        style_patterns = [
            r'\s+(AS)$', r'\s+(ES)$', r'\s+(NS)$',
            r'\s+(Another\s*Style)$', r'\s+(Extra\s*Style)$',
            r'\s+(Manifestation)$', r'\s+(Alter)$',
        ]
        
        base_name = english_name
        style_suffix = ""
        
        for pattern in style_patterns:
            match = re.search(pattern, english_name, re.IGNORECASE)
            if match:
                style_suffix = " " + match.group(1)
                base_name = english_name[:match.start()]
                break
        
        # 한글 매칭
        korean_base = self.name_mapping.get(base_name.lower(), base_name)
        return korean_base + style_suffix
    
    def sanitize_filename(self, name):
        """파일명으로 안전하게 변환"""
        name = unicodedata.normalize('NFKC', name)
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = name.strip()
        return name
    
    def check_file_exists(self, filepath):
        """파일 존재 여부 확인 (중복 시 None 반환으로 스킵 처리)"""
        if os.path.exists(filepath):
            return None  # 파일이 이미 존재하면 None 반환 (스킵)
        return filepath
        
    def download_image(self, image_url, subfolder="", eng_name="Unknown"):
        """이미지 다운로드 및 저장 (디버깅 및 안정성 강화 버전)"""
        if not image_url:
            print(f"  - {eng_name}: 제공된 이미지 URL이 없어 건너뜁니다.")
            return None
        
        # 다운로드 시도 로그
        print(f"  -> '{eng_name}' 이미지 다운로드 시도...")
        full_image_url = urljoin(BASE_URL, image_url)
        
        try:
            # 1. 파일명 분석 및 확정
            parsed_url = urlparse(full_image_url)
            query_params = parse_qs(parsed_url.query)
            image_name_from_f = query_params.get('f', [None])[0]
            
            if image_name_from_f:
                image_name = os.path.basename(unquote(image_name_from_f))
            else:
                image_name = os.path.basename(unquote(parsed_url.path.split('?')[0]))

            if not image_name or image_name.lower() in ["thumb.php", "index.php"]:
                temp_name = unquote(full_image_url.split('/')[-1].split('?')[0])
                image_name = (temp_name[:50] + ".png") if temp_name else "unknown_image.png"

            base_name, ext = os.path.splitext(image_name)

            # 확장자가 불분명할 경우, HTTP 헤더를 통해 추측
            if not ext or len(ext) > 5:
                try:
                    head_resp = requests.head(full_image_url, timeout=5, allow_redirects=True)
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get('Content-Type')
                    if content_type:
                        guessed_ext = mimetypes.guess_extension(content_type.split(';')[0])
                        if guessed_ext:
                            ext = guessed_ext
                except requests.RequestException:
                    ext = ".png"  # 추측 실패 시 기본 .png로 설정
            
            # 2. 저장 경로 및 파일명 설정
            korean_name = self.convert_to_korean(base_name)
            safe_name = self.sanitize_filename(korean_name) + ext
            
            save_dir = IMAGE_DIR / subfolder if subfolder else IMAGE_DIR
            save_path = save_dir / safe_name
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 중복 파일 체크 (이미 존재하면 스킵)
            if self.check_file_exists(str(save_path)) is None:
                # 파일이 이미 존재하는 경우
                relative_path = save_path.relative_to(PROJECT_ROOT).as_posix()
                print(f"  ⏭️ 파일이 이미 존재하여 스킵: {relative_path}")
                return str(relative_path)
            
            # 3. 실제 다운로드 및 저장
            response = requests.get(full_image_url, headers=self.headers, timeout=30)
            response.raise_for_status()  # 4xx, 5xx 에러 발생 시 예외 처리
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # 4. 성공 처리
            # 프로젝트 루트에서의 상대 경로로 저장 (앱에서 사용하는 형식)
            relative_path = save_path.relative_to(PROJECT_ROOT).as_posix()
            print(f"  ✔ 다운로드 성공: {relative_path}")
            return str(relative_path)
            
        except Exception as e:
            # 5. 실패 처리 (상세 로그 출력)
            print("=" * 20 + " 🚨 다운로드 중 오류 발생! 🚨 " + "=" * 20)
            print(f"  - 캐릭터 이름: {eng_name}")
            print(f"  - 실패한 URL: {full_image_url}")
            print(f"  - 오류 종류: {type(e).__name__}")
            print(f"  - 오류 메시지: {e}")
            print("  - 상세 추적 로그:")
            traceback.print_exc()
            print("=" * 60)
            return None
    
    def download_element_equipment_images(self, char_data):
        """캐릭터의 element와 equipment 이미지들을 다운로드"""
        eng_name = char_data.get('english_name', 'Unknown')
        downloaded_files = {'elements': [], 'equipment': []}
        
        # Element 이미지 다운로드
        for img_data in char_data.get('element_images', []):
            try:
                image_path = self.download_image(
                    img_data['src'], 
                    subfolder="elements_equipment", 
                    eng_name=f"{eng_name}_element_{img_data['alt']}"
                )
                if image_path:
                    downloaded_files['elements'].append(image_path)
            except Exception as e:
                print(f"  ⚠️ Element 이미지 다운로드 실패: {img_data['alt']} - {e}")
        
        # Equipment 이미지 다운로드  
        for img_data in char_data.get('equipment_images', []):
            try:
                image_path = self.download_image(
                    img_data['src'], 
                    subfolder="elements_equipment", 
                    eng_name=f"{eng_name}_equipment_{img_data['alt']}"
                )
                if image_path:
                    downloaded_files['equipment'].append(image_path)
            except Exception as e:
                print(f"  ⚠️ Equipment 이미지 다운로드 실패: {img_data['alt']} - {e}")
        
        return downloaded_files

# ⬇️ 이 코드로 scrape_character_list 함수 전체를 교체해주세요.

    def scrape_character_list(self):
        """캐릭터 목록 페이지 스크래핑 (최종 필터링)"""
        print("캐릭터 목록 스크래핑 중...")
        try:
            response = requests.get(TARGET_URL, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tables = soup.find_all('table', class_='wikitable')
            if not tables:
                print("캐릭터 테이블을 찾을 수 없습니다")
                return []
            
            characters = []
            for table in tables:
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) < 2:
                        continue
                    
                    # 캐릭터 이름은 두 번째 열(cols[1])에서 추출
                    name_col = cols[1] if len(cols) > 1 else cols[0]
                    char_link = name_col.find('a')
                    if not char_link:
                        continue

                    # 이름과 URL 추출
                    href = char_link.get('href', '')
                    eng_name = char_link.get('title', '').strip()
                    
                    # 비-캐릭터 항목 필터링
                    if (not href or not eng_name or
                        href.startswith(('/w/File:', '/w/Category:', '/w/Template:', '/w/Special:')) or
                        eng_name.startswith(('File:', 'Category:', 'Template:'))):
                        continue

                    detail_url = urljoin(BASE_URL, href)
                    
                    # 캐릭터 이미지는 첫 번째 열(cols[0])에서 추출
                    img_url = ''
                    element_images = []
                    equipment_images = []
                    
                    if len(cols) > 0:
                        # 첫 번째 열에서 캐릭터 아이콘 이미지 찾기 (가장 큰 이미지)
                        img_tags = cols[0].find_all('img')
                        for img_tag in img_tags:
                            src = img_tag.get('src', '')
                            alt = img_tag.get('alt', '')
                            # 캐릭터 아이콘은 보통 command.png로 끝나고 width=80
                            if (src and 'command.png' in alt.lower() and 
                                ('width=80' in src or 'rank5' in src or 's2' in src)):
                                img_url = src
                                break
                        
                        # 상대 경로를 절대 경로로 변환
                        if img_url and not img_url.startswith('http'):
                            img_url = urljoin(BASE_URL, img_url)
                    
                    # Element & Equipment 이미지는 세 번째 열(cols[2])에서 추출
                    if len(cols) > 2:
                        element_col = cols[2]
                        img_tags = element_col.find_all('img')
                        
                        for img_tag in img_tags:
                            src = img_tag.get('src', '')
                            alt = img_tag.get('alt', '')
                            
                            if src:
                                # 상대 경로를 절대 경로로 변환
                                if not src.startswith('http'):
                                    src = urljoin(BASE_URL, src)
                                
                                # Element 이미지 (Skill_Type)
                                if 'skill type' in alt.lower() or 'skill_type' in alt.lower():
                                    element_images.append({'src': src, 'alt': alt})
                                # Equipment 이미지 (202*, 216*, Buddy_equipment)
                                elif any(pattern in alt.lower() for pattern in ['icon.png', 'equipment.png']):
                                    equipment_images.append({'src': src, 'alt': alt})
                    
                    characters.append({
                        'english_name': eng_name,
                        'detail_url': detail_url,
                        'image_url': img_url,
                        'korean_name': self.convert_to_korean(eng_name),  # 미리 변환
                        'element_images': element_images,
                        'equipment_images': equipment_images
                    })
            
            print(f"캐릭터 목록 스크래핑 완료: 필터링 후 {len(characters)}개")
            return characters
            
        except Exception as e:
            print(f"캐릭터 목록 스크래핑 실패: {e}")
            return []
        
    def scrape_character_details(self, detail_url, eng_name):
        """캐릭터 상세 페이지 스크래핑"""
        try:
            response = requests.get(detail_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # infobox에서 데이터 추출
            infobox = soup.find('table', class_='infobox')
            if not infobox:
                return {}
            
            data = {}
            rows = infobox.find_all('tr')
            
            for row in rows:
                header = row.find(['th', 'td'])
                if not header:
                    continue
                
                header_text = header.get_text(strip=True)
                if 'Rarity' in header_text or '희귀도' in header_text:
                    rarity_cell = row.find_all(['td', 'th'])[-1]
                    data['rarity'] = rarity_cell.get_text(strip=True)
                elif 'Element' in header_text or '속성' in header_text:
                    element_cell = row.find_all(['td', 'th'])[-1]
                    data['elements'] = element_cell.get_text(strip=True)
                elif 'Weapon' in header_text or '무기' in header_text:
                    weapon_cell = row.find_all(['td', 'th'])[-1]
                    data['weapons'] = weapon_cell.get_text(strip=True)
            
            # 고화질 이미지 추출
            img_tag = infobox.find('img')
            if img_tag:
                img_src = img_tag.get('src', '')
                if img_src.startswith('http'):
                    data['high_res_image_url'] = img_src
                else:
                    data['high_res_image_url'] = urljoin(BASE_URL, img_src)
            
            return data
            
        except Exception as e:
            print(f"{eng_name} 상세 페이지 스크래핑 실패: {e}")
            return {}
    
    def scrape_all_personalities(self):
        """전체 퍼스널리티 데이터 스크래핑"""
        print("퍼스널리티 데이터 스크래핑 중...")
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
            
            print(f"퍼스널리티 데이터 스크래핑 완료: {len(character_personalities)}명")
            return character_personalities
            
        except Exception as e:
            print(f"퍼스널리티 데이터 스크래핑 실패: {e}")
            return {}
    
    def create_excel_with_images(self, characters):
        """이미지 포함 엑셀 파일 생성"""
        print("📊 엑셀 파일 생성 중...")
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Characters"
            
            # 헤더
            headers = ['English Name', 'Korean Name', 'Rarity', 'Elements', 'Weapons', 'Personalities', 'Image Path']
            ws.append(headers)
            
            # 데이터 추가
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
            
            # 열 너비 조정
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # 파일 저장
            excel_path = CSV_DIR / "another_eden_characters_detailed.xlsx"
            wb.save(excel_path)
            print(f"엑셀 파일 저장 완료: {excel_path}")
            return excel_path
            
        except Exception as e:
            print(f"엑셀 파일 생성 실패: {e}")
            return None
    
    def generate_csv_files(self, characters, personality_data):
        """CSV 파일들 생성"""
        print("📋 CSV 파일들 생성 중...")
        
        # 1. 퀴즈용 데이터 (eden_quiz_data.csv)
        quiz_data = []
        for char in characters:
            quiz_data.append({
                '캐릭터명': char.get('korean_name', ''),
                '영문명': char.get('english_name', ''),
                '캐릭터아이콘경로': char.get('image_path', ''),
                '희귀도': char.get('rarity', ''),
                '속성명리스트': char.get('elements', ''),
                '무기명리스트': char.get('weapons', ''),
                '성격특성리스트': char.get('personalities', '')
            })
        
        quiz_df = pd.DataFrame(quiz_data)
        quiz_csv_path = CSV_DIR / "eden_quiz_data.csv"
        quiz_df.to_csv(quiz_csv_path, index=False, encoding='utf-8-sig')
        print(f"퀴즈 데이터 저장: {quiz_csv_path}")
        
        # 2. 룰렛용 데이터 (eden_roulette_data.csv)
        roulette_data = []
        for char in characters:
            roulette_data.append({
                'english_name': char.get('english_name', ''),
                'korean_name': char.get('korean_name', ''),
                'image_path': char.get('image_path', ''),
                'rarity': char.get('rarity', ''),
                'elements': char.get('elements', ''),
                'weapons': char.get('weapons', ''),
                'personalities': char.get('personalities', '')
            })
        
        roulette_df = pd.DataFrame(roulette_data)
        roulette_csv_path = CSV_DIR / "eden_roulette_data.csv"
        roulette_df.to_csv(roulette_csv_path, index=False, encoding='utf-8-sig')
        print(f"룰렛 데이터 저장: {roulette_csv_path}")
        
        # 3. 퍼스널리티 데이터 (character_personalities.csv)
        personality_list = []
        for eng_name, personalities in personality_data.items():
            kor_name = self.name_mapping.get(eng_name.lower(), eng_name)
            personality_list.append({
                'English_Name': eng_name,
                'Korean_Name': kor_name,
                'Personalities_Korean': ', '.join(personalities),
                'Personalities_Count': len(personalities),
                'Personalities_List': '|'.join(personalities)
            })
        
        personality_df = pd.DataFrame(personality_list)
        personality_df.sort_values('Personalities_Count', ascending=False, inplace=True)
        personality_csv_path = CSV_DIR / "character_personalities.csv"
        personality_df.to_csv(personality_csv_path, index=False, encoding='utf-8-sig')
        print(f"퍼스널리티 데이터 저장: {personality_csv_path}")
        
        return quiz_csv_path, roulette_csv_path, personality_csv_path
    
    def save_progress(self, characters, personality_data, suffix=""):
        """진행상황 저장 (중간 저장용)"""
        try:
            print(f"  📋 백업 CSV 파일 생성 중{suffix}...")
            
            # 처리된 캐릭터들만 필터링 (korean_name이 있는 것들)
            processed_chars = [char for char in characters if char.get('korean_name')]
            
            if not processed_chars:
                print("  ⚠️ 처리된 캐릭터가 없어 백업을 건너뜁니다.")
                return
            
            # 백업 CSV 파일들 생성
            quiz_data = []
            for char in processed_chars:
                quiz_data.append({
                    '캐릭터명': char.get('korean_name', ''),
                    '영문명': char.get('english_name', ''),
                    '캐릭터아이콘경로': char.get('image_path', ''),
                    '희귀도': char.get('rarity', ''),
                    '속성명리스트': char.get('elements', ''),
                    '무기명리스트': char.get('weapons', ''),
                    '성격특성리스트': char.get('personalities', '')
                })
            
            quiz_df = pd.DataFrame(quiz_data)
            backup_path = CSV_DIR / f"eden_quiz_data{suffix}.csv"
            quiz_df.to_csv(backup_path, index=False, encoding='utf-8-sig')
            print(f"  ✓ 백업 저장됨: {backup_path}")
            
        except Exception as e:
            print(f"  ⚠️ 백업 저장 실패: {e}")
    
    def run_full_scraping(self, test_mode=False):
        """전체 스크래핑 실행"""
        print("Another Eden 통합 스크래퍼 시작")
        print("=" * 60)
        
        # SSL 인증서 검증 활성화
        print("🔒 SSL/TLS 인증서 검증이 활성화되어 있습니다.")
        
        # 매핑 로드
        self.load_name_mapping()
        self.load_personality_mapping()
        
        # 1. 캐릭터 목록 스크래핑
        characters = self.scrape_character_list()
        if not characters:
            print("캐릭터 데이터 없음")
            return False
        
        # 테스트 모드: 처음 10개만 처리
        if test_mode:
            characters = characters[:10]
            print(f"🧪 테스트 모드: {len(characters)}개 캐릭터만 처리합니다.")
        
        # 2. 퍼스널리티 데이터 스크래핑
        personality_data = self.scrape_all_personalities()
        
        # 3. 각 캐릭터 상세 정보 스크래핑
        print("캐릭터 상세 정보 스크래핑 중...")
        processed_count = 0
        downloaded_count = 0
        skipped_count = 0
        
        try:
            for i, char in enumerate(characters, 1):
                eng_name = char['english_name']
                print(f"[{i}/{len(characters)}] {eng_name} 처리 중...")
                
                try:
                    # 한글명은 이미 목록에서 변환됨
                    if 'korean_name' not in char:
                        char['korean_name'] = self.convert_to_korean(eng_name)
                    
                    # 퍼스널리티 정보 (가장 먼저 처리)
                    personalities = personality_data.get(eng_name, [])
                    char['personalities'] = ', '.join(personalities)
                    
                    # 이미지 다운로드 (메인 리스트에서 가져온 URL 사용)
                    image_url = char.get('image_url', '')
                    image_path = ''
                    
                    if image_url:
                        image_path = self.download_image(image_url, subfolder="", eng_name=eng_name)
                        if image_path:
                            # 스킵된 것인지 새로 다운로드된 것인지는 download_image에서 출력됨
                            if "스킵" in str(image_path) or os.path.exists(PROJECT_ROOT / image_path):
                                downloaded_count += 1  # 기존 파일이든 새 파일이든 성공
                        else:
                            print(f"  ⚠️ 이미지 다운로드 실패: {eng_name}")
                    else:
                        print(f"  ❌ 이미지 URL 없음: {eng_name}")
                    
                    char['image_path'] = image_path or ''
                    
                    # Element & Equipment 이미지 다운로드
                    element_equipment_files = self.download_element_equipment_images(char)
                    element_count = len(element_equipment_files['elements'])
                    equipment_count = len(element_equipment_files['equipment'])
                    
                    if element_count > 0 or equipment_count > 0:
                        print(f"  📦 Element/Equipment: {element_count}개 속성, {equipment_count}개 장비 이미지 다운로드")
                    
                    # 상세 정보는 필요시에만 (희귀도, 속성, 무기가 중요한 경우만)
                    # 현재는 퍼스널리티만 사용하므로 상세 페이지 접근 생략
                    char['rarity'] = ''  # 필요시 상세 페이지에서 가져오기
                    char['elements'] = ''
                    char['weapons'] = ''
                    
                    processed_count += 1
                    
                    # 매 50개마다 중간 저장
                    if processed_count % 50 == 0:
                        print(f"\n💾 중간 저장 중... ({processed_count}개 처리됨)")
                        self.save_progress(characters[:i], personality_data, suffix=f"_backup_{processed_count}")
                    
                    time.sleep(0.5)  # 서버 부하 방지
                    
                except Exception as e:
                    print(f"⚠️ {eng_name} 처리 중 오류 발생: {e}")
                    # 오류가 있어도 기본값으로라도 데이터를 유지
                    char['korean_name'] = self.convert_to_korean(eng_name) if 'korean_name' not in char else char['korean_name']
                    char['rarity'] = char.get('rarity', '')
                    char['elements'] = char.get('elements', '')  
                    char['weapons'] = char.get('weapons', '')
                    char['personalities'] = char.get('personalities', '')
                    char['image_path'] = char.get('image_path', '')
                    continue
                    
        except KeyboardInterrupt:
            print(f"\n\n🛑 사용자에 의해 중단됨! 지금까지 처리된 {processed_count}개 캐릭터 데이터를 저장합니다...")
            # 중단되어도 지금까지의 데이터는 저장
            excel_path = self.create_excel_with_images(characters)
            csv_paths = self.generate_csv_files(characters, personality_data)
            
            print(f"\n✅ 중단 시점 데이터 저장 완료!")
            print(f"처리된 캐릭터: {processed_count}/{len(characters)}")
            if excel_path:
                print(f"엑셀 파일: {excel_path}")
            if csv_paths:
                for csv_path in csv_paths:
                    if os.path.exists(csv_path):
                        print(f"  ✓ {csv_path}")
            return True
        
        # 4. 엑셀 및 CSV 파일 생성
        excel_path = self.create_excel_with_images(characters)
        csv_paths = self.generate_csv_files(characters, personality_data)
        
        print("\n통합 스크래핑 완료!")
        print("=" * 60)
        print(f"총 캐릭터 수: {len(characters)}")
        print(f"성공적으로 처리된 캐릭터: {processed_count}")
        print(f"이미지 처리 성공: {downloaded_count}/{len(characters)} ({downloaded_count/len(characters)*100:.1f}%)")
        if excel_path:
            print(f"엑셀 파일: {excel_path}")
        if csv_paths:
            print(f"CSV 파일들:")
            for csv_path in csv_paths:
                if os.path.exists(csv_path):
                    print(f"  ✓ {csv_path}")
                else:
                    print(f"  ✗ {csv_path} (생성 실패)")
        
        return True


def main(test_mode=False):
    """메인 실행 함수"""
    scraper = MasterScraper()
    success = scraper.run_full_scraping(test_mode=test_mode)
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
