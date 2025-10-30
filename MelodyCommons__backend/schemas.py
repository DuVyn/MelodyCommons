from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# 用户相关
class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# 歌曲相关
class SongCreate(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None


class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


class Song(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    duration: int
    file_path: str
    file_size: Optional[int]
    cover_url: Optional[str]
    cover_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SongInPlaylist(BaseModel):
    song: Song
    order_index: int
    added_at: datetime

    class Config:
        from_attributes = True


# 歌单相关
class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Playlist(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistWithSongs(BaseModel):
    id: int
    name: str
    description: Optional[str]
    songs: List[SongInPlaylist] = []
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistSongOrder(BaseModel):
    song_orders: List[Dict[str, int]]


# 通用响应
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Dict = {}
