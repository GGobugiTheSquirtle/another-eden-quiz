# Another Eden 퀴즈 & 룰렛 프로젝트 - 최종 구조

## 🎯 프로젝트 개요

Another Eden 캐릭터 정보를 기반으로 한 퀴즈 앱과 룰렛 앱을 제공하는 통합 프로젝트입니다.

## 📁 프로젝트 구조

```
Another_Eden_Quiz/
├── 📁 01_scraping/                    # 데이터 수집 모듈
│   ├── master_scraper.py              # 통합 마스터 스크래퍼
│   ├── gui_scraper.py                 # GUI 스크래퍼
│   └── scraper_config.ini             # 스크래퍼 설정
│
├── 📁 02_launcher/                    # 실행 런처 모듈
│   ├── terminal_launcher.py           # 터미널 통합 런처
│   ├── gui_launcher.py                # GUI 런처
│   ├── gui_main_launcher.py           # 메인 GUI 런처
│   ├── eden_integrated_launcher.py    # Streamlit 통합 런처
│   ├── quick_start.bat                # 빠른 시작 배치 파일
│   ├── run_launcher.bat               # 런처 실행 배치 파일
│   └── run_launcher.ps1               # PowerShell 런처 스크립트
│
├── 📁 03_apps/                        # 앱 모듈
│   ├── 📁 quiz/                       # 퀴즈 앱
│   │   └── eden_quiz_app.py           # 메인 퀴즈 앱
│   ├── 📁 roulette/                   # 룰렛 앱
│   │   └── streamlit_eden_restructure.py  # 메인 룰렛 앱
│   └── 📁 shared/                     # 공유 유틸리티
│       ├── batch_rename_images.py     # 이미지 일괄 이름 변경
│       ├── fix_image_character_matching.py  # 이미지-캐릭터 매칭 수정
│       ├── rename_images_to_korean.py # 이미지를 한글명으로 변경
│       └── unified_image_matching.py  # 통합 이미지 매칭
│
├── 📁 04_data/                        # 데이터 모듈
│   ├── 📁 csv/                        # CSV 데이터 파일
│   │   ├── another_eden_characters_detailed.xlsx  # 상세 캐릭터 정보
│   │   ├── eden_quiz_data.csv         # 퀴즈용 데이터
│   │   ├── eden_quiz_data_fixed.csv   # 퀴즈용 데이터 (고정)
│   │   ├── eden_roulette_data.csv     # 룰렛용 데이터
│   │   ├── character_personalities.csv # 퍼스널리티 데이터
│   │   ├── Matching_names.csv         # 이름 매칭 데이터
│   │   └── personality_matching.csv   # 퍼스널리티 매칭 데이터
│   ├── 📁 images/                     # 이미지 데이터
│   │   └── 📁 character_art/          # 캐릭터 이미지
│   │       ├── 📁 elements_equipment/ # 속성/장비 아이콘
│   │       └── 📁 icons/              # 아이콘 이미지
│   └── quiz_stats.json                # 퀴즈 통계 데이터
│
├── 📁 05_archive/                     # 아카이브 모듈
│   ├── 📁 backup/                     # 백업 파일들
│   ├── 📁 legacy_files/               # 레거시 파일들
│   ├── 📁 legacy_scrapers/            # 구버전 스크래퍼들
│   ├── 📁 old_scripts/                # 구버전 스크립트들
│   └── 📁 old_versions/               # 구버전 파일들
│
├── 📁 docs/                           # 문서 모듈
│   └── project_summary.json           # 프로젝트 요약
│
├── 📁 .streamlit/                     # Streamlit 설정
├── 📁 .github/                        # GitHub 설정
├── 📁 audio/                          # 오디오 파일
│
├── main_launcher.py                   # 메인 런처 (진입점)
├── requirements.txt                   # Python 의존성
├── README.md                          # 프로젝트 설명서
├── QUICK_START.md                     # 빠른 시작 가이드
├── STRUCTURE_GUIDE.md                 # 구조 가이드
├── DATA_STRUCTURE_ANALYSIS.md         # 데이터 구조 분석
├── FINAL_PROJECT_STRUCTURE.md         # 최종 프로젝트 구조 (이 파일)
├── GITHUB_SETUP.md                    # GitHub 설정 가이드
├── DEPLOYMENT.md                      # 배포 가이드
├── LICENSE                            # 라이선스
├── run_app.bat                        # 앱 실행 배치 파일
└── run_app.py                         # 앱 실행 Python 스크립트
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# Python 의존성 설치
pip install -r requirements.txt
```

### 2. 메인 런처 실행
```bash
# 메인 런처 실행
python main_launcher.py
```

### 3. 직접 앱 실행
```bash
# 퀴즈 앱 실행
streamlit run 03_apps/quiz/eden_quiz_app.py

# 룰렛 앱 실행
streamlit run 03_apps/roulette/streamlit_eden_restructure.py

# 스크래퍼 실행
python 01_scraping/master_scraper.py
```

## 📊 데이터 구조

### 통일된 CSV 구조
모든 데이터 파일은 다음 7개 컬럼을 가집니다:

```csv
- 캐릭터명 (한글)
- English_Name (영어 이름)
- 캐릭터아이콘경로 (이미지 파일 경로)
- 희귀도 (5★, 5★ 성도각성 등)
- 속성명리스트 (Fire, Water, Earth, Wind, Light, Dark, Crystal)
- 무기명리스트 (Sword, Katana, Axe, Hammer, Spear, Bow, Staff, Fist)
- 퍼스널리티리스트 (한글 퍼스널리티, 쉼표로 구분)
```

## 🎮 앱 기능

### 퀴즈 앱 (`03_apps/quiz/eden_quiz_app.py`)
- **캐릭터 이름 맞추기**: 이미지로 캐릭터 이름 추측
- **속성 맞추기**: 캐릭터의 속성 추측
- **희귀도 맞추기**: 캐릭터의 희귀도 추측 (SA 포함)
- **무기 맞추기**: 캐릭터의 무기 추측
- **실루엣 퀴즈**: 실루엣으로 캐릭터 추측
- **타이머 기능**: 시간 제한 퀴즈
- **힌트 시스템**: 50:50 힌트 제공
- **통계 추적**: 점수, 정답률, 콤보 기록

### 룰렛 앱 (`03_apps/roulette/streamlit_eden_restructure.py`)
- **필터링**: 희귀도, 속성, 무기별 필터링
- **검색**: 이름/성격 검색
- **룰렛**: 필터링된 캐릭터 중 랜덤 선택
- **슬롯머신**: 애니메이션 효과
- **캐릭터 카드**: 상세 정보 표시

## 🔧 개발 도구

### 스크래퍼 (`01_scraping/master_scraper.py`)
- **캐릭터 정보 수집**: anothereden.wiki에서 372개 캐릭터
- **상세 정보 스크래핑**: 희귀도, 속성, 무기, SA 정보
- **퍼스널리티 수집**: 241명의 퍼스널리티 정보
- **이미지 다운로드**: 고화질 캐릭터 이미지
- **데이터 변환**: 영어→한글 매핑, SA→성도각성 변환

### 런처 (`02_launcher/`)
- **터미널 런처**: 명령줄 기반 통합 실행
- **GUI 런처**: 그래픽 인터페이스 기반 실행
- **Streamlit 런처**: 웹 기반 통합 실행

## 📋 주요 개선사항

### ✅ 완료된 작업
- [x] **데이터 구조 통일**: 퀴즈/룰렛 데이터 동일한 컬럼 구조
- [x] **SA 정보 처리**: SA → '성도각성' 정확한 변환
- [x] **퍼스널리티 정보 통합**: 영어→한글 퍼스널리티 변환
- [x] **이미지 파일명 정규화**: 특수문자 처리 및 일관된 명명
- [x] **UI/UX 개선**: 모바일 반응형, 버튼 크기 최적화
- [x] **매핑 파일 활용**: 이름/퍼스널리티 변환 시스템
- [x] **불필요한 파일 아카이브화**: 레거시 파일 정리

### 🔄 다음 단계
- [ ] 전체 372개 캐릭터로 확장
- [ ] 무기 정보 수집 개선
- [ ] 앱에서 퍼스널리티 정보 활용
- [ ] 데이터 검증 및 테스트

## 🛠️ 기술 스택

- **Python**: 3.8+
- **Streamlit**: 웹 앱 프레임워크
- **Pandas**: 데이터 처리
- **BeautifulSoup**: 웹 스크래핑
- **Requests**: HTTP 요청
- **Pillow**: 이미지 처리

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다!

---

**프로젝트 상태**: ✅ 완료 (정리 완료)
**마지막 업데이트**: 2025-08-05
**버전**: 1.0.0 