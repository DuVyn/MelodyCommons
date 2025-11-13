from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, BIGINT, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    album = Column(String(255), nullable=True)
    duration = Column(Integer, default=0)
    file_path = Column(String(500), nullable=False, unique=True)
    file_size = Column(BIGINT, nullable=True)
    cover_url = Column(String(500), nullable=True)
    cover_path = Column(String(500), nullable=True)
    play_count = Column(Integer, default=0, nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    songs = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    order_index = Column(Integer, default=0)
    added_at = Column(TIMESTAMP, default=func.current_timestamp())

    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song")

    __table_args__ = (UniqueConstraint('playlist_id', 'song_id', name='unique_playlist_song'),)
