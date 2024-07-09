import os

def update_labels_in_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        parts = line.strip().split()
        if parts[0] == '0':
            parts[0] = '6'
        updated_lines.append(' '.join(parts))

    with open(file_path, 'w') as file:
        file.write('\n'.join(updated_lines) + '\n')

def update_labels_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            update_labels_in_file(file_path)

# 예제 사용
directory_path = 'labels'
update_labels_in_directory(directory_path)
