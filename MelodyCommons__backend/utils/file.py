import os
import shutil
from datetime import datetime
from fastapi import UploadFile

BASE_DIR = "D:/Projects/MelodyCommons/MelodyCommons__backend"
STATIC_DIR = "static"
AUDIO_DIR = "static/audio"


def ensure_directories():
    """确保必要的目录存在"""
    directories = [STATIC_DIR, AUDIO_DIR, "static/covers"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def save_uploaded_file(upload_file: UploadFile, directory: str) -> str:
    """保存上传的文件"""
    ensure_directories()

    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename, ext = os.path.splitext(upload_file.filename)
    unique_filename = f"{filename}_{timestamp}{ext}"

    # 确保文件名唯一
    counter = 1
    final_filename = unique_filename
    while os.path.exists(os.path.join(directory, final_filename)):
        final_filename = f"{filename}_{timestamp}_{counter}{ext}"
        counter += 1

    file_path = os.path.join(directory, final_filename)

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


def get_file_size(file_path: str) -> int:
    """获取文件大小"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
    return False
