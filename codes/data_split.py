import os
import random
import shutil

# 이미지가 저장된 디렉터리 경로
image_dir = '../dataset/images/'

# 레이블이 저장된 디렉터리 경로
label_dir = '../dataset/labels/'

# train, val, test 비율
train_ratio = 0.7
val_ratio = 0.2
test_ratio = 0.1

# 모든 이미지 파일 경로 읽기
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.jpg')]

# 파일 경로를 랜덤하게 섞기
random.shuffle(image_files)

# 학습, 검증, 테스트 데이터셋으로 나누기
train_count = int(len(image_files) * train_ratio)
val_count = int(len(image_files) * val_ratio)

train_files = image_files[:train_count]
val_files = image_files[train_count:train_count + val_count]
test_files = image_files[train_count + val_count:]

# 파일 경로를 txt 파일로 저장하기
with open('../dataset/train.txt', 'w') as f:
    for file in train_files:
        f.write(f"{file}\n")

with open('../dataset/val.txt', 'w') as f:
    for file in val_files:
        f.write(f"{file}\n")

with open('../dataset/test.txt', 'w') as f:
    for file in test_files:
        f.write(f"{file}\n")