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
        self.root.geometry("1300x1080")
        self.root.configure(bg="#f0f0f0")  # 배경색

        # 제목 레이블
        title_label = tk.Label(root, text="유해 오브젝트 감지", font=("Arial", 20, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # 사용 안내 레이블 추가
        guide_text = """
        1. 파일 형식: 이미지는 jpg, png, jpeg  /  영상은 gif, mp4, avi의 파일 형식이 지원됩니다.
        
        2. 모자이크 기능은 이미지에 한해서 지원됩니다.
        
        3. 영상이 길 경우 처리가 오래 걸릴 수 있습니다.

        4. 6가지 레이블을 감지합니다. 총, 칼, 혈흔, 흡연, 음주, 자살암시, 부적절한 제스쳐(미국식 손가락 욕)

        5. 모델의 특성상 작은 오브젝트는 감지하기 어려울 수 있습니다.
        """
        guide_label = tk.Label(root, text=guide_text, font=("Arial", 12), bg="#f0f0f0", justify="left", anchor="w")
        guide_label.pack(padx=20, pady=10, anchor="w")
        # 이미지/영상 선택 버튼
        self.upload_btn = tk.Button(root, text="이미지/영상 파일 업로드", command=self.upload_file, font=("Arial", 14), bg="#4CAF50", fg="white", padx=20, pady=10)
        self.upload_btn.pack(pady=20)

        # 모자이크 버튼 추가
        self.mosaic_btn = tk.Button(root, text="모자이크 적용", command=self.apply_mosaic, font=("Arial", 14), bg="#FF5722", fg="white", padx=20, pady=10)
        self.mosaic_btn.pack(pady=20)
        self.mosaic_btn.config(state=tk.DISABLED)  # 초기에는 비활성화

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
            
            latest_exp_path = self.get_latest_exp_folder()
            if latest_exp_path:
                messagebox.showinfo("결과 저장 폴더", f"결과가 저장된 폴더: {latest_exp_path}")

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
                self.mosaic_btn.config(state=tk.DISABLED)  # 영상 선택 시 모자이크 비활성화
            elif file_extension == '.gif':
                result_video_path = os.path.join(latest_exp_path, os.path.splitext(os.path.basename(file_path))[0] + '.mp4')
                if os.path.exists(result_video_path):  # MP4 파일이 존재하는지 확인
                    self.video_path = result_video_path
                    self.play_video(result_video_path)  # 결과 영상 재생
                    self.mosaic_btn.config(state=tk.DISABLED)  # 영상 선택 시 모자이크 비활성화
                else:
                    messagebox.showerror("Error", f"결과 MP4 파일을 찾을 수 없습니다: {result_video_path}")
            else:
                result_image_path = os.path.join(latest_exp_path, os.path.basename(file_path))  # 이미지 결과 파일 경로
                self.show_image(result_image_path)  # 결과 이미지 표시
                self.mosaic_image_path = result_image_path  # 모자이크에 사용할 이미지 경로 저장
                self.mosaic_btn.config(state=tk.NORMAL)  # 이미지 선택 시 모자이크 활성화

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
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / fps) if fps > 0 else 100  # FPS에 따라 딜레이 설정

        self.update_video_frame()  # 첫 번째 프레임 표시

    def update_video_frame(self):
        if self.is_playing and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 프레임을 RGB로 변환하고 PIL 이미지로 변환
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((1080, 720), Image.LANCZOS)  # 크기 조정
                img_tk = ImageTk.PhotoImage(img)

                # 이미지 라벨에 표시
                self.image_label.config(image=img_tk)
                self.image_label.image = img_tk

                # 다음 프레임 업데이트
                self.after_id = self.root.after(self.delay, self.update_video_frame)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 영상의 첫 프레임으로 설정
                self.update_video_frame()  # 다시 첫 프레임을 업데이트

    def reset_video_display(self):
        # 영상 스트림 해제 및 이미지 라벨 초기화
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)  # 다음 프레임 업데이트 중지
            self.after_id = None
        self.image_label.config(image='')  # 이미지 라벨 초기화
        self.mosaic_btn.config(state=tk.DISABLED)  # 모자이크 버튼 비활성화

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOApp(root)
    root.mainloop()
