# 🚀 Another Eden 앱 빠른 시작 가이드

## 📋 실행 방법

### 방법 1: 배치 파일 (Windows)
```bash
# 프로젝트 폴더에서 더블클릭
run_app.bat
```

### 방법 2: Python 스크립트
```bash
python run_app.py
```

### 방법 3: 직접 실행
```bash
# 퀴즈 앱
streamlit run 03_apps/quiz/eden_quiz_app.py

# 룰렛 앱  
streamlit run 03_apps/roulette/streamlit_eden_restructure.py
```

## 🔄 전체 파이프라인 (데이터부터 시작)

### 1. 스크래핑
```bash
python 01_scraping/master_scraper.py
```

### 2. 데이터 정리
```bash
python fix_data_issues.py
```

### 3. 앱 실행
```bash
python run_app.py
```

## 📁 프로젝트 구조

```
어나덴퀴즈/
├── 01_scraping/          # 데이터 스크래핑
├── 02_launcher/          # 실행 런처
├── 03_apps/              # 앱 모듈
│   ├── quiz/            # 퀴즈 앱
│   └── roulette/        # 룰렛 앱
├── 04_data/             # 데이터 파일
│   ├── csv/             # CSV 데이터
│   └── images/          # 이미지 데이터
├── run_app.py           # 간단 실행기
├── run_app.bat          # Windows 배치 파일
└── integrated_pipeline.py # 통합 파이프라인
```

## 🎮 앱 기능

### 퀴즈 앱
- 캐릭터 이름 맞추기
- 희귀도 맞추기  
- 속성 맞추기
- 무기 맞추기
- 실루엣 퀴즈

### 룰렛 앱
- 캐릭터 룰렛
- 필터링 기능
- 상세 정보 표시

## 🔧 문제 해결

### 이미지가 안 보이는 경우
```bash
python fix_data_issues.py
```

### 데이터가 없는 경우
```bash
python 01_scraping/master_scraper.py
```

### 앱이 실행되지 않는 경우
```bash
pip install streamlit pandas requests beautifulsoup4
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 3.8+ 설치
2. 필요한 패키지 설치
3. 데이터 파일 존재 여부
4. 이미지 파일 경로 