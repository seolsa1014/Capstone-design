import subprocess

# YOLOv5 detect.py 실행
subprocess.run(['python', 'detect.py', '--weights', 'runs/train/exp/weights/best.pt', '--img', '640', '--conf', '0.5', '--source', '../dataset/real_test/gesture.mp4', '--save-txt', '--save-conf'])