import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
from pathlib import Path
import threading

class NotionStyleLauncher:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        
    def setup_window(self):
        """윈도우 기본 설정"""
        self.root.title("🎮 Another Eden 통합 런처")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")
        
        # 윈도우 중앙 정렬
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """스타일 설정 (Notion 스타일)"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 색상 정의
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'gray': '#6c757d',
            'white': '#ffffff'
        }
        
        # 버튼 스타일
        self.style.configure('Primary.TButton', 
                           background=self.colors['primary'],
                           foreground=self.colors['white'],
                           font=('Segoe UI', 11, 'bold'),
                           padding=10,
                           borderwidth=0)
        self.style.map('Primary.TButton', 
                      background=[('active', self.colors['secondary'])])
        
        # 프레임 스타일
        self.style.configure('Card.TFrame', 
                           background=self.colors['white'],
                           relief='flat')
        
        # 라벨 스타일
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 16, 'bold'),
                           background=self.colors['white'],
                           foreground=self.colors['dark'])
        
        self.style.configure('SubHeader.TLabel', 
                           font=('Segoe UI', 12),
                           background=self.colors['white'],
                           foreground=self.colors['gray'])
        
    def create_widgets(self):
        """위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 헤더
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_label = ttk.Label(header_frame, 
                                text="🎮 Another Eden 통합 런처", 
                                style='Header.TLabel')
        header_label.pack(side='left')
        
        # 카드 프레임들
        self.create_scraper_card(main_frame)
        self.create_apps_card(main_frame)
        self.create_utils_card(main_frame)
        
        # 로그 영역
        self.create_log_area(main_frame)
        
    def create_scraper_card(self, parent):
        """스크래퍼 카드 생성"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=(0, 15))
        
        title = ttk.Label(card, text="📡 데이터 스크래퍼", style='SubHeader.TLabel')
        title.pack(anchor='w', pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="캐릭터 데이터와 이미지를 새로 생성하거나 업데이트합니다.", 
                        style='SubHeader.TLabel')
        desc.pack(anchor='w')
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=10)
        
        self.scraper_btn = ttk.Button(btn_frame, 
                                     text="스크래퍼 실행", 
                                     style='Primary.TButton',
                                     command=self.run_scraper)
        self.scraper_btn.pack(side='left')
        
        self.scraper_status = ttk.Label(btn_frame, 
                                       text="대기 중", 
                                       style='SubHeader.TLabel')
        self.scraper_status.pack(side='left', padx=(10, 0))
        
    def create_apps_card(self, parent):
        """앱 카드 생성"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=(0, 15))
        
        title = ttk.Label(card, text="🎯 앱 실행", style='SubHeader.TLabel')
        title.pack(anchor='w', pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="퀴즈쇼 또는 룰렛 앱을 실행합니다.", 
                        style='SubHeader.TLabel')
        desc.pack(anchor='w')
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=10)
        
        self.quiz_btn = ttk.Button(btn_frame, 
                                  text="퀴즈 앱 실행", 
                                  style='Primary.TButton',
                                  command=self.run_quiz_app)
        self.quiz_btn.pack(side='left', padx=(0, 10))
        
        self.roulette_btn = ttk.Button(btn_frame, 
                                      text="룰렛 앱 실행", 
                                      style='Primary.TButton',
                                      command=self.run_roulette_app)
        self.roulette_btn.pack(side='left')
        
    def create_utils_card(self, parent):
        """유틸리티 카드 생성"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='x', pady=(0, 15))
        
        title = ttk.Label(card, text="🛠️ 유틸리티", style='SubHeader.TLabel')
        title.pack(anchor='w', pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="프로젝트 구조를 재정비하거나 기타 유틸리티 기능을 실행합니다.", 
                        style='SubHeader.TLabel')
        desc.pack(anchor='w')
        
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=10)
        
        self.restructure_btn = ttk.Button(btn_frame, 
                                         text="구조 재정비", 
                                         style='Primary.TButton',
                                         command=self.run_restructure)
        self.restructure_btn.pack(side='left')
        
    def create_log_area(self, parent):
        """로그 영역 생성"""
        log_frame = ttk.Frame(parent, style='Card.TFrame')
        log_frame.pack(fill='both', expand=True)
        
        title = ttk.Label(log_frame, text="📋 실행 로그", style='SubHeader.TLabel')
        title.pack(anchor='w', pady=(10, 5))
        
        # 로그 텍스트 위젯
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 height=10,
                                                 font=('Consolas', 10),
                                                 bg=self.colors['light'],
                                                 fg=self.colors['dark'])
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 로그 클리어 버튼
        clear_btn = ttk.Button(log_frame, 
                              text="로그 지우기", 
                              command=self.clear_log)
        clear_btn.pack(anchor='e', padx=10, pady=(0, 10))
        
    def log_message(self, message):
        """로그 메시지 추가"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
        
    def get_project_root(self):
        """프로젝트 루트 경로 반환"""
        # gui_launcher.py 위치: .../02_launcher/
        # 프로젝트 루트: .../
        return Path(__file__).parent.parent.resolve()
        
    def run_scraper(self):
        """스크래퍼 실행"""
        self.scraper_btn.config(state='disabled')
        self.scraper_status.config(text="실행 중...")
        self.log_message("[스크래퍼] 실행을 시작합니다...")
        
        def scraper_thread():
            try:
                scraper_path = Path(__file__).parent.parent / "01_scraping" / "master_scraper.py"
                if not scraper_path.exists():
                    self.log_message(f"[스크래퍼] 파일을 찾을 수 없습니다: {scraper_path}")
                    return
                
                # 스크래퍼 실행
                process = subprocess.Popen([sys.executable, str(scraper_path)], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         text=True,
                                         bufsize=1,
                                         universal_newlines=True)
                
                # 실시간 로그 출력
                for line in process.stdout:
                    self.log_message(f"[스크래퍼] {line.strip()}")
                
                process.wait()
                if process.returncode == 0:
                    self.log_message("[스크래퍼] 실행이 완료되었습니다!")
                    self.scraper_status.config(text="완료", foreground=self.colors['success'])
                else:
                    self.log_message(f"[스크래퍼] 실행 중 오류가 발생했습니다. 종료 코드: {process.returncode}")
                    self.scraper_status.config(text="오류", foreground=self.colors['danger'])
            except Exception as e:
                self.log_message(f"[스크래퍼] 실행 중 예외 발생: {str(e)}")
                self.scraper_status.config(text="오류", foreground=self.colors['danger'])
            finally:
                self.scraper_btn.config(state='normal')
                
        # 스레드에서 실행
        thread = threading.Thread(target=scraper_thread)
        thread.daemon = True
        thread.start()
        
    def run_quiz_app(self):
        """퀴즈 앱 실행"""
        self.quiz_btn.config(state='disabled')
        self.log_message("[퀴즈 앱] 실행을 시작합니다...")
        
        def quiz_thread():
            try:
                app_path = Path(__file__).parent.parent / "03_apps" / "quiz" / "eden_quiz_app.py"
                if not app_path.exists():
                    self.log_message(f"[퀴즈 앱] 파일을 찾을 수 없습니다: {app_path}")
                    return
                
                # 퀴즈 앱 실행
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(app_path)])
                self.log_message("[퀴즈 앱] 브라우저에서 실행 중입니다.")
            except Exception as e:
                self.log_message(f"[퀴즈 앱] 실행 중 예외 발생: {str(e)}")
            finally:
                self.root.after(0, lambda: self.quiz_btn.config(state='normal'))
                
        # 스레드에서 실행
        thread = threading.Thread(target=quiz_thread)
        thread.daemon = True
        thread.start()
        
    def run_roulette_app(self):
        """룰렛 앱 실행"""
        self.roulette_btn.config(state='disabled')
        self.log_message("[룰렛 앱] 실행을 시작합니다...")
        
        def roulette_thread():
            try:
                app_path = Path(__file__).parent.parent / "03_apps" / "roulette" / "streamlit_eden_restructure.py"
                if not app_path.exists():
                    self.log_message(f"[룰렛 앱] 파일을 찾을 수 없습니다: {app_path}")
                    return
                
                # 룰렛 앱 실행
                subprocess.Popen([sys.executable, "-m", "streamlit", "run", str(app_path)])
                self.log_message("[룰렛 앱] 브라우저에서 실행 중입니다.")
            except Exception as e:
                self.log_message(f"[룰렛 앱] 실행 중 예외 발생: {str(e)}")
            finally:
                self.root.after(0, lambda: self.roulette_btn.config(state='normal'))
                
        # 스레드에서 실행
        thread = threading.Thread(target=roulette_thread)
        thread.daemon = True
        thread.start()
        
    def run_restructure(self):
        """구조 재정비 실행"""
        self.restructure_btn.config(state='disabled')
        self.log_message("[구조 재정비] 실행을 시작합니다...")
        
        def restructure_thread():
            try:
                script_path = Path(__file__).parent.parent / "restructure_project.py"
                if not script_path.exists():
                    self.log_message(f"[구조 재정비] 파일을 찾을 수 없습니다: {script_path}")
                    return
                
                # 구조 재정비 스크립트 실행
                process = subprocess.Popen([sys.executable, str(script_path)], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         text=True,
                                         bufsize=1,
                                         universal_newlines=True)
                
                # 실시간 로그 출력
                for line in process.stdout:
                    self.log_message(f"[구조 재정비] {line.strip()}")
                
                process.wait()
                if process.returncode == 0:
                    self.log_message("[구조 재정비] 실행이 완료되었습니다!")
                else:
                    self.log_message(f"[구조 재정비] 실행 중 오류가 발생했습니다. 종료 코드: {process.returncode}")
            except Exception as e:
                self.log_message(f"[구조 재정비] 실행 중 예외 발생: {str(e)}")
            finally:
                self.root.after(0, lambda: self.restructure_btn.config(state='normal'))
                
        # 스레드에서 실행
        thread = threading.Thread(target=restructure_thread)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = NotionStyleLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
