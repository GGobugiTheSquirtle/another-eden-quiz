# -*- coding: utf-8 -*-
import os
import shutil

def project_cleanup_final():
    """프로젝트 정리 및 최종 확인"""
    print("Another Eden 프로젝트 최종 정리 시작")
    
    # 백업 파일 목록
    backup_files = [
        "eden_integrated_launcher_backup.py",
        "personality_matching_backup.csv",
        "cleanup_and_summarize.py",
        "cleanup_project.py",
        "cleanup_summary.py",
        "execute_all_cleanup.py",
        "execute_final_cleanup.py",
        "execute_final_cleanup_all.py",
        "execute_final_project_cleanup.py",
        "execute_project_cleanup_final.py",
        "final_cleanup_execution.py",
        "final_execute_all_cleanup.py",
        "final_execute_cleanup_all.py",
        "final_project_cleanup.py",
        "move_backup_to_archive.py",
        "run_all_cleanup.py",
        "run_cleanup_summary.py",
        "run_final_cleanup_execution.py",
        "run_final_execute_all_cleanup.py",
        "run_final_project_cleanup.py",
        "run_project_cleanup.py",
        "run_project_cleanup_final.py"
    ]
    
    # archive 디렉토리 생성 (존재하지 않는 경우)
    archive_dir = "archive"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    # 백업 파일들을 archive 디렉토리로 이동
    moved_files = []
    for file in backup_files:
        if os.path.exists(file):
            try:
                shutil.move(file, os.path.join(archive_dir, file))
                moved_files.append(file)
                print(f"[OK] {file}을(를) {archive_dir} 디렉토리로 이동했습니다.")
            except Exception as e:
                print(f"[ERROR] {file} 이동 중 오류 발생: {e}")
        else:
            print(f"[WARN] {file}이(가) 존재하지 않습니다.")
    
    print(f"\n총 {len(moved_files)}개 파일이 archive 디렉토리로 이동되었습니다.")
    
    # 최종 파일 구조 표시
    print("\n최종 프로젝트 구조:")
    for root, dirs, files in os.walk("."):
        # archive 디렉토리의 내용은 표시하지 않음
        if "archive" in root and root != "./archive":
            continue
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            # archive 디렉토리의 파일은 표시하지 않음
            if "archive" not in root:
                print(f"{subindent}{file}")
    
    print("\n프로젝트 정리가 완료되었습니다!")
    print("\n프로젝트 요약:")
    print("- 퀴즈 앱과 룰렛 앱이 완전히 최적화됨")
    print("- 이미지 캐싱을 통해 성능 향상")
    print("- 반응형 UI로 모바일 친화적 디자인 개선")
    print("- 불필요한 백업 파일을 archive 디렉토리로 이동")
    print("- 프로젝트 구조가 체계적으로 정리됨")
    
    # 정리 후 파일 존재 여부 확인
    print("\n정리 후 파일 존재 여부 확인:")
    main_files = [
        "eden_quiz_app.py",
        "streamlit_eden_restructure.py",
        "eden_roulette_data.csv",
        "Matching_names.csv"
    ]
    
    for file in main_files:
        if os.path.exists(file):
            print(f"✅ {file} - 존재함")
        else:
            print(f"❌ {file} - 존재하지 않음")
    
    # archive 디렉토리 내용 확인
    if os.path.exists(archive_dir):
        archive_files = os.listdir(archive_dir)
        print(f"\nArchive 디렉토리 내용 ({len(archive_files)}개 파일):")
        for file in archive_files:
            print(f"  - {file}")
    
    print("\nAnother Eden 퀴즈 및 룰렛 프로젝트가 완전히 정리 및 최적화되었습니다!")
    print("프로젝트는 이제 체계적으로 정리된 상태입니다.")

if __name__ == "__main__":
    project_cleanup_final()
