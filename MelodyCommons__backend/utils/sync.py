import os
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def sync_database_with_static_files():
    """
    同步数据库和static文件夹，删除数据库中存在但static文件夹中不存在的歌曲记录。
    """
    db: Session = SessionLocal()
    try:
        all_songs = db.query(models.Song).all()
        songs_to_delete = []

        print("开始同步数据库与static文件夹...")

        for song in all_songs:
            # 检查歌曲文件是否存在
            if song.file_path and not os.path.exists(song.file_path):
                print(f"歌曲 '{song.title}' (ID: {song.id}) 的文件不存在，路径: {song.file_path}。准备删除...")
                songs_to_delete.append(song)
                continue  # 文件不存在，无需检查封面

            # 如果歌曲文件存在，再检查封面文件
            if song.cover_path and not os.path.exists(song.cover_path):
                print(f"歌曲 '{song.title}' (ID: {song.id}) 的封面文件不存在，路径: {song.cover_path}。准备删除...")
                songs_to_delete.append(song)

        if not songs_to_delete:
            print("数据库与static文件夹内容一致，无需同步。")
            return

        # 在删除歌曲之前，先从 playlist_songs 表中删除关联记录
        song_ids_to_delete = {s.id for s in songs_to_delete}
        db.query(models.PlaylistSong).filter(models.PlaylistSong.song_id.in_(song_ids_to_delete)).delete(synchronize_session=False)

        # 执行删除
        for song in songs_to_delete:
            db.delete(song)

        db.commit()
        print(f"同步完成，共删除了 {len(songs_to_delete)} 条无效的歌曲记录。")

    except Exception as e:
        print(f"同步过程中发生错误: {e}")
        db.rollback()
    finally:
        db.close()

