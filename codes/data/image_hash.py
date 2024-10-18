import os
import shutil
from PIL import Image
import imagehash

def calculate_hash(image_path):
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"Error calculating hash for {image_path}: {e}")
        return None

def find_and_move_duplicates(src_image_dir, dst_image_dir, src_label_dir, dst_label_dir):
    if not os.path.exists(dst_image_dir):
        os.makedirs(dst_image_dir)
    if not os.path.exists(dst_label_dir):
        os.makedirs(dst_label_dir)

    image_hashes = {}
    duplicate_count = 0

    for class_dir in os.listdir(src_image_dir):
        class_image_path = os.path.join(src_image_dir, class_dir)
        class_label_path = os.path.join(src_label_dir, class_dir)

        if not os.path.isdir(class_image_path):
            continue

        if not os.path.exists(os.path.join(dst_image_dir, class_dir)):
            os.makedirs(os.path.join(dst_image_dir, class_dir))
        if not os.path.exists(os.path.join(dst_label_dir, class_dir)):
            os.makedirs(os.path.join(dst_label_dir, class_dir))

        for root, _, files in os.walk(class_image_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = calculate_hash(file_path)

                if file_hash is None:
                    continue

                if file_hash in image_hashes:
                    new_image_path = os.path.join(dst_image_dir, class_dir, file)
                    shutil.move(file_path, new_image_path)
                    print(f"Moved duplicate image {file_path} to {new_image_path}")

                    # Move corresponding label file from src_label_dir to dst_label_dir
                    label_file = os.path.join(class_label_path, os.path.splitext(file)[0] + '.txt')
                    if os.path.exists(label_file):
                        new_label_path = os.path.join(dst_label_dir, class_dir, os.path.basename(label_file))
                        shutil.move(label_file, new_label_path)
                        print(f"Moved label file {label_file} to {new_label_path}")

                    duplicate_count += 1
                else:
                    image_hashes[file_hash] = file_path

    print(f"Total duplicate images moved: {duplicate_count}")

source_image_directory = '../dataset/images'  # 이미지가 있는 디렉토리
destination_image_directory = '../dataset/images_hashed'  # 중복 이미지를 옮길 디렉토리
source_label_directory = '../dataset/labels'  # 라벨 파일이 있는 디렉토리
destination_label_directory = '../dataset/labels_hashed'  # 중복 라벨 파일을 옮길 디렉토리

find_and_move_duplicates(source_image_directory, destination_image_directory, source_label_directory, destination_label_directory)
