import {defineStore} from 'pinia'
import {ref} from 'vue'
import {songsApi} from '@/api/songs'
import type {Song, SongCreate, SongUpdate} from '@/types'

interface SongsResponse {
    data: Song[]
    total: number
}

export const useSongsStore = defineStore('songs', () => {
    const songs = ref<Song[]>([])
    const total = ref(0)
    const loading = ref(false)
    const searchQuery = ref('')

    // 加载歌曲列表
    const loadSongs = async (params?: {
        page?: number
        limit?: number
        search?: string
    }) => {
        loading.value = true
        try {
            const response = await songsApi.getSongs(params)
            // 假设 API 返回的是数组或包含 data 和 total 的对象
            if (Array.isArray(response)) {
                songs.value = response
                total.value = response.length
            } else {
                songs.value = (response as SongsResponse).data || []
                total.value = (response as SongsResponse).total || 0
            }
        } catch (error) {
            console.error('Failed to load songs:', error)
            throw error
        } finally {
            loading.value = false
        }
    }

    // 获取单个歌曲
    const getSong = async (id: number): Promise<Song> => {
        try {
            return await songsApi.getSong(id)
        } catch (error) {
            console.error('Failed to get song:', error)
            throw error
        }
    }

    // 获取歌曲列表（用于其他组件）
    const getSongs = async (params?: {
        search?: string
        page?: number
        limit?: number
    }): Promise<Song[]> => {
        try {
            const response = await songsApi.getSongs(params)
            return Array.isArray(response) ? response : (response as SongsResponse).data || []
        } catch (error) {
            console.error('Failed to get songs:', error)
            throw error
        }
    }

    // 上传歌曲
    const uploadSong = async (file: File, metadata?: Partial<SongCreate>): Promise<Song> => {
        try {
            return await songsApi.uploadSong(file, metadata)
        } catch (error) {
            console.error('Failed to upload song:', error)
            throw error
        }
    }

    // 更新歌曲信息
    const updateSong = async (id: number, data: SongUpdate): Promise<Song> => {
        try {
            const updatedSong = await songsApi.updateSong(id, data)

            // 更新本地数据
            const index = songs.value.findIndex(song => song.id === id)
            if (index > -1) {
                songs.value[index] = updatedSong
            }

            return updatedSong
        } catch (error) {
            console.error('Failed to update song:', error)
            throw error
        }
    }

    // 删除歌曲
    const deleteSong = async (id: number): Promise<void> => {
        try {
            await songsApi.deleteSong(id)

            // 从本地数据中移除
            const index = songs.value.findIndex(song => song.id === id)
            if (index > -1) {
                songs.value.splice(index, 1)
                total.value--
            }
        } catch (error) {
            console.error('Failed to delete song:', error)
            throw error
        }
    }

    // 刷新歌曲封面
    const refreshCover = async (id: number): Promise<Song> => {
        try {
            const updatedSong = await songsApi.refreshCover(id)

            // 更新本地数据
            const index = songs.value.findIndex(song => song.id === id)
            if (index > -1) {
                songs.value[index] = updatedSong
            }

            return updatedSong
        } catch (error) {
            console.error('Failed to refresh cover:', error)
            throw error
        }
    }

    // 设置搜索查询
    const setSearchQuery = (query: string) => {
        searchQuery.value = query
    }

    return {
        songs,
        total,
        loading,
        searchQuery,
        loadSongs,
        getSong,
        getSongs,
        uploadSong,
        updateSong,
        deleteSong,
        refreshCover,
        setSearchQuery
    }
})