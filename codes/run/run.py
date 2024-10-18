import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

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
        
    def upload_file(self):
        # 파일 다이얼로그를 통해 이미지 파일 선택
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")])
        if file_path:
            try:
                # 선택된 파일을 YOLO 모델에 전달하여 처리
                self.run_yolo(file_path)
                self.result_label.config(text="이미지 처리 완료. 결과가 저장되었습니다.")
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
        # 결과는 YOLO detect.py 스크립트에서 지정한 폴더에 저장됩니다.

# Tkinter 창 실행
root = tk.Tk()
app = YOLOApp(root)
root.mainloop()
