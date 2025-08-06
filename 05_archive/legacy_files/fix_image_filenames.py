#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 이미지 파일명 정리 스크립트
&width=80 파라미터를 제거하고 파일명을 정리합니다.
"""

import os
import shutil
from pathlib import Path
import re

def fix_image_filenames():
    """이미지 파일명에서 &width=80 파라미터 제거"""
    
    # 프로젝트 루트 설정
    PROJECT_ROOT = Path(__file__).parent.resolve()
    IMAGE_DIR = PROJECT_ROOT / "04_data" / "images" / "character_art"
    
    if not IMAGE_DIR.exists():
        print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {IMAGE_DIR}")
        return
    
    print(f"🔧 이미지 파일명 정리 시작: {IMAGE_DIR}")
    
    # 백업 디렉토리 생성
    backup_dir = IMAGE_DIR.parent / "character_art_backup"
    backup_dir.mkdir(exist_ok=True)
    
    fixed_count = 0
    error_count = 0
    
    for file_path in IMAGE_DIR.iterdir():
        if file_path.is_file():
            old_name = file_path.name
            
            # &width=80 파라미터 제거
            if "&width=80" in old_name:
                new_name = old_name.replace("&width=80", "")
                
                # 파일명 정리 (특수문자 제거)
                new_name = re.sub(r'[<>:"/\\|?*]', '', new_name)
                new_name = new_name.strip()
                
                if new_name != old_name:
                    try:
                        # 백업 생성
                        backup_path = backup_dir / old_name
                        shutil.copy2(file_path, backup_path)
                        
                        # 파일명 변경
                        new_path = file_path.parent / new_name
                        file_path.rename(new_path)
                        
                        print(f"✅ {old_name} → {new_name}")
                        fixed_count += 1
                        
                    except Exception as e:
                        print(f"❌ {old_name} 처리 실패: {e}")
                        error_count += 1
    
    print(f"\n📊 정리 완료:")
    print(f"   ✅ 수정된 파일: {fixed_count}개")
    print(f"   ❌ 오류: {error_count}개")
    print(f"   💾 백업 위치: {backup_dir}")

if __name__ == "__main__":
    fix_image_filenames() 