from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
import models
import schemas
from auth import hash_password
import os
import random
from typing import Optional, List, Dict


# 用户CRUD
def create_user(db: Session, user: schemas.UserCreate):
    """创建用户"""
    db_user = models.User(
        username=user.username,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user(db: Session, user_id: int):
    """根据ID获取用户"""
    return db.query(models.User).filter(models.User.id == user_id).first()


# 歌曲CRUD
def create_song(db: Session, song: schemas.SongCreate, file_path: str, file_size: int, duration: int = 0):
    """创建歌曲"""
    db_song = models.Song(
        title=song.title,
        artist=song.artist,
        album=song.album,
        duration=duration,
        file_path=file_path,
        file_size=file_size
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_songs(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    """获取歌曲列表（支持搜索和分页）"""
    query = db.query(models.Song)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Song.title.like(search_filter)) |
            (models.Song.artist.like(search_filter)) |
            (models.Song.album.like(search_filter))
        )

    return query.offset(skip).limit(limit).all()


def get_song(db: Session, song_id: int):
    """根据ID获取歌曲"""
    return db.query(models.Song).filter(models.Song.id == song_id).first()


def increment_play_count(db: Session, song_id: int):
    """增加歌曲播放次数"""
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if db_song:
        db_song.play_count += 1
        db.commit()
        db.refresh(db_song)
    return db_song


def get_popular_songs(db: Session, limit: int = 10):
    """获取热门歌曲（按播放次数排序，播放次数相同时随机选择）"""
    # 首先获取所有歌曲并按播放次数分组
    all_songs = db.query(models.Song).order_by(desc(models.Song.play_count)).all()

    if not all_songs:
        return []

    # 如果歌曲总数小于等于限制，直接返回所有歌曲并随机打乱顺序
    if len(all_songs) <= limit:
        random.shuffle(all_songs)
        return all_songs

    # 按播放次数分组
    play_count_groups = {}
    for song in all_songs:
        count = song.play_count
        if count not in play_count_groups:
            play_count_groups[count] = []
        play_count_groups[count].append(song)

    # 从高到低遍历播放次数，随机选择歌曲直到达到limit
    result = []
    for count in sorted(play_count_groups.keys(), reverse=True):
        songs_in_group = play_count_groups[count]
        random.shuffle(songs_in_group)  # 随机打乱同播放次数的歌曲

        if len(result) + len(songs_in_group) <= limit:
            # 如果整组都可以加入，全部加入
            result.extend(songs_in_group)
        else:
            # 否则只加入需要的数量
            remaining = limit - len(result)
            result.extend(songs_in_group[:remaining])
            break

        if len(result) >= limit:
            break

    return result


def update_song(db: Session, song_id: int, song_update: schemas.SongUpdate):
    """更新歌曲信息"""
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if db_song:
        old_file_path = db_song.file_path
        old_cover_path = db_song.cover_path

        update_data = song_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_song, field, value)

        db.commit()
        db.refresh(db_song)

        # Check if file_path has changed and delete the old file
        if "file_path" in update_data and old_file_path and old_file_path != db_song.file_path:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # Check if cover_path has changed and delete the old cover
        if "cover_path" in update_data and old_cover_path and old_cover_path != db_song.cover_path:
            if os.path.exists(old_cover_path):
                os.remove(old_cover_path)

    return db_song


def update_song_cover(db: Session, song_id: int, cover_url: str = None, cover_path: str = None):
    """更新歌曲封面"""
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if db_song:
        old_cover_path = db_song.cover_path

        if cover_url:
            db_song.cover_url = cover_url
        if cover_path:
            db_song.cover_path = cover_path
        db.commit()
        db.refresh(db_song)

        if cover_path and old_cover_path and old_cover_path != cover_path:
            if os.path.exists(old_cover_path):
                os.remove(old_cover_path)
    return db_song


