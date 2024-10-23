import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2  # OpenCV 라이브러리
import threading  # 스레드 라이브러리 추가
import shutil  # 파일 복사를 위한 라이브러리 추가

class YOLOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO 유해 오브젝트 감지 프로그램")
        self.root.geometry("1080x800")
        self.root.configure(bg="#f0f0f0")  # 배경색

        # 제목 레이블
        title_label = tk.Label(root, text="유해 오브젝트 감지", font=("Arial", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)

        # 이미지/영상 선택 버튼
        self.upload_btn = tk.Button(root, text="이미지/영상 파일 업로드", command=self.upload_file, font=("Arial", 14), bg="#4CAF50", fg="white", padx=20, pady=10)
        self.upload_btn.pack(pady=20)

        # 모자이크 버튼 추가
        self.mosaic_btn = tk.Button(root, text="모자이크 적용", command=self.apply_mosaic, font=("Arial", 14), bg="#FF5722", fg="white", padx=20, pady=10)
        self.mosaic_btn.pack(pady=20)

        # 처리 상태 레이블
        self.status_label = tk.Label(root, text="", font=("Arial", 12, "italic"), bg="#f0f0f0")
        self.status_label.pack(pady=10)

        # 결과 이미지/영상 표시
        self.image_label = tk.Label(root, bg="#f0f0f0")
        self.image_label.pack()

        # 영상 스트림 관리 변수
        self.cap = None
        self.video_path = None
        self.is_playing = False  # 영상 재생 상태
        self.after_id = None  # after 호출 ID 저장
        self.mosaic_image_path = None  # 모자이크 이미지 경로

    def upload_file(self):
        # 파일 다이얼로그를 통해 이미지 또는 영상 파일 선택
        file_path = filedialog.askopenfilename(filetypes=[("Image and Video files", "*.jpg *.jpeg *.png *.gif *.mp4 *.avi")])
        if file_path:
            # 새 파일을 업로드 할 때 기존의 영상 및 이미지를 초기화
            self.reset_video_display()

            # 처리 상태 업데이트
            self.status_label.config(text="처리중...")

            # YOLO 모델을 실행할 스레드 생성
            processing_thread = threading.Thread(target=self.run_yolo, args=(file_path,))
            processing_thread.start()  # 스레드 시작

    def run_yolo(self, file_path):
        try:
            # YOLO 모델을 실행하는 subprocess 명령
            subprocess.run([ 
                'python', 'detect.py', 
                '--weights', 'runs/train/exp/weights/best.pt',  # 모델 경로
                '--img', '640',  # 이미지 크기
                '--conf', '0.5',  # 신뢰도 기준
                '--source', file_path,  # 선택된 파일 경로 (이미지 또는 영상)
                '--save-txt',  # 결과를 txt로 저장
                '--save-conf',  # 신뢰도도 함께 저장
            ])
            
            # 원본 이미지도 저장 (이름을 _original로 변경)
            self.save_original_image(file_path)

            # YOLO 처리 완료 후 결과를 표시
            self.display_results(file_path)

        except Exception as e:
            self.status_label.config(text="오류 발생")  # 오류 메시지 업데이트
            messagebox.showerror("Error", f"오류 발생: {str(e)}")
            self.reset_video_display()

    def save_original_image(self, file_path):
        # 원본 이미지 저장
        latest_exp_path = self.get_latest_exp_folder()
        if latest_exp_path:
            original_image_path = os.path.join(latest_exp_path, os.path.basename(file_path).replace('.', '_original.'))
            shutil.copy(file_path, original_image_path)  # 원본 이미지를 새로운 경로로 복사
            print(f"원본 이미지 저장 완료: {original_image_path}")  # 저장 완료 메시지

    def display_results(self, file_path):
        # 파일 확장자 확인
        file_extension = os.path.splitext(file_path)[1].lower()

        # 결과 표시
        latest_exp_path = self.get_latest_exp_folder()
        if latest_exp_path:
            if file_extension in ['.mp4', '.avi']:
                result_video_path = os.path.join(latest_exp_path, os.path.basename(file_path))  # 결과 영상 파일 경로
                self.video_path = result_video_path
                self.play_video(result_video_path)  # 결과 영상 재생
            elif file_extension == '.gif':
                result_video_path = os.path.join(latest_exp_path, os.path.splitext(os.path.basename(file_path))[0] + '.mp4')
                if os.path.exists(result_video_path):  # MP4 파일이 존재하는지 확인
                    self.video_path = result_video_path
                    self.play_video(result_video_path)  # 결과 영상 재생
                else:
                    messagebox.showerror("Error", f"결과 MP4 파일을 찾을 수 없습니다: {result_video_path}")
            else:
                result_image_path = os.path.join(latest_exp_path, os.path.basename(file_path))  # 이미지 결과 파일 경로
                self.show_image(result_image_path)  # 결과 이미지 표시
                self.mosaic_image_path = result_image_path  # 모자이크에 사용할 이미지 경로 저장

            self.status_label.config(text="처리 완료!")  # 처리 완료 상태로 변경
        else:
            self.status_label.config(text="결과 폴더를 찾을 수 없습니다.")  # 결과 폴더가 없을 경우 처리

    def apply_mosaic(self):
        if self.mosaic_image_path:
             # 모자이크 적용
            mosaic_script_path = 'mosaic.py'  # mosaic.py 경로
            subprocess.run(['python', mosaic_script_path])

            # 모자이크 이미지 경로 설정 (이름을 _original_mosaic로 변경)
            mosaic_image_file = os.path.splitext(os.path.basename(self.mosaic_image_path))[0] + '_original_mosaic.jpg'
            latest_exp_path = self.get_latest_exp_folder()
            mosaic_image_path = os.path.join(latest_exp_path, mosaic_image_file)

            # 모자이크 이미지 표시
            self.show_image(mosaic_image_path)
            self.status_label.config(text="모자이크 적용 완료!")  # 상태 레이블 업데이트
        else:
            messagebox.showwarning("Warning", "먼저 이미지를 처리한 후 모자이크를 적용하세요.")    


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
            img = img.resize((400, 400), Image.LANCZOS)  # 이미지 크기 조정
            img_tk = ImageTk.PhotoImage(img)

            # 이미지 라벨에 표시
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk
        else:
            messagebox.showerror("Error", f"결과 이미지를 찾을 수 없습니다: {image_path}")

    def play_video(self, video_path):
        # OpenCV로 영상 파일을 재생
        if not os.path.exists(video_path):
            messagebox.showerror("Error", f"영상 파일을 찾을 수 없습니다: {video_path}")
            return

        # 영상 스트림 열기
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "영상을 열 수 없습니다.")
            return

        self.is_playing = True  # 영상 재생 상태 설정

        # FPS 가져오기
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / self.fps) if self.fps > 0 else 30  # FPS에 맞는 지연 설정

        # 영상 업데이트 함수
        self.update_frame()

    def update_frame(self):
        if not self.is_playing:
            return

        ret, frame = self.cap.read()
        if ret:
            # OpenCV 이미지를 Tkinter가 처리할 수 있는 포맷으로 변환
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 이미지 크기 조정
            height, width, _ = frame.shape
            max_height = 400  # 최대 높이
            max_width = 800  # 최대 너비

            if height > max_height or width > max_width:
                scaling_factor = min(max_height / height, max_width / width)
                frame = cv2.resize(frame, (int(width * scaling_factor), int(height * scaling_factor)))

            # 이미지를 PhotoImage로 변환하여 라벨에 표시
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

            self.after_id = self.root.after(self.delay, self.update_frame)  # 다음 프레임 업데이트 예약
        else:
            self.stop_video()

    def stop_video(self):
        if self.cap is not None:
            self.cap.release()
        self.is_playing = False

    def reset_video_display(self):
        # 영상 및 이미지 초기화
        if self.cap is not None:
            self.cap.release()
        self.image_label.config(image='')
        self.is_playing = False
        self.status_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOApp(root)
    root.mainloop()
