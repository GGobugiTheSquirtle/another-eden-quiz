#!/usr/bin/env python3
"""
캐릭터별 퍼스널리티 데이터 추출
Characters/Personality 페이지에서 실제 캐릭터-퍼스널리티 매핑 데이터 수집
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

# 기본 설정
BASE_URL = "https://anothereden.wiki"
PERSONALITY_URL = "https://anothereden.wiki/w/Characters/Personality"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_personality_mapping():
    """퍼스널리티 매칭 CSV 파일을 로드합니다."""
    personality_mapping = {}
    try:
        personality_csv_path = os.path.join(SCRIPT_DIR, "personality_matching.csv")
        if os.path.exists(personality_csv_path):
            df = pd.read_csv(personality_csv_path)
            for _, row in df.iterrows():
                if 'English' in row and 'Korean' in row:
                    personality_mapping[row['English']] = row['Korean']
        print(f"✅ 퍼스널리티 매핑 로드: {len(personality_mapping)}개")
    except Exception as e:
        print(f"❌ 퍼스널리티 매핑 로드 실패: {e}")
    return personality_mapping

def load_character_name_mapping():
    """캐릭터명 매칭 CSV 파일을 로드합니다."""
    name_mapping = {}
    try:
        matching_csv_path = os.path.join(SCRIPT_DIR, "Matching_names.csv")
        if os.path.exists(matching_csv_path):
            df = pd.read_csv(matching_csv_path, encoding='utf-8-sig')
            for _, row in df.iterrows():
                if len(row) >= 2:
                    eng_name = row.iloc[0]  # 첫 번째 컬럼 (영어명)
                    kor_name = row.iloc[1]  # 두 번째 컬럼 (한국어명)
                    if pd.notna(eng_name) and pd.notna(kor_name):
                        name_mapping[eng_name] = kor_name
        print(f"✅ 캐릭터명 매핑 로드: {len(name_mapping)}개")
    except Exception as e:
        print(f"❌ 캐릭터명 매핑 로드 실패: {e}")
    return name_mapping

def extract_character_personalities():
    """Characters/Personality 페이지에서 캐릭터별 퍼스널리티 데이터 추출"""
    print("🔍 캐릭터별 퍼스널리티 데이터 추출 시작...")
    
    personality_mapping = load_personality_mapping()
    character_name_mapping = load_character_name_mapping()
    character_personalities = {}
    
    headers_ua = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"📡 페이지 요청: {PERSONALITY_URL}")
        response = requests.get(PERSONALITY_URL, headers=headers_ua, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # wikitable 클래스를 가진 테이블들 찾기
        tables = soup.find_all('table', class_='wikitable')
        print(f"📊 발견된 테이블 수: {len(tables)}")
        
        personality_count = 0
        character_total = 0
        
        for table_idx, table in enumerate(tables):
            print(f"\n🔍 테이블 {table_idx + 1} 처리 중...")
            
            rows = table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # 첫 번째 셀: 퍼스널리티 이름
                    personality_cell = cells[0]
                    personality_eng = personality_cell.get_text(strip=True)
                    
                    # 한국어 퍼스널리티명으로 변환
                    personality_kor = personality_mapping.get(personality_eng, personality_eng)
                    
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
                            'Category:' not in href):
                            
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
        
        print(f"\n✅ 수집 완료!")
        print(f"📊 총 퍼스널리티 수: {personality_count}개")
        print(f"🎭 총 캐릭터 수: {len(character_personalities)}명")
        print(f"📈 총 퍼스널리티 연결: {character_total}개")
        
        # 결과 저장
        if character_personalities:
            # 캐릭터별 퍼스널리티 데이터 생성
            character_data = []
            for char_name, personalities in character_personalities.items():
                korean_name = character_name_mapping.get(char_name, char_name)
                character_data.append({
                    'English_Name': char_name,
                    'Korean_Name': korean_name,
                    'Personalities_Korean': ', '.join(personalities),
                    'Personalities_Count': len(personalities),
                    'Personalities_List': '|'.join(personalities)  # 구분자로 |사용
                })
            
            # 정렬 (퍼스널리티 수 기준)
            character_data.sort(key=lambda x: x['Personalities_Count'], reverse=True)
            
            df = pd.DataFrame(character_data)
            output_file = "character_personalities.csv"
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"💾 데이터 저장: {output_file}")
            
            # 상위 20명 출력
            print(f"\n🏆 퍼스널리티가 많은 캐릭터 TOP 20:")
            for i, char in enumerate(character_data[:20]):
                print(f"  {i+1:2d}. {char['Korean_Name']} ({char['English_Name']}): {char['Personalities_Count']}개")
                print(f"      └─ {char['Personalities_Korean']}")
        
        return character_personalities
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return {}

if __name__ == "__main__":
    print("🎮 Another Eden 캐릭터별 퍼스널리티 추출")
    print("=" * 60)
    
    result = extract_character_personalities()
    
    if result:
        print(f"\n🎉 성공! {len(result)}명의 캐릭터 퍼스널리티 데이터 추출 완료")
        print(f"📋 character_personalities.csv 파일을 확인하세요!")
    else:
        print(f"\n❌ 실패")