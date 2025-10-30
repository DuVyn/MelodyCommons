from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import mimetypes
import time

from database import get_db
import crud
import schemas
from auth import get_current_user, verify_token_string, get_user_by_token
from utils.audio import extract_audio_metadata, is_valid_audio_file, MAX_AUDIO_SIZE
from utils.file import save_uploaded_file, get_file_size, AUDIO_DIR
from utils.cover import save_cover_image, get_cover_url, refresh_song_cover

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/", response_model=List[schemas.Song])
def get_songs(
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=100),
        search: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """获取所有歌曲（支持分页和搜索）"""
    skip = (page - 1) * limit
    songs = crud.get_songs(db, skip=skip, limit=limit, search=search)
    return songs


@router.get("/{song_id}", response_model=schemas.Song)
def get_song(
        song_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """获取单个歌曲详情"""
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    return song


@router.get("/{song_id}/stream")
async def stream_song(
        song_id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """流式播放歌曲 - 支持查询参数认证和Header认证"""

    user = None

    # 方法1: 尝试从查询参数获取token（用于音频播放）
    token = request.query_params.get("token")
    if token:
        try:
            username = verify_token_string(token)
            user = get_user_by_token(username, db)
        except Exception as e:
            print(f"Token validation error: {e}")
            pass

    # 方法2: 如果查询参数认证失败，尝试从Authorization头获取token
    if not user:
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                username = verify_token_string(token)
                user = get_user_by_token(username, db)
        except Exception as e:
            print(f"Authorization header error: {e}")
            pass

    # 如果两种认证方式都失败
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required"
        )

    # 获取歌曲信息
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    # 检查文件是否存在
    if not os.path.exists(song.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song file not found"
        )

    # 获取文件信息
    file_size = os.path.getsize(song.file_path)
    file_ext = os.path.splitext(song.file_path)[1].lower()

    # 确定媒体类型
    media_type_map = {
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.wav': 'audio/wav'
    }
    media_type = media_type_map.get(file_ext, 'audio/mpeg')

    # 处理Range请求（支持音频播放器的跳转功能）
    range_header = request.headers.get('range')

    if range_header:
        # 解析Range头
        try:
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1

            # 确保范围有效
            start = max(0, start)
            end = min(file_size - 1, end)
            content_length = end - start + 1

            def iterfile_range(file_path: str, start: int, end: int):
                with open(file_path, "rb") as file_like:
                    file_like.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk_size = min(8192, remaining)
                        chunk = file_like.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": media_type,
                "Cache-Control": "public, max-age=3600",
            }

            return StreamingResponse(
                iterfile_range(song.file_path, start, end),
                status_code=206,  # Partial Content
                headers=headers
            )
        except (ValueError, IndexError) as e:
            print(f"Range header parsing error: {e}")
            # 如果Range头解析失败，返回完整文件
            pass

    # 返回完整文件
    def iterfile(file_path: str):
        with open(file_path, "rb") as file_like:
            while chunk := file_like.read(8192):
                yield chunk

    headers = {
        "Content-Length": str(file_size),
        "Accept-Ranges": "bytes",
        "Content-Type": media_type,
        "Cache-Control": "public, max-age=3600",
    }

    return StreamingResponse(
        iterfile(song.file_path),
        headers=headers
    )


@router.post("/", response_model=schemas.Song)
def upload_song(
        file: UploadFile = File(...),
        title: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """上传歌曲文件"""
    # 验证文件格式
    if not is_valid_audio_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported audio format"
        )

    # 检查文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到开头

    if file_size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )

    try:
        # 保存文件
        file_path = save_uploaded_file(file, AUDIO_DIR)

        # 提取元数据
        metadata = extract_audio_metadata(file_path)

        # 使用提供的信息或元数据
        song_data = schemas.SongCreate(
            title=title or metadata.get("title", "Unknown Title"),
            artist=artist or metadata.get("artist", "Unknown Artist"),
            album=album or metadata.get("album", "")
        )

        # 创建歌曲记录
        song = crud.create_song(
            db=db,
            song=song_data,
            file_path=file_path,
            file_size=file_size,
            duration=metadata.get("duration", 0)
        )

        # 尝试获取封面
        try:
            cover_url, cover_path = refresh_song_cover(
                song.id, song.title, song.artist, song.album
            )
            if cover_url or cover_path:
                crud.update_song_cover(db, song.id, cover_url, cover_path)
                db.refresh(song)
        except Exception as e:
            print(f"Failed to get cover for song {song.id}: {e}")

        return song

    except Exception as e:
        # 如果出错，清理已保存的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload song: {str(e)}"
        )


@router.put("/{song_id}", response_model=schemas.Song)
def update_song(
        song_id: int,
        song_update: schemas.SongUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """更新歌曲信息"""
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    updated_song = crud.update_song(db, song_id=song_id, song_update=song_update)
    return updated_song


@router.delete("/{song_id}")
def delete_song(
        song_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """删除歌曲，包含重试逻辑以处理文件锁定"""
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    max_retries = 3
    retry_delay = 0.1  # 100毫秒

    for attempt in range(max_retries):
        success = crud.delete_song(db, song_id=song_id, attempt=attempt)
        if success:
            return {"message": "Song deleted successfully"}

        print(f"Delete attempt {attempt + 1} failed, retrying in {retry_delay}s...")
        time.sleep(retry_delay)

    # 如果重试多次后仍然失败
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to delete song after multiple attempts. The file might be locked."
    )


@router.post("/{song_id}/cover/refresh", response_model=schemas.Song)
def refresh_cover(
        song_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """手动刷新歌曲封面"""
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    try:
        cover_url, cover_path = refresh_song_cover(
            song.id, song.title, song.artist, song.album
        )
        updated_song = crud.update_song_cover(db, song.id, cover_url, cover_path)
        return updated_song
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh cover: {str(e)}"
        )
