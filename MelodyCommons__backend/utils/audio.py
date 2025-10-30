import os
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
import hashlib

ALLOWED_AUDIO_FORMATS = [".mp3", ".flac", ".wav"]
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_hash(file_path: str) -> str:
    """计算文件MD5哈希"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def extract_audio_metadata(file_path: str) -> dict:
    """提取音频文件元数据"""
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            return {}

        metadata = {
            "title": "",
            "artist": "",
            "album": "",
            "duration": 0
        }

        # 获取基本信息
        if hasattr(audio_file, 'info') and audio_file.info:
            metadata["duration"] = int(audio_file.info.length) if audio_file.info.length else 0

        # 获取标签信息
        if audio_file.tags:
            # 标题
            title = audio_file.tags.get("TIT2") or audio_file.tags.get("TITLE") or audio_file.tags.get("\xa9nam")
            if title:
                metadata["title"] = str(title[0]) if isinstance(title, list) else str(title)

            # 艺术家
            artist = audio_file.tags.get("TPE1") or audio_file.tags.get("ARTIST") or audio_file.tags.get("\xa9ART")
            if artist:
                metadata["artist"] = str(artist[0]) if isinstance(artist, list) else str(artist)

            # 专辑
            album = audio_file.tags.get("TALB") or audio_file.tags.get("ALBUM") or audio_file.tags.get("\xa9alb")
            if album:
                metadata["album"] = str(album[0]) if isinstance(album, list) else str(album)

        # 如果没有提取到标题，使用文件名
        if not metadata["title"]:
            metadata["title"] = os.path.splitext(os.path.basename(file_path))[0]

        # 如果没有提取到艺术家，使用未知
        if not metadata["artist"]:
            metadata["artist"] = "Unknown Artist"

        return metadata

    except Exception as e:
        print(f"Error extracting metadata from {file_path}: {e}")
        return {
            "title": os.path.splitext(os.path.basename(file_path))[0],
            "artist": "Unknown Artist",
            "album": "",
            "duration": 0
        }


def is_valid_audio_file(filename: str) -> bool:
    """检查是否为有效的音频文件"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_AUDIO_FORMATS


def get_unique_filename(directory: str, filename: str) -> str:
    """生成唯一的文件名"""
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1

    return new_filename
