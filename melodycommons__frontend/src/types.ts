export interface User {
    id: number
    username: string
}

export interface UserCreate {
    username: string
    password: string
}

export interface Token {
    access_token: string
    token_type: string
}

export interface Song {
    id: number
    title: string
    artist: string
    album: string | null
    duration: number
    file_path: string
    file_size: number | null
    cover_url: string | null
    cover_path: string | null
    created_at: string
    updated_at: string
}

export interface SongCreate {
    title: string
    artist: string
    album?: string
}

export interface SongUpdate {
    title?: string
    artist?: string
    album?: string
}

export interface Playlist {
    id: number
    name: string
    description: string | null
    created_at: string
}

export interface PlaylistCreate {
    name: string
    description?: string
}

export interface PlaylistUpdate {
    name?: string
    description?: string
}

export interface SongInPlaylist {
    song: Song
    order_index: number
    added_at: string
}

export interface PlaylistWithSongs extends Playlist {
    songs: SongInPlaylist[]
}

export interface PlaylistSongOrder {
    song_orders: Array<{
        song_id: number
        order_index: number
    }>
}

export interface ErrorResponse {
    error: string
    message: string
    details: Record<string, any>
}