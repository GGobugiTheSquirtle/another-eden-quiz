# 🎮 Another Eden 퀴즈쇼 (배포용)

원본 캐릭터 이미지를 활용한 Another Eden 캐릭터 퀴즈 앱입니다.

## 📋 기능

- **🏷️ 이름 맞추기**: 캐릭터 이미지를 보고 이름 맞추기 (3-4성 최대)
- **🔥 속성 맞추기**: 캐릭터의 속성 맞추기 (3-4성 최대)
- **⚔️ 무기 맞추기**: 캐릭터의 무기 맞추기 (3-4성 최대)
- **🎭 퍼스널리티 빈칸맞추기**: 퍼스널리티 빈칸 맞추기
- **📅 출시일 순서맞추기**: 캐릭터 출시 순서 맞추기
- **👤 실루엣 퀴즈**: 캐릭터 실루엣 보고 맞추기 (전체 캐릭터)

## 🚀 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

## 📁 파일 구조

```
deployment/
├── app.py              # 메인 앱 파일
├── requirements.txt    # 의존성 목록
├── README.md          # 이 파일
└── data/
    ├── csv/
    │   ├── eden_quiz_data.csv    # 퀴즈 데이터 (자동생성)
    │   ├── Matching_names.csv    # 영어-한글 매칭
    │   └── personality_matching.csv  # 퍼스널리티 매칭
    └── images/            # 원본 캐릭터 이미지 (309개)
        ├── 001_Ruby-Sleeved Merchant_NS.png
        ├── 002_Cyan Scyther_AS.png
        └── ... (기타 캐릭터 이미지)
```

## ☁️ Streamlit Cloud 배포

1. GitHub 리포지토리에 업로드
2. Streamlit Cloud에서 앱 연결
3. `app.py`를 메인 파일로 지정

## 📊 데이터 정보

- **캐릭터 수**: 309명
- **이미지 형식**: PNG (원본 유지)
- **데이터 소스**: Another Eden Wiki
- **파일명 규칙**: `순번_영문이름_스타일.png`

## 🛠️ 최적화 내용

- 원본 이미지 사용 (중복 제거)
- 필수 파일만 포함
- 배포 환경 대응 경로 설정
- Cloud 환경 호환성 확보

## ⚖️ 저작권

- 모든 캐릭터 이미지: © WFS
- 데이터 출처: [Another Eden Wiki](https://anothereden.wiki)
- 앱 코드: MIT License