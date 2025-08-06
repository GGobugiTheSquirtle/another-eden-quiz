#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지 경로 매칭 점검 스크립트
"""

import pandas as pd
import os
from pathlib import Path

def check_image_paths():
    """이미지 경로와 파일 존재 여부 점검"""
    
    # CSV 로드
    try:
        df = pd.read_csv('04_data/csv/eden_quiz_data.csv', encoding='utf-8-sig')
    except Exception as e:
        print(f"CSV 로드 실패: {e}")
        return
    
    print('=' * 50)
    print('이미지 경로 매칭 점검')
    print('=' * 50)
    print(f'총 캐릭터 수: {len(df)}')
    print()
    
    # 이미지 경로 확인
    missing_images = []
    existing_images = []
    no_path_images = []
    
    for idx, row in df.head(20).iterrows():  # 처음 20개만 점검
        char_name = row['캐릭터명']
        image_path = row.get('캐릭터아이콘경로', '')
        
        if pd.isna(image_path) or image_path == '':
            print(f'{idx+1:2d}. {char_name:<25}: X 경로 없음')
            no_path_images.append(char_name)
        else:
            # 경로 정규화
            normalized_path = str(image_path).replace('\\\\', '/').replace('\\', '/')
            
            if os.path.exists(normalized_path):
                print(f'{idx+1:2d}. {char_name:<25}: O 존재')
                existing_images.append(char_name)
            else:
                print(f'{idx+1:2d}. {char_name:<25}: X 파일 없음')
                print(f'     경로: {normalized_path}')
                missing_images.append((char_name, normalized_path))
    
    print()
    print('=' * 50)
    print('점검 결과')
    print('=' * 50)
    print(f'O 이미지 존재: {len(existing_images)}개')
    print(f'X 파일 없음: {len(missing_images)}개')
    print(f'! 경로 없음: {len(no_path_images)}개')
    
    if missing_images:
        print('\nX 누락된 이미지:')
        for name, path in missing_images:
            print(f'   - {name}: {path}')
    
    # 실제 icons 폴더 파일 수 확인
    icons_path = Path('04_data/images/character_art/icons')
    if icons_path.exists():
        icon_files = list(icons_path.glob('*.png'))
        print(f'\n폴더 실제 아이콘 파일 수: {len(icon_files)}개')
        
        # 샘플 파일명 표시
        if icon_files:
            print('   샘플 파일들:')
            for file in icon_files[:5]:
                print(f'   - {file.name}')
    
    return existing_images, missing_images, no_path_images

if __name__ == "__main__":
    check_image_paths()