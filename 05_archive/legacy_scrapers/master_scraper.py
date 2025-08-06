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
        mapping_file = SCRAPING_DIR / "personality_matching.csv"
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
    
    def download_image(self, image_url, subfolder=""):
        """이미지 다운로드 및 저장"""
        if not image_url:
            return None
        
        full_image_url = urljoin(BASE_URL, image_url)
        try:
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
            if not ext or len(ext) > 5:
                try:
                    head_resp = requests.head(full_image_url, timeout=3, allow_redirects=True)
                    head_resp.raise_for_status()
                    content_type = head_resp.headers.get('Content-Type')
                    if content_type:
                        guessed_ext = mimetypes.guess_extension(content_type.split(';')[0])
                        if guessed_ext:
                            ext = guessed_ext
                except:
                    ext = ".png"
            
            # 한글 이름으로 변환
            korean_name = self.convert_to_korean(base_name)
            safe_name = self.sanitize_filename(korean_name) + ext
            
            # 저장 경로 결정
            save_dir = IMAGE_DIR / subfolder if subfolder else IMAGE_DIR
            save_path = save_dir / safe_name
            save_path = Path(self.get_unique_filename(str(save_path)))
            
            # 디렉토리 생성
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 다운로드
            response = requests.get(full_image_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # 상대 경로 반환
            relative_path = save_path.relative_to(DATA_DIR).as_posix()
            return str(relative_path)
            
        except Exception as e:
            print(f"⚠️ 이미지 다운로드 실패 {full_image_url}: {e}")
            return None
    
    def scrape_character_list(self):
        """캐릭터 목록 페이지 스크래핑"""
        print("📡 캐릭터 목록 스크래핑 중...")
        try:
            response = requests.get(TARGET_URL, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 테이블 찾기
            tables = soup.find_all('table', class_='wikitable')
            if not tables:
                print("❌ 캐릭터 테이블을 찾을 수 없습니다")
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
                    detail_url = urljoin(BASE_URL, char_link.get('href', ''))
                    
                    if not eng_name or not detail_url:
                        continue
                    
                    # 이미지 URL 추출
                    img_tag = cols[1].find('img')
                    img_url = img_tag.get('src', '') if img_tag else ''
                    
                    characters.append({
                        'english_name': eng_name,
                        'detail_url': detail_url,
                        'image_url': img_url
                    })
            
            print(f"✅ 캐릭터 목록 스크래핑 완료: {len(characters)}개")
            return characters
            
        except Exception as e:
            print(f"❌ 캐릭터 목록 스크래핑 실패: {e}")
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
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # 파일 저장
            excel_path = CSV_DIR / "another_eden_characters_detailed.xlsx"
            wb.save(excel_path)
            print(f"✅ 엑셀 파일 저장 완료: {excel_path}")
            return excel_path
            
        except Exception as e:
            print(f"❌ 엑셀 파일 생성 실패: {e}")
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
        print(f"✅ 퀴즈 데이터 저장: {quiz_csv_path}")
        
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
        print(f"✅ 룰렛 데이터 저장: {roulette_csv_path}")
        
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
        print(f"✅ 퍼스널리티 데이터 저장: {personality_csv_path}")
        
        return quiz_csv_path, roulette_csv_path, personality_csv_path
    
    def run_full_scraping(self):
        """전체 스크래핑 실행"""
        print("🚀 Another Eden 통합 스크래퍼 시작")
        print("=" * 60)
        
        # 매핑 로드
        self.load_name_mapping()
        self.load_personality_mapping()
        
        # 1. 캐릭터 목록 스크래핑
        characters = self.scrape_character_list()
        if not characters:
            print("❌ 캐릭터 데이터 없음")
            return False
        
        # 2. 퍼스널리티 데이터 스크래핑
        personality_data = self.scrape_all_personalities()
        
        # 3. 각 캐릭터 상세 정보 스크래핑
        print("📄 캐릭터 상세 정보 스크래핑 중...")
        for i, char in enumerate(characters, 1):
            eng_name = char['english_name']
            print(f"[{i}/{len(characters)}] {eng_name} 처리 중...")
            
            # 한글명 변환
            kor_name = self.convert_to_korean(eng_name)
            char['korean_name'] = kor_name
            
            # 상세 정보 스크래핑
            details = self.scrape_character_details(char['detail_url'], eng_name)
            
            # 희귀도, 속성, 무기 정보
            char['rarity'] = details.get('rarity', '')
            char['elements'] = details.get('elements', '')
            char['weapons'] = details.get('weapons', '')
            
            # 퍼스널리티 정보
            personalities = personality_data.get(eng_name, [])
            char['personalities'] = ', '.join(personalities)
            
            # 이미지 다운로드
            image_url = details.get('high_res_image_url') or char['image_url']
            if image_url:
                image_path = self.download_image(image_url)
                char['image_path'] = image_path or ''
            else:
                char['image_path'] = ''
            
            time.sleep(0.5)  # 서버 부하 방지
        
        # 4. 엑셀 및 CSV 파일 생성
        excel_path = self.create_excel_with_images(characters)
        csv_paths = self.generate_csv_files(characters, personality_data)
        
        print("\n🎉 통합 스크래핑 완료!")
        print("=" * 60)
        print(f"📊 총 캐릭터 수: {len(characters)}")
        if excel_path:
            print(f"💾 엑셀 파일: {excel_path}")
        print(f"💾 CSV 파일들: {', '.join(map(str, csv_paths))}")
        
        return True


def main():
    """메인 실행 함수"""
    scraper = MasterScraper()
    success = scraper.run_full_scraping()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
