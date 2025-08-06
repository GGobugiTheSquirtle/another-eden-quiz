#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗂️ 이미지 자동 정리 시스템 (Legacy 기능 복원)
레거시 스크래퍼의 이미지 정리 기능을 복원하여 사용자 편의성을 향상시킵니다.
"""

import os
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

class ImageOrganizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "04_data"
        self.images_dir = self.data_dir / "images" / "character_art"
        self.csv_dir = self.data_dir / "csv"
        
    def create_organized_folders(self, csv_file_path=None):
        """
        레거시 스크래퍼의 이미지 정리 기능 복원
        1. 출시일 순 정리 (1. 출시일 순)
        2. 가나다 순 정리 (2. 가나다 순)
        """
        print("🗂️ 이미지 자동 정리 시작...")
        
        # CSV 파일 로드 (출시일 데이터 포함)
        if not csv_file_path:
            csv_file_path = self.csv_dir / "eden_quiz_data.csv"
        
        if not csv_file_path.exists():
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return False
            
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            print(f"✅ CSV 데이터 로드: {len(df)}개 캐릭터")
        except Exception as e:
            print(f"❌ CSV 파일 로드 실패: {e}")
            return False
        
        # 필요한 컬럼 확인
        required_columns = ['캐릭터명', '캐릭터아이콘경로', '출시일']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️ 필요한 컬럼이 없습니다: {missing_columns}")
            # 출시일이 없는 경우에도 가나다순 정리는 수행
            if '출시일' in missing_columns:
                print("ℹ️ 출시일 데이터가 없어 가나다순 정리만 수행합니다.")
        
        # 정리된 폴더 생성
        organized_base = self.images_dir.parent / "organized_character_art"
        organized_base.mkdir(exist_ok=True)
        
        # 1. 출시일 순 정리
        if '출시일' in df.columns:
            self._organize_by_release_date(df, organized_base)
        
        # 2. 가나다 순 정리
        self._organize_by_alphabetical(df, organized_base)
        
        print("✅ 이미지 자동 정리 완료!")
        return True
    
    def _organize_by_release_date(self, df, base_dir):
        """출시일 순으로 이미지 정리"""
        print("📅 출시일 순 정리 중...")
        
        release_date_dir = base_dir / "1. 출시일 순"
        release_date_dir.mkdir(exist_ok=True)
        
        # 출시일로 정렬 (빈 값은 맨 뒤로)
        df_sorted = df.copy()
        df_sorted['출시일_정렬키'] = df_sorted['출시일'].fillna('9999/12/31')
        df_sorted = df_sorted.sort_values('출시일_정렬키')
        
        copied_count = 0
        for idx, row in df_sorted.iterrows():
            char_name = str(row['캐릭터명']).strip()
            image_path = str(row.get('캐릭터아이콘경로', '')).strip()
            release_date = str(row.get('출시일', '')).strip()
            
            if not char_name or not image_path:
                continue
                
            # 원본 이미지 파일 찾기
            source_file = self._find_source_image(image_path, char_name)
            if not source_file:
                continue
            
            # 파일명 생성 (출시일_캐릭터명)
            file_extension = source_file.suffix
            if release_date and release_date != 'nan':
                # 날짜 형식 정규화
                formatted_date = self._format_date_for_filename(release_date)
                safe_filename = f"{formatted_date}_{self._safe_filename(char_name)}{file_extension}"
            else:
                safe_filename = f"9999-12-31_{self._safe_filename(char_name)}{file_extension}"
            
            dest_file = release_date_dir / safe_filename
            
            # 파일 복사
            try:
                shutil.copy2(source_file, dest_file)
                copied_count += 1
            except Exception as e:
                print(f"⚠️ 파일 복사 실패 ({char_name}): {e}")
        
        print(f"✅ 출시일 순 정리 완료: {copied_count}개 파일")
    
    def _organize_by_alphabetical(self, df, base_dir):
        """가나다 순으로 이미지 정리"""
        print("🔤 가나다 순 정리 중...")
        
        alphabetical_dir = base_dir / "2. 가나다 순"
        alphabetical_dir.mkdir(exist_ok=True)
        
        # 캐릭터명으로 정렬
        df_sorted = df.sort_values('캐릭터명', key=lambda x: x.str.replace(' ', ''))
        
        copied_count = 0
        for idx, row in df_sorted.iterrows():
            char_name = str(row['캐릭터명']).strip()
            image_path = str(row.get('캐릭터아이콘경로', '')).strip()
            
            if not char_name or not image_path:
                continue
                
            # 원본 이미지 파일 찾기
            source_file = self._find_source_image(image_path, char_name)
            if not source_file:
                continue
            
            # 파일명 생성 (순번_캐릭터명)
            file_extension = source_file.suffix
            safe_filename = f"{idx+1:03d}_{self._safe_filename(char_name)}{file_extension}"
            dest_file = alphabetical_dir / safe_filename
            
            # 파일 복사
            try:
                shutil.copy2(source_file, dest_file)
                copied_count += 1
            except Exception as e:
                print(f"⚠️ 파일 복사 실패 ({char_name}): {e}")
        
        print(f"✅ 가나다 순 정리 완료: {copied_count}개 파일")
    
    def _find_source_image(self, image_path, char_name):
        """이미지 파일 찾기 (여러 경로에서 검색)"""
        # 1. CSV에서 지정한 경로
        full_path = self.project_root / image_path
        if full_path.exists():
            return full_path
        
        # 2. 캐릭터 아트 폴더에서 직접 검색
        filename = Path(image_path).name
        direct_path = self.images_dir / filename
        if direct_path.exists():
            return direct_path
        
        # 3. 캐릭터명으로 검색
        for file in self.images_dir.glob("*.png"):
            if self._normalize_name(char_name) in self._normalize_name(file.stem):
                return file
        
        # 4. 백업 폴더에서 검색
        backup_icon_dir = self.project_root / "05_archive" / "old_versions" / "icons_for_tierlist_250723"
        if backup_icon_dir.exists():
            for file in backup_icon_dir.glob("*.png"):
                if self._normalize_name(char_name) in self._normalize_name(file.stem):
                    return file
        
        print(f"⚠️ 이미지 파일을 찾을 수 없습니다: {char_name} ({image_path})")
        return None
    
    def _normalize_name(self, name):
        """이름 정규화 (공백, 특수문자 제거)"""
        return re.sub(r'[^\w가-힣]', '', str(name)).lower()
    
    def _safe_filename(self, name):
        """파일명으로 안전한 문자열 생성"""
        # Windows 파일명에서 허용되지 않는 문자 제거
        unsafe_chars = r'<>:"/\|?*'
        safe_name = str(name)
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        return safe_name
    
    def _format_date_for_filename(self, date_str):
        """날짜 문자열을 파일명용으로 포맷팅"""
        try:
            # 다양한 날짜 형식 처리
            date_patterns = [
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
                r'(\d{4})\.(\d{1,2})\.(\d{1,2})',      # YYYY.MM.DD
                r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'  # YYYY년 MM월 DD일
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    year, month, day = match.groups()
                    return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # 패턴에 맞지 않으면 원본 반환 (안전한 문자로 변환)
            return re.sub(r'[^\w가-힣.-]', '-', date_str)
        except:
            return "0000-00-00"
    
    def copy_backup_images(self):
        """백업 폴더의 이미지들을 메인 폴더로 복사"""
        print("📦 백업 이미지 복사 중...")
        
        backup_icon_dir = self.project_root / "05_archive" / "old_versions" / "icons_for_tierlist_250723"
        if not backup_icon_dir.exists():
            print("❌ 백업 이미지 폴더를 찾을 수 없습니다.")
            return False
        
        # 메인 이미지 폴더 확인 및 생성
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        copied_count = 0
        for backup_file in backup_icon_dir.glob("*.png"):
            dest_file = self.images_dir / backup_file.name
            
            # 이미 존재하지 않는 경우에만 복사
            if not dest_file.exists():
                try:
                    shutil.copy2(backup_file, dest_file)
                    copied_count += 1
                except Exception as e:
                    print(f"⚠️ 파일 복사 실패 ({backup_file.name}): {e}")
        
        print(f"✅ 백업 이미지 복사 완료: {copied_count}개 파일")
        return True

def main():
    """독립 실행"""
    project_root = Path(__file__).parent.parent
    organizer = ImageOrganizer(project_root)
    
    print("🗂️ Another Eden 이미지 자동 정리 시스템")
    print("=" * 50)
    
    # 1. 백업 이미지 복사
    organizer.copy_backup_images()
    
    # 2. 이미지 정리
    organizer.create_organized_folders()
    
    print("🎉 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()