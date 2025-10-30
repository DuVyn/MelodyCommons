import apiClient from './index'
import type {
    Playlist,
    PlaylistCreate,
    PlaylistUpdate,
    SongInPlaylist,
    PlaylistSongOrder
} from '@/types'

export const playlistsApi = {
    // 获取歌单列表
    getPlaylists: (): Promise<Playlist[]> => {
        return apiClient.get('/playlists')
    },

    // 获取单个歌单
    getPlaylist: (id: number): Promise<Playlist> => {
        return apiClient.get(`/playlists/${id}`)
    },

    // 创建歌单
    createPlaylist: (data: PlaylistCreate): Promise<Playlist> => {
        return apiClient.post('/playlists', data)
    },

    // 更新歌单
    updatePlaylist: (id: number, data: PlaylistUpdate): Promise<Playlist> => {
        return apiClient.put(`/playlists/${id}`, data)
    },

    // 删除歌单
    deletePlaylist: (id: number): Promise<void> => {
        return apiClient.delete(`/playlists/${id}`)
    },

    // 获取歌单中的歌曲
    getPlaylistSongs: (id: number): Promise<SongInPlaylist[]> => {
        return apiClient.get(`/playlists/${id}/songs`)
    },

    // 添加歌曲到歌单
    addSongToPlaylist: (playlistId: number, songId: number): Promise<void> => {
        return apiClient.post(`/playlists/${playlistId}/songs/${songId}`)
    },

    // 从歌单移除歌曲
    removeSongFromPlaylist: (playlistId: number, songId: number): Promise<void> => {
        return apiClient.delete(`/playlists/${playlistId}/songs/${songId}`)
    },

    // 更新歌单中歌曲顺序
    updatePlaylistSongOrder: (id: number, data: PlaylistSongOrder): Promise<void> => {
        return apiClient.put(`/playlists/${id}/songs/order`, data)
    }
}