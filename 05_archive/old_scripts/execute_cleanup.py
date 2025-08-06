import os
import subprocess
import sys

def execute_cleanup():
    """프로젝트 정리 스크립트를 직접 실행하여 작업을 단순화합니다."""
    script_to_run = "project_cleanup_final.py"
    print(f"🚀 '{script_to_run}' 스크립트를 실행하여 프로젝트 정리를 시작합니다.")

    try:
        # 스크립트 실행 (encoding 지정 없이 바이너리로 읽기)
        result = subprocess.run(
            [sys.executable, script_to_run],
            capture_output=True,
            check=True
        )

        # 인코딩 자동 판별 시도
        for enc in ('utf-8', 'cp949', 'euc-kr'):
            try:
                stdout = result.stdout.decode(enc)
                stderr = result.stderr.decode(enc) if result.stderr else ""
                break
            except Exception:
                continue
        else:
            stdout = result.stdout
            stderr = result.stderr

        print("--- 스크립트 출력 ---")
        print(stdout)
        if stderr:
            print("--- 스크립트 에러 ---")
            print(stderr)
        print("--------------------")
        print("\n✅ 프로젝트 정리가 성공적으로 완료되었습니다.")

    except FileNotFoundError:
        print(f"❌ 오류: '{script_to_run}' 스크립트를 찾을 수 없습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ '{script_to_run}' 실행 중 오류가 발생했습니다.")
        print("--- 스크립트 출력 ---")
        print(e.stdout)
        print("--- 스크립트 에러 ---")
        print(e.stderr)
        print("--------------------")
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    execute_cleanup()