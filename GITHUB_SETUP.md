
🐙 GitHub 리포지토리 생성 안내
================================

1. GitHub에서 새 리포지토리 생성:
   - 리포지토리 이름: another-eden-quiz
   - 설명: Interactive quiz games and character roulette for Another Eden
   - Public/Private: 원하는 설정 선택
   - README, .gitignore, license: 생성하지 않음 (이미 존재)

2. 생성 후 다음 명령어로 연결:
   
   git remote add origin https://github.com/[사용자명]/another-eden-quiz.git
   git branch -M main
   git push -u origin main

3. Streamlit Community Cloud 배포:
   - https://share.streamlit.io/ 방문
   - GitHub 리포지토리 연결
   - 앱 파일 선택:
     * eden_integrated_launcher.py (메인 런처)
     * eden_quiz_app.py (퀴즈 앱)
     * streamlit_eden_restructure.py (룰렛 앱)

4. 필요한 경우 다음 파일들을 리포지토리에 추가:
   - Matching_names.csv (캐릭터명 매핑)
   - character_art/ 폴더 (이미지 파일들)
   - audio/ 폴더 (사운드 파일들)

⚠️  주의사항:
- 큰 이미지/오디오 파일들은 Git LFS 사용 고려
- 민감한 데이터가 있는지 .gitignore 확인
- 첫 번째 배포 시 데이터 파일 부족으로 에러 날 수 있음
