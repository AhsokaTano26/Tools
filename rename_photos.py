import os
import hashlib
import argparse


def calculate_file_hash(file_path, algorithm='md5', buffer_size=65536):
    """计算文件的哈希值"""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def rename_images_to_hash(directory):
    """将目录中的照片文件重命名为其哈希值"""
    # 支持的图片文件扩展名
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # 跳过子目录和非文件项
        if not os.path.isfile(file_path):
            continue

        # 检查文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in image_extensions:
            continue

        try:
            # 计算文件哈希
            file_hash = calculate_file_hash(file_path)
            file_hash = file_hash[0:8]

            # 构建新文件名
            new_filename = f"{file_hash}{file_ext}"
            new_path = os.path.join(directory, new_filename)

            # 检查是否已存在同名文件
            counter = 1
            while os.path.exists(new_path):
                new_filename = f"{file_hash}_{counter}{file_ext}"
                new_path = os.path.join(directory, new_filename)
                counter += 1

            # 重命名文件
            os.rename(file_path, new_path)
            print(f"重命名: {filename} -> {new_filename}")

        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='将照片文件重命名为其哈希值')
    parser.add_argument('directory', help='包含照片的目录路径')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        exit(1)

    print(f"开始处理目录: {args.directory}")
    rename_images_to_hash(args.directory)
    print("处理完成")