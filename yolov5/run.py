import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# Tkinter GUI 설정
class YOLOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO 유해 오브젝트 감지 프로그램")
        
        # 파일 선택 버튼
        self.upload_btn = tk.Button(root, text="이미지 파일 업로드", command=self.upload_file)
        self.upload_btn.pack(pady=20)
        
        # 결과 레이블
        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

        # 결과 이미지 표시
        self.image_label = tk.Label(root)
        self.image_label.pack()

    def upload_file(self):
        # 파일 다이얼로그를 통해 이미지 파일 선택
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            try:
                # 파일명만 추출 (경로 제외)
                image_filename = os.path.basename(file_path)
                
                # 선택된 파일을 YOLO 모델에 전달하여 처리
                self.run_yolo(file_path)
                
                # 가장 최근의 exp 폴더에서 결과 이미지 가져오기
                latest_exp_path = self.get_latest_exp_folder()
                if latest_exp_path:
                    # 입력 이미지 파일명과 동일한 이름의 결과 파일 경로 설정
                    result_image_path = os.path.join(latest_exp_path, image_filename)  
                    self.show_image(result_image_path)
                    self.result_label.config(text="이미지 처리 완료. 결과가 표시됩니다.")
                else:
                    self.result_label.config(text="결과 폴더를 찾을 수 없습니다.")
                
            except Exception as e:
                messagebox.showerror("Error", f"오류 발생: {str(e)}")
                self.result_label.config(text="")
    
    def run_yolo(self, image_path):
        # YOLO 모델을 실행하는 subprocess 명령
        subprocess.run([
            'python', 'detect.py', 
            '--weights', 'runs/train/exp/weights/best.pt',  # 모델 경로
            '--img', '640',  # 이미지 크기
            '--conf', '0.5',  # 신뢰도 기준
            '--source', image_path,  # 선택된 이미지 파일 경로
            '--save-txt',  # 결과를 txt로 저장
            '--save-conf'  # 신뢰도도 함께 저장
        ])
    
    def get_latest_exp_folder(self):
        # runs/detect 폴더 내 가장 최근의 exp 폴더를 찾음
        detect_dir = 'runs/detect'
        exp_folders = [os.path.join(detect_dir, d) for d in os.listdir(detect_dir) if os.path.isdir(os.path.join(detect_dir, d))]
        if not exp_folders:
            return None
        latest_exp_folder = max(exp_folders, key=os.path.getmtime)  # 가장 최근의 폴더 선택
        return latest_exp_folder

    def show_image(self, image_path):
        # PIL로 이미지 로드 및 Tkinter용으로 변환
        if os.path.exists(image_path):  # 결과 이미지가 존재하는지 확인
            img = Image.open(image_path)
            img = img.resize((400, 400))  # 이미지 크기 조정
            img_tk = ImageTk.PhotoImage(img)

            # 이미지 라벨에 표시
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        else:
            messagebox.showerror("Error", f"결과 이미지를 찾을 수 없습니다: {image_path}")

# Tkinter 창 실행
root = tk.Tk()
app = YOLOApp(root)
root.mainloop()

