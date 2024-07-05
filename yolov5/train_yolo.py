import subprocess
import torch

device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
print(device)
print("CUDA Available: ", torch.cuda.is_available())
print("CUDA Device Count: ", torch.cuda.device_count())
# YOLOv5 학습 실행
subprocess.run(['python', 'train.py', '--img', '640', '--batch', '16', '--epochs', '30', '--data', 'data/dataset.yaml', '--weights', 'yolov5s.pt'])