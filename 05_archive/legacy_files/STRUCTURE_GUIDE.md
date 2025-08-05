# 🏗️ 프로젝트 구조 가이드

## 📁 새로운 모듈화 구조

```
📦 Another Eden Quiz & Roulette
├── 📂 01_scraping/              # 데이터 스크래핑
│   └── master_scraper.py              # 통합 마스터 스크래퍼
├── 📂 02_launcher/              # 실행 런쳐
│   ├── eden_integrated_launcher.py    # Streamlit 통합 런쳐
│   ├── terminal_launcher.py           # 터미널 통합 런쳐
│   ├── run_launcher.bat               # Windows 배치
│   └── run_launcher.ps1               # PowerShell
├── 📂 03_apps/                  # 앱 알맹이
│   ├── 📂 quiz/                 # 퀴즈 앱
│   │   └── eden_quiz_app.py
│   ├── 📂 roulette/             # 룰렛 앱
│   │   └── streamlit_eden_restructure.py
│   └── 📂 shared/               # 공통 모듈
│       └── fix_image_character_matching.py
├── 📂 04_data/                  # 데이터
│   ├── 📂 csv/                  # CSV 데이터
│   │   ├── eden_quiz_data_fixed.csv   # 수정된 퀴즈 데이터
│   │   ├── eden_quiz_data.csv         # 기본 퀴즈 데이터
│   │   ├── eden_roulette_data.csv     # 룰렛 데이터
│   │   ├── eden_roulette_data_with_personalities.csv # 룰렛+성격 데이터
│   │   ├── character_personalities.csv # 성격 데이터
│   │   └── Matching_names.csv          # 이름 매핑
│   └── 📂 images/               # 이미지 데이터
│       └── character_art/              # 캐릭터 이미지
├── 📂 05_archive/               # 아카이브
│   └── 📂 legacy_scrapers/      # 구버전 스크래퍼
├── main_launcher.py             # 🎯 메인 실행기
├── restructure_project.py       # 구조 재정비 스크립트
├── requirements.txt             # 의존성
└── README.md                    # 프로젝트 문서
```

## 🚀 사용법

### 메인 런쳐 사용 (권장)
```bash
# 터미널 런처 실행 (권장)
python 02_launcher/terminal_launcher.py

# 또는 메인 런처 실행
python main_launcher.py
```

### 개별 실행
```bash
# 퀴즈 앱
streamlit run 03_apps/quiz/eden_quiz_app.py

# 룰렛 앱  
streamlit run 03_apps/roulette/streamlit_eden_restructure.py

# 통합 스크래퍼
python 01_scraping/master_scraper.py
```

## 🔧 개발자 노트

- 기존 파일들은 그대로 유지됩니다
- 새로운 구조는 복사본으로 생성됩니다
- 필요시 기존 파일들을 삭제하여 정리할 수 있습니다

## 📋 다음 단계

1. 새로운 구조에서 앱들이 정상 작동하는지 확인
2. 경로 참조 문제가 있다면 수정
3. 기존 파일들 정리 (선택사항)
