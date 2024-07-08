import os
import shutil
import hashlib
from PIL import Image
import imagehash

def calculate_hash(image_path):
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"Error calculating hash for {image_path}: {e}")
        return None

def find_and_move_duplicates(src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    image_hashes = {}
    duplicate_count = 0

    for root, _, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_hash(file_path)

            if file_hash is None:
                continue

            if file_hash in image_hashes:
                new_path = os.path.join(dst_dir, file)
                shutil.move(file_path, new_path)
                print(f"Moved duplicate image {file_path} to {new_path}")
                duplicate_count += 1
            else:
                image_hashes[file_hash] = file_path

    print(f"Total duplicate images moved: {duplicate_count}")

source_directory = '../dataset/images'  # 이미지가 있는 디렉토리
destination_directory = '../dataset/images_hashed'  # 중복 이미지를 옮길 디렉토리

find_and_move_duplicates(source_directory, destination_directory)
