import {defineStore} from 'pinia'
import {ref} from 'vue'
import {playlistsApi} from '@/api/playlists'
import type {Playlist, PlaylistCreate, PlaylistUpdate, SongInPlaylist} from '@/types'

export const usePlaylistsStore = defineStore('playlists', () => {
    const playlists = ref<Playlist[]>([])
    const currentPlaylist = ref<Playlist | null>(null)
    const loading = ref(false)

    // 加载歌单列表
    const loadPlaylists = async () => {
        loading.value = true
        try {
            playlists.value = await playlistsApi.getPlaylists()
        } catch (error) {
            console.error('Failed to load playlists:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 获取单个歌单
    const getPlaylist = async (id: number): Promise<Playlist> => {
        try {
            const playlist = await playlistsApi.getPlaylist(id)
            currentPlaylist.value = playlist
            return playlist
        } catch (error) {
            console.error('Failed to get playlist:', error)
            throw error
        }
    }

    // 创建歌单
    const createPlaylist = async (data: PlaylistCreate): Promise<Playlist> => {
        try {
            const newPlaylist = await playlistsApi.createPlaylist(data)
            playlists.value.unshift(newPlaylist)
            return newPlaylist
        } catch (error) {
            console.error('Failed to create playlist:', error)
            throw error
        }
    }

    // 更新歌单
    const updatePlaylist = async (id: number, data: PlaylistUpdate): Promise<Playlist> => {
        try {
            const updatedPlaylist = await playlistsApi.updatePlaylist(id, data)

            // 更新本地数据
            const index = playlists.value.findIndex(p => p.id === id)
            if (index > -1) {
                playlists.value[index] = updatedPlaylist
            }

            if (currentPlaylist.value?.id === id) {
                currentPlaylist.value = updatedPlaylist
            }

            return updatedPlaylist
        } catch (error) {
            console.error('Failed to update playlist:', error)
            throw error
        }
    }

    // 删除歌单
    const deletePlaylist = async (id: number): Promise<void> => {
        try {
            await playlistsApi.deletePlaylist(id)

            // 从本地数据中移除
            const index = playlists.value.findIndex(p => p.id === id)
            if (index > -1) {
                playlists.value.splice(index, 1)
            }

            if (currentPlaylist.value?.id === id) {
                currentPlaylist.value = null
            }
        } catch (error) {
            console.error('Failed to delete playlist:', error)
            throw error
        }
    }

    // 获取歌单中的歌曲
    const getPlaylistSongs = async (id: number): Promise<SongInPlaylist[]> => {
        try {
            return await playlistsApi.getPlaylistSongs(id)
        } catch (error) {
            console.error('Failed to get playlist songs:', error)
            throw error
        }
    }

    // 添加歌曲到歌单
    const addSongToPlaylist = async (playlistId: number, songId: number): Promise<void> => {
        try {
            await playlistsApi.addSongToPlaylist(playlistId, songId)
        } catch (error) {
            console.error('Failed to add song to playlist:', error)
            throw error
        }
    }

    // 从歌单移除歌曲
    const removeSongFromPlaylist = async (playlistId: number, songId: number): Promise<void> => {
        try {
            await playlistsApi.removeSongFromPlaylist(playlistId, songId)
        } catch (error) {
            console.error('Failed to remove song from playlist:', error)
            throw error
        }
    }

    // 更新歌单中歌曲顺序
    const updatePlaylistSongOrder = async (
        playlistId: number,
        songOrders: Array<{ song_id: number; order_index: number }>
    ): Promise<void> => {
        try {
            await playlistsApi.updatePlaylistSongOrder(playlistId, {song_orders: songOrders})
        } catch (error) {
            console.error('Failed to update playlist song order:', error)
            throw error
        }
    }

    return {
        playlists,
        currentPlaylist,
        loading,
        loadPlaylists,
        getPlaylist,
        createPlaylist,
        updatePlaylist,
        deletePlaylist,
        getPlaylistSongs,
        addSongToPlaylist,
        removeSongFromPlaylist,
        updatePlaylistSongOrder
    }
})