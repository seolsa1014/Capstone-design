import subprocess

# YOLOv5 detect.py 실행
subprocess.run(['python', 'detect.py', '--weights', 'runs/train/exp9/weights/best.pt', '--img', '640', '--conf', '0.5', '--source', '../dataset/real_test/test1.jpg', '--save-txt', '--save-conf'])