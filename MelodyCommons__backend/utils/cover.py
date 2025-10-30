import requests
import os
import hashlib
from typing import Optional

LRCAPI_COVER_URL = "https://api.lrc.cx/cover"
COVER_REQUEST_TIMEOUT = 10
COVER_DIR = "static/covers"
MAX_COVER_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_cover_dir():
    """确保封面目录存在"""
    if not os.path.exists(COVER_DIR):
        os.makedirs(COVER_DIR, exist_ok=True)


def generate_cover_filename(song_id: int, title: str, artist: str, album: str = "") -> str:
    """生成封面文件名"""
    content = f"{title}_{artist}_{album}".encode('utf-8')
    content_hash = hashlib.md5(content).hexdigest()[:8]
    return f"{song_id}_{content_hash}.jpg"


def download_cover_from_lrcapi(title: str, artist: str = "", album: str = "") -> Optional[bytes]:
    """从lrcapi下载封面"""
    try:
        params = {"title": title}
        if artist:
            params["artist"] = artist
        if album:
            params["album"] = album

        response = requests.get(
            LRCAPI_COVER_URL,
            params=params,
            timeout=COVER_REQUEST_TIMEOUT,
            allow_redirects=True
        )

        if response.status_code == 200:
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'image' in content_type:
                # 检查文件大小
                if len(response.content) <= MAX_COVER_SIZE:
                    return response.content
                else:
                    print(f"Cover too large: {len(response.content)} bytes")
            else:
                print(f"Invalid content type: {content_type}")
        else:
            print(f"Failed to download cover: {response.status_code}")

    except Exception as e:
        print(f"Error downloading cover: {e}")

    return None


def save_cover_image(song_id: int, title: str, artist: str, album: str = "") -> Optional[str]:
    """保存封面图片到本地"""
    ensure_cover_dir()

    # 生成文件名
    filename = generate_cover_filename(song_id, title, artist, album)
    file_path = os.path.join(COVER_DIR, filename)

    # 如果文件已存在，直接返回路径
    if os.path.exists(file_path):
        return file_path

    # 尝试从lrcapi下载
    cover_data = download_cover_from_lrcapi(title, artist, album)

    # 如果失败，尝试不带专辑信息
    if not cover_data and album:
        cover_data = download_cover_from_lrcapi(title, artist)

    # 如果还是失败，尝试只用标题
    if not cover_data and artist:
        cover_data = download_cover_from_lrcapi(title)

    if cover_data:
        try:
            with open(file_path, 'wb') as f:
                f.write(cover_data)
            return file_path
        except Exception as e:
            print(f"Error saving cover: {e}")

    return None


def get_cover_url(song_id: int, title: str, artist: str, album: str = "") -> Optional[str]:
    """获取封面URL（如果无法下载则直接返回API URL）"""
    try:
        params = {"title": title}
        if artist:
            params["artist"] = artist
        if album:
            params["album"] = album

        # 构建URL
        param_str = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
        return f"{LRCAPI_COVER_URL}?{param_str}"

    except Exception as e:
        print(f"Error generating cover URL: {e}")
        return None


def refresh_song_cover(song_id: int, title: str, artist: str, album: str = "") -> tuple:
    """刷新歌曲封面，返回(cover_url, cover_path)"""
    # 删除旧封面文件
    old_filename = generate_cover_filename(song_id, title, artist, album)
    old_path = os.path.join(COVER_DIR, old_filename)
    if os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            print(f"Error removing old cover: {e}")

    # 获取新封面
    cover_path = save_cover_image(song_id, title, artist, album)
    cover_url = get_cover_url(song_id, title, artist, album)

    return cover_url, cover_path
