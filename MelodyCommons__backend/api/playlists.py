from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import crud
import schemas
from auth import get_current_user

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.get("/", response_model=List[schemas.Playlist])
def get_playlists(
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """获取所有歌单"""
    playlists = crud.get_playlists(db)
    return playlists


@router.get("/{playlist_id}", response_model=schemas.Playlist)
def get_playlist(
        playlist_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """获取单个歌单详情"""
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )
    return playlist


@router.post("/", response_model=schemas.Playlist)
def create_playlist(
        playlist: schemas.PlaylistCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """创建歌单"""
    try:
        return crud.create_playlist(db=db, playlist=playlist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create playlist"
        )


@router.put("/{playlist_id}", response_model=schemas.Playlist)
def update_playlist(
        playlist_id: int,
        playlist_update: schemas.PlaylistUpdate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """更新歌单信息"""
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    updated_playlist = crud.update_playlist(db, playlist_id=playlist_id, playlist_update=playlist_update)
    return updated_playlist


@router.delete("/{playlist_id}")
def delete_playlist(
        playlist_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """删除歌单"""
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    success = crud.delete_playlist(db, playlist_id=playlist_id)
    if success:
        return {"message": "Playlist deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete playlist"
        )


@router.post("/{playlist_id}/songs/{song_id}")
def add_song_to_playlist(
        playlist_id: int,
        song_id: int,
        order_index: int = None,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """添加歌曲到歌单"""
    # 检查歌单是否存在
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    # 检查歌曲是否存在
    song = crud.get_song(db, song_id=song_id)
    if song is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )

    # 添加歌曲到歌单
    result = crud.add_song_to_playlist(db, playlist_id=playlist_id, song_id=song_id, order_index=order_index)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Song already exists in playlist"
        )

    return {"message": "Song added to playlist successfully"}


@router.delete("/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist(
        playlist_id: int,
        song_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """从歌单移除歌曲"""
    # 检查歌单是否存在
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    success = crud.remove_song_from_playlist(db, playlist_id=playlist_id, song_id=song_id)
    if success:
        return {"message": "Song removed from playlist successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found in playlist"
        )


@router.get("/{playlist_id}/songs", response_model=List[schemas.SongInPlaylist])
def get_playlist_songs(
        playlist_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """获取歌单内歌曲（按顺序）"""
    # 检查歌单是否存在
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    playlist_songs = crud.get_playlist_songs(db, playlist_id=playlist_id)
    return [
        schemas.SongInPlaylist(
            song=ps.song,
            order_index=ps.order_index,
            added_at=ps.added_at
        )
        for ps in playlist_songs
    ]


@router.put("/{playlist_id}/songs/order")
def update_playlist_song_order(
        playlist_id: int,
        order_data: schemas.PlaylistSongOrder,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    """调整歌单内歌曲顺序"""
    # 检查歌单是否存在
    playlist = crud.get_playlist(db, playlist_id=playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found"
        )

    try:
        success = crud.update_playlist_song_order(db, playlist_id=playlist_id, song_orders=order_data.song_orders)
        if success:
            return {"message": "Playlist song order updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update playlist song order"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update playlist song order: {str(e)}"
        )
