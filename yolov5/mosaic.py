import os
import cv2

def apply_mosaic(image, bounding_boxes, mosaic_scale=0.05):
    """
    주어진 이미지에 바운딩 박스를 기준으로 모자이크를 적용합니다.
    :param image: 원본 이미지
    :param bounding_boxes: 바운딩 박스 리스트 (x, y, w, h)
    :param mosaic_scale: 모자이크 적용 비율 (값이 작을수록 모자이크가 더 크게 적용됨)
    :return: 모자이크가 적용된 이미지
    """
    for (x, y, w, h) in bounding_boxes:
        # 모자이크를 적용할 영역을 추출
        roi = image[y:y+h, x:x+w]

        # 모자이크를 적용할 크기로 조정
        roi = cv2.resize(roi, (int(w * mosaic_scale), int(h * mosaic_scale)), interpolation=cv2.INTER_LINEAR)

        # 다시 원래 크기로 확대
        roi = cv2.resize(roi, (w, h), interpolation=cv2.INTER_NEAREST)

        # 모자이크 영역을 원본 이미지에 덮어씌움
        image[y:y+h, x:x+w] = roi

    return image

def get_bounding_boxes(label_file_path, image_width, image_height):
    """
    label 파일에서 바운딩 박스 좌표를 읽어옵니다.

    :param label_file_path: label 파일 경로
    :param image_width: 이미지 너비
    :param image_height: 이미지 높이
    :return: 바운딩 박스 리스트 (x, y, w, h)
    """
    bounding_boxes = []
    
    with open(label_file_path, 'r') as f:
        for line in f.readlines():
            # YOLO 형식 (클래스 x_center y_center width height)
            # 첫 번째(클래스)와 마지막(신뢰도) 값을 무시
            values = line.split()
            if len(values) >= 5:  # 최소한 5개의 값이 있어야 함
                x_center, y_center, width, height = map(float, values[1:5])
                x_center, y_center, width, height = x_center * image_width, y_center * image_height, width * image_width, height * image_height
                x = int(x_center - width / 2)
                y = int(y_center - height / 2)
                bounding_boxes.append((x, y, int(width), int(height)))

    return bounding_boxes

def get_latest_exp_folder(detect_dir='runs/detect'):
    """
    YOLO 결과 폴더에서 가장 최근의 exp 폴더를 찾습니다.
    :param detect_dir: YOLO 결과가 저장된 디렉토리
    :return: 가장 최근의 exp 폴더 경로
    """
    exp_folders = [os.path.join(detect_dir, d) for d in os.listdir(detect_dir) if os.path.isdir(os.path.join(detect_dir, d))]
    if not exp_folders:
        return None
    latest_exp_folder = max(exp_folders, key=os.path.getmtime)  # 가장 최근의 폴더 선택
    return latest_exp_folder

def mosaic_images_in_folder(results_folder):
    """
    YOLO 결과 폴더에서 이미지를 불러와 바운딩 박스 정보를 바탕으로 모자이크를 적용하고 저장합니다.
    :param results_folder: YOLO 결과 폴더 (detect 결과가 저장된 폴더)
    """
    # labels 폴더와 images 파일 경로 설정
    labels_folder = os.path.join(results_folder, 'labels')
    images_folder = results_folder  # 결과가 저장된 폴더 경로

    # 이미지 파일들을 확인
    for image_file in os.listdir(images_folder):
        if image_file.endswith(('.jpg', '.png', '.jpeg')) and '_original' in image_file:  # 원본 이미지만 처리
            image_path = os.path.join(images_folder, image_file)
            label_file = os.path.join(labels_folder, os.path.splitext(image_file.replace('_original', ''))[0] + '.txt')

            if os.path.exists(label_file):
                # 이미지 로드
                image = cv2.imread(image_path)
                image_height, image_width = image.shape[:2]  # 이미지 크기

                # 바운딩 박스 정보 읽기
                bounding_boxes = get_bounding_boxes(label_file, image_width, image_height)

                # 모자이크 적용
                mosaic_image = apply_mosaic(image, bounding_boxes)

                # 모자이크 적용된 이미지 저장
                mosaic_image_path = os.path.join(images_folder, os.path.splitext(image_file)[0] + '_mosaic.jpg')
                cv2.imwrite(mosaic_image_path, mosaic_image)
                print(f"모자이크 이미지 저장 완료: {mosaic_image_path}")
            else:
                print(f"라벨 파일을 찾을 수 없습니다: {label_file}")

if __name__ == "__main__":
    # YOLO 결과 폴더 경로 입력
    results_folder = get_latest_exp_folder()  # 가장 최신의 YOLO 결과 폴더 경로로 수정
    if results_folder:
        mosaic_images_in_folder(results_folder)
    else:
        print("YOLO 결과 폴더를 찾을 수 없습니다.")
