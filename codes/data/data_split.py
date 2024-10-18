import os
import random
from glob import glob

# 디렉토리 경로 설정
base_dir = '../dataset/images'
output_dir = '../yolov5'

# 비율 설정
train_ratio = 0.7
val_ratio = 0.2
test_ratio = 0.1

# 파일 경로를 저장할 리스트 초기화
train_files = []
val_files = []
test_files = []

# 각 클래스 폴더를 순회
for class_dir in os.listdir(base_dir):
    class_path = os.path.join(base_dir, class_dir)
    if os.path.isdir(class_path):
        # 클래스 폴더 내의 모든 이미지 파일 경로를 가져옴
        image_files = glob(os.path.join(class_path, '*.jpg'))
        
        # 파일을 무작위로 섞음
        random.shuffle(image_files)
        
        # 각 셋의 파일 개수 계산
        total_count = len(image_files)
        train_count = int(total_count * train_ratio)
        val_count = int(total_count * val_ratio)
        test_count = total_count - train_count - val_count
        
        # 파일을 각각의 셋에 할당
        train_files.extend(image_files[:train_count])
        val_files.extend(image_files[train_count:train_count + val_count])
        test_files.extend(image_files[train_count + val_count:])

# 함수: 파일 경로를 텍스트 파일로 저장
def save_file_paths(file_paths, output_path):
    with open(output_path, 'w') as f:
        for file_path in file_paths:
            f.write(f"{file_path}\n")

# 파일 경로 저장
save_file_paths(train_files, os.path.join(output_dir, 'train.txt'))
save_file_paths(val_files, os.path.join(output_dir, 'val.txt'))
save_file_paths(test_files, os.path.join(output_dir, 'test.txt'))