def delete_song(db: Session, song_id: int, attempt: int = 0):
    """删除歌曲，包含文件删除逻辑，并支持重试"""
    db_song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not db_song:
        # 如果在重试期间，其他请求已经删除了它，也视为成功
        return True

    # 尝试删除物理文件
    try:
        if db_song.file_path and os.path.exists(db_song.file_path):
            os.remove(db_song.file_path)
        if db_song.cover_path and os.path.exists(db_song.cover_path):
            os.remove(db_song.cover_path)
    except Exception as e:
        # 只在第一次尝试时打印错误，避免重试时信息泛滥
        if attempt == 0:
            print(f"Error deleting files: {e}")
        # 文件删除失败，返回 False 以便上层进行重试
        return False

    # 文件删除成功后，才删除数据库记录
    db.delete(db_song)
    db.commit()
    return True


# 歌单CRUD
def create_playlist(db: Session, playlist: schemas.PlaylistCreate):
    """创建歌单"""
    db_playlist = models.Playlist(
        name=playlist.name,
        description=playlist.description
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


def get_playlists(db: Session):
    """获取所有歌单"""
    return db.query(models.Playlist).order_by(desc(models.Playlist.created_at)).all()


def get_playlist(db: Session, playlist_id: int):
    """根据ID获取歌单"""
    return db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()


def get_playlist_with_songs(db: Session, playlist_id: int):
    """获取歌单及其歌曲"""
    return db.query(models.Playlist).options(
        joinedload(models.Playlist.songs).joinedload(models.PlaylistSong.song)
    ).filter(models.Playlist.id == playlist_id).first()


def update_playlist(db: Session, playlist_id: int, playlist_update: schemas.PlaylistUpdate):
    """更新歌单信息"""
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if db_playlist:
        update_data = playlist_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_playlist, field, value)
        db.commit()
        db.refresh(db_playlist)
    return db_playlist


def delete_playlist(db: Session, playlist_id: int):
    """删除歌单"""
    db_playlist = db.query(models.Playlist).filter(models.Playlist.id == playlist_id).first()
    if db_playlist:
        db.delete(db_playlist)
        db.commit()
        return True
    return False


# 歌单歌曲关联CRUD
def add_song_to_playlist(db: Session, playlist_id: int, song_id: int, order_index: int = None):
    """添加歌曲到歌单"""
    # 检查是否已存在
    existing = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()

    if existing:
        return None  # 已存在

    # 如果没有指定顺序，添加到末尾
    if order_index is None:
        max_order = db.query(func.max(models.PlaylistSong.order_index)).filter(
            models.PlaylistSong.playlist_id == playlist_id
        ).scalar() or -1
        order_index = max_order + 1

    db_playlist_song = models.PlaylistSong(
        playlist_id=playlist_id,
        song_id=song_id,
        order_index=order_index
    )
    db.add(db_playlist_song)
    db.commit()
    db.refresh(db_playlist_song)
    return db_playlist_song


def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int):
    """从歌单移除歌曲"""
    db_playlist_song = db.query(models.PlaylistSong).filter(
        models.PlaylistSong.playlist_id == playlist_id,
        models.PlaylistSong.song_id == song_id
    ).first()

    if db_playlist_song:
        db.delete(db_playlist_song)
        db.commit()
        return True
    return False


def get_playlist_songs(db: Session, playlist_id: int):
    """获取歌单内的歌曲（按顺序）"""
    return db.query(models.PlaylistSong).options(
        joinedload(models.PlaylistSong.song)
    ).filter(
        models.PlaylistSong.playlist_id == playlist_id
    ).order_by(models.PlaylistSong.order_index).all()


def update_playlist_song_order(db: Session, playlist_id: int, song_orders: List[Dict]):
    """更新歌单内歌曲顺序"""
    for order_data in song_orders:
        song_id = order_data.get("song_id")
        order_index = order_data.get("order_index")

        db_playlist_song = db.query(models.PlaylistSong).filter(
            models.PlaylistSong.playlist_id == playlist_id,
            models.PlaylistSong.song_id == song_id
        ).first()

        if db_playlist_song:
            db_playlist_song.order_index = order_index

    db.commit()
    return True
