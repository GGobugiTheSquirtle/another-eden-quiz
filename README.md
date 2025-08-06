<<<<<<< HEAD
# 🎮 Another Eden 캐릭터 앱

Another Eden 캐릭터들을 위한 퀴즈와 룰렛 앱입니다.

## 🚀 기능

### 🎲 캐릭터 룰렛
- 캐릭터 랜덤 뽑기
- 속성, 무기, 희귀도별 필터링
- 슬롯머신 애니메이션
- 캐릭터 상세 정보 표시

### 🎮 캐릭터 퀴즈
- 다양한 퀴즈 유형 (이름, 속성, 무기, 퍼스널리티)
- 실루엣 퀴즈
- 점수 시스템 및 통계
- 틀린 문제 복습 기능

## 📊 데이터

- **366명**의 캐릭터 정보
- **퍼스널리티 데이터** 포함
- **한글/영문 매핑** 지원
- **실시간 업데이트**

## 🛠️ 기술 스택

- **Streamlit** - 웹 애플리케이션 프레임워크
- **Pandas** - 데이터 처리
- **BeautifulSoup** - 웹 스크래핑
- **OpenPyXL** - Excel 파일 처리

## 🚀 배포

이 앱은 Streamlit Cloud에서 배포됩니다.

### 로컬 실행

```bash
# 의존성 설치
=======
# 🚀 Another Eden Quiz & Roulette App

Welcome to the Another Eden Character Quiz & Roulette application!

## ✨ Features

- **🎯 캐릭터 퀴즈**: Test your knowledge with 6 different quiz modes
  - 🏷️ Name Quiz (3-4★ max)
  - 🔥 Element Quiz (3-4★ max)  
  - ⚔️ Weapon Quiz (3-4★ max)
  - 🎭 Personality Fill-in-the-blank (NEW!)
  - 📅 Release Date Ordering (NEW!)
  - 👤 Silhouette Quiz (All Characters)

- **🎰 캐릭터 룰렛**: Random character selection with advanced filtering
  - Advanced filtering by rarity, element, weapon
  - Visual roulette animation
  - Character personality matching

- **📡 데이터 스크래퍼**: Automated data collection from Another Eden Wiki
  - Character information scraping
  - Image downloading and organization
  - CSV data generation

## 🚀 Quick Start

### Main App (Recommended)
```bash
streamlit run app.py
```

### Individual Apps
```bash
# Quiz App
streamlit run 03_apps/quiz/eden_quiz_app.py

# Roulette App  
streamlit run 03_apps/roulette/streamlit_eden_restructure.py

# Unified Launcher
streamlit run 02_launcher/unified_launcher.py
```

## 📦 Installation

```bash
>>>>>>> 51a6804ef3bd3f3fa2c256192c03c12cd0142417
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

<<<<<<< HEAD
## 📁 프로젝트 구조

```
Another_Eden_Quiz/
├── app.py                          # 메인 앱 (배포용)
├── requirements.txt                 # 의존성
├── .streamlit/config.toml          # Streamlit 설정
├── 03_apps/
│   ├── quiz/                       # 퀴즈 앱
│   └── roulette/                   # 룰렛 앱
├── 04_data/
│   ├── csv/                        # 데이터 파일
│   └── images/                     # 이미지 파일
└── create_complete_unified_data.py # 데이터 생성기
```

## 📈 데이터 통계

- **캐릭터 수**: 366명
- **5성 캐릭터**: 301명
- **4성 캐릭터**: 40명
- **3성 캐릭터**: 25명
- **퍼스널리티 포함**: 241명

## 🎯 사용법

1. **메인 페이지**에서 원하는 앱 선택
2. **룰렛**: 필터를 설정하고 룰렛을 돌려보세요
3. **퀴즈**: 다양한 퀴즈를 풀어 캐릭터에 대해 알아보세요

## 📝 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.
데이터는 Another Eden Wiki에서 제공됩니다.

## 🔄 업데이트

데이터는 정기적으로 업데이트됩니다:
- 새로운 캐릭터 추가
- 퍼스널리티 정보 업데이트
- 이미지 및 정보 개선

---

**🎮 Another Eden 캐릭터 앱 v1.0**
=======
## ☁️ Cloud Deployment

This app is optimized for Cloud Streamlit deployment:

- **File Upload Support**: Upload CSV files directly in the app
- **Path Validation**: Robust file path handling for cloud environments
- **Error Handling**: Comprehensive error messages and debugging info
- **Caching**: Optimized data loading with `@st.cache_data`

### For Cloud Deployment:
1. Upload your CSV files using the "📤 CSV 파일 업로드" feature
2. Or run the scraper locally and upload the generated files
3. All features work seamlessly in cloud environments

## 🔧 Development

### Data Structure
- **Quiz Data**: `04_data/csv/eden_quiz_data.csv`
- **Roulette Data**: `04_data/csv/eden_roulette_data.csv`
- **Personality Data**: `04_data/csv/character_personalities.csv`
- **Images**: `04_data/images/character_art/`

### Scraper
```bash
python 01_scraping/master_scraper.py
```

## 📊 Data Sources

- Character information from [Another Eden Wiki](https://anothereden.wiki)
- Personality data from official sources
- Images and icons from game assets

## 🤝 Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the UI/UX
- Adding new quiz modes

## 📄 License

This project is licensed under the MIT License.
>>>>>>> 51a6804ef3bd3f3fa2c256192c03c12cd0142417
