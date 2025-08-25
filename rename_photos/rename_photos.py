import os
import hashlib
import argparse
import logging
from collections import defaultdict

def setup_logger():
    """配置日志记录器"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("photo_rename.log"),
            logging.StreamHandler()
        ],
        encoding = "utf-8"
    )
    return logging.getLogger()

def calculate_file_hash(file_path, algorithm='md5', buffer_size=65536):
    """计算文件的哈希值"""
    hasher = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"计算文件 {file_path} 的哈希值时出错: {str(e)}")
        return None

def rename_and_deduplicate(directory):
    """重命名照片并删除重复文件"""
    # 支持的图片文件扩展名
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.raw', '.arw'}
    
    # 存储哈希值到文件路径的映射
    hash_map = defaultdict(list)
    total_files = 0
    renamed_count = 0
    duplicates_removed = 0
    errors = 0
    
    # 第一次遍历：收集所有文件的哈希值
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 跳过子目录和非文件项
        if not os.path.isfile(file_path):
            continue
        
        # 检查文件扩展名
        _, file_ext = os.path.splitext(filename)
        file_ext = file_ext.lower()
        
        if file_ext not in image_extensions:
            continue
        
        total_files += 1
        file_hash = calculate_file_hash(file_path)
        
        if file_hash:
            hash_map[file_hash].append(file_path)
    
    # 第二次遍历：重命名和删除重复文件
    for file_hash, file_paths in hash_map.items():
        # 保留第一个文件，删除其他重复文件
        if len(file_paths) > 1:
            original_file = file_paths[0]
            duplicates = file_paths[1:]
            
            # 删除重复文件
            for dup_path in duplicates:
                try:
                    os.remove(dup_path)
                    logging.info(f"删除重复文件: {os.path.basename(dup_path)} (哈希: {file_hash})")
                    duplicates_removed += 1
                except Exception as e:
                    logging.error(f"删除文件 {os.path.basename(dup_path)} 时出错: {str(e)}")
                    errors += 1
            
            # 重命名保留的文件
            file_paths = [original_file]
        
        # 重命名文件
        original_path = file_paths[0]
        _, file_ext = os.path.splitext(original_path)
        
        file_hash = file_hash[0:8]
        new_filename = f"{file_hash}{file_ext}"
        new_path = os.path.join(directory, new_filename)
        
        # 如果目标文件已存在且不同，添加后缀
        counter = 1
        while os.path.exists(new_path) and not os.path.samefile(original_path, new_path):
            new_filename = f"{file_hash}_{counter}{file_ext}"
            new_path = os.path.join(directory, new_filename)
            counter += 1
        
        if original_path != new_path:
            try:
                os.rename(original_path, new_path)
                logging.info(f"重命名: {os.path.basename(original_path)} -> {new_filename}")
                renamed_count += 1
            except Exception as e:
                logging.error(f"重命名文件 {os.path.basename(original_path)} 时出错: {str(e)}")
                errors += 1
    
    # 打印摘要
    logging.info("\n===== 操作摘要 =====")
    logging.info(f"扫描文件总数: {total_files}")
    logging.info(f"重命名文件数: {renamed_count}")
    logging.info(f"删除重复文件数: {duplicates_removed}")
    logging.info(f"错误数: {errors}")
    logging.info(f"最终保留文件数: {total_files - duplicates_removed - errors}")

if __name__ == "__main__":
    logger = setup_logger()
    
    parser = argparse.ArgumentParser(description='将照片文件重命名为其哈希值并删除重复文件')
    parser.add_argument('directory', help='包含照片的目录路径')
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        logger.error(f"错误: 目录 '{args.directory}' 不存在")
        exit(1)
    
    logger.info(f"开始处理目录: {args.directory}")
    rename_and_deduplicate(args.directory)
    logger.info("处理完成")