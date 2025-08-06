# Another Eden 프로젝트 데이터 구조 분석 및 정리

## 📊 현재 데이터 구조 분석

### 1. CSV 파일 구조 (통일된 구조)

#### 1.1 퀴즈 데이터 (`eden_quiz_data.csv`)
```csv
컬럼 구조:
- 캐릭터명 (한글)
- English_Name (영어 이름)
- 캐릭터아이콘경로 (이미지 파일 경로)
- 희귀도 (5★, 5★ 성도각성 등)
- 속성명리스트 (Fire, Water, Earth, Wind, Light, Dark, Crystal)
- 무기명리스트 (Sword, Katana, Axe, Hammer, Spear, Bow, Staff, Fist)
- 퍼스널리티리스트 (한글 퍼스널리티, 쉼표로 구분)
```

#### 1.2 룰렛 데이터 (`eden_roulette_data.csv`)
```csv
컬럼 구조:
- 캐릭터명 (한글)
- English_Name (영어 이름)
- 캐릭터아이콘경로 (이미지 파일 경로)
- 희귀도 (5★, 5★ 성도각성 등)
- 속성명리스트 (Fire, Water, Earth, Wind, Light, Dark, Crystal)
- 무기명리스트 (Sword, Katana, Axe, Hammer, Spear, Bow, Staff, Fist)
- 퍼스널리티리스트 (한글 퍼스널리티, 쉼표로 구분)
```

#### 1.3 퍼스널리티 데이터 (`character_personalities.csv`)
```csv
컬럼 구조:
- Character (캐릭터명)
- Personalities_Count (퍼스널리티 개수)
- Personalities_List (퍼스널리티 목록, |로 구분)
```

### 2. 매핑 파일 구조

#### 2.1 이름 매칭 (`Matching_names.csv`)
```csv
컬럼 구조:
- 캐릭터명 (입력) (영어 이름)
- 캐릭터명 (매칭) (한글 이름)
```

#### 2.2 퍼스널리티 매칭 (`personality_matching.csv`)
```csv
컬럼 구조:
- English (영어 퍼스널리티)
- Korean (한글 퍼스널리티)
```

### 3. 이미지 파일 구조

#### 3.1 캐릭터 이미지
```
경로: 04_data/images/character_art/
파일명 규칙: {한글_캐릭터명}.png
예시: 레이븐 AS.png, 붉은 소매의 행상인.png
```

#### 3.2 아이콘 이미지
```
경로: 04_data/images/character_art/icons/
경로: 04_data/images/character_art/elements_equipment/
```

## ✅ 해결된 문제점

### 1. 데이터 구조 통일 ✅
- **퀴즈 데이터**: 7개 컬럼 (퍼스널리티리스트 추가)
- **룰렛 데이터**: 7개 컬럼 (동일한 구조)
- **결과**: 완전히 통일된 컬럼 구조

### 2. SA 정보 처리 ✅
- **스크래퍼**: SA → '성도각성' 변환 완료
- **데이터**: 모든 파일에 일관되게 반영
- **결과**: 5★ 성도각성으로 정확히 구분

### 3. 퍼스널리티 정보 통합 ✅
- **영어 퍼스널리티**: 스크래핑으로 수집
- **한글 변환**: personality_matching.csv 기반 변환
- **통합**: 퀴즈/룰렛 데이터에 포함

## 🔧 구현된 개선사항

### 1. 통일된 데이터 생성 함수
```python
def generate_csv_files(self, characters, personality_data):
    """통일된 CSV 파일들 생성"""
    unified_data = []
    for char in characters:
        # 퍼스널리티 정보 가져오기 및 한글 변환
        base_eng_name = re.sub(r'\s*\(.*\)$', '', char.get('english_name', '')).strip()
        personalities = personality_data.get(base_eng_name, [])
        
        korean_personalities = []
        for personality in personalities:
            korean_personality = self.personality_mapping.get(personality, personality)
            korean_personalities.append(korean_personality)
        
        unified_data.append({
            '캐릭터명': char.get('korean_name', ''),
            'English_Name': char.get('english_name', ''),
            '캐릭터아이콘경로': char.get('image_path', ''),
            '희귀도': char.get('rarity', ''),
            '속성명리스트': char.get('elements', ''),
            '무기명리스트': char.get('weapons', ''),
            '퍼스널리티리스트': ', '.join(korean_personalities)
        })
    
    unified_df = pd.DataFrame(unified_data)
    
    # 퀴즈/룰렛 데이터 동일한 구조로 생성
    quiz_csv_path = CSV_DIR / "eden_quiz_data.csv"
    roulette_csv_path = CSV_DIR / "eden_roulette_data.csv"
    
    unified_df.to_csv(quiz_csv_path, index=False, encoding='utf-8-sig')
    unified_df.to_csv(roulette_csv_path, index=False, encoding='utf-8-sig')
```

### 2. 이미지 파일명 정규화
```python
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
```

### 3. SA 정보 처리 로직
```python
def clean_scraped_data(self, data):
    """스크래핑된 데이터 정리 (SA 정보 포함)"""
    # SA 정보 확인
    is_sa = 'SA' in rarity.upper() or 'Stellar Awakened' in rarity or '성도각성' in rarity
    
    # 숫자와 별표 추출
    rarity_match = re.search(r'(\d+)\s*★', rarity)
    if rarity_match:
        star_count = rarity_match.group(1)
        if is_sa:
            cleaned_data['rarity'] = f"{star_count}★ 성도각성"
        else:
            cleaned_data['rarity'] = f"{star_count}★"
```

## 📋 데이터 생성 프로세스

### 1. 스크래핑 단계
1. **캐릭터 목록 수집**: anothereden.wiki에서 372개 캐릭터 정보
2. **상세 정보 스크래핑**: 각 캐릭터의 희귀도, 속성, 무기, SA 정보
3. **퍼스널리티 수집**: 241명의 퍼스널리티 정보
4. **이미지 다운로드**: 고화질 캐릭터 이미지

### 2. 데이터 처리 단계
1. **이름 변환**: 영어 → 한글 매핑
2. **퍼스널리티 변환**: 영어 → 한글 퍼스널리티 변환
3. **SA 정보 처리**: SA → '성도각성' 변환
4. **데이터 정리**: 속성, 무기 정보 정규화

### 3. 파일 생성 단계
1. **통일된 구조**: 퀴즈/룰렛 데이터 동일한 컬럼 구조
2. **퍼스널리티 통합**: 각 캐릭터의 퍼스널리티 정보 포함
3. **파일명 정규화**: 이미지 파일명 특수문자 처리

## 🎯 현재 상태

### ✅ 완료된 작업
- [x] 데이터 구조 통일 (퀴즈/룰렛 동일한 컬럼)
- [x] SA 정보 처리 ('성도각성' 변환)
- [x] 퍼스널리티 정보 통합
- [x] 이미지 파일명 정규화
- [x] 매핑 파일 활용

### 🔄 다음 단계
- [ ] 전체 372개 캐릭터로 확장
- [ ] 무기 정보 수집 개선
- [ ] 앱에서 퍼스널리티 정보 활용
- [ ] 데이터 검증 및 테스트 