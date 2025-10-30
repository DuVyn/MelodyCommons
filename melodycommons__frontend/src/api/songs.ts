import apiClient from './index'
import type {Song, SongCreate, SongUpdate} from '@/types'

export const songsApi = {
    // 获取歌曲列表
    getSongs: (params?: {
        page?: number
        limit?: number
        search?: string
    }): Promise<Song[]> => {
        return apiClient.get('/songs', {params})
    },

    // 获取单个歌曲
    getSong: (id: number): Promise<Song> => {
        return apiClient.get(`/songs/${id}`)
    },

    // 上传歌曲
    uploadSong: (file: File, metadata?: Partial<SongCreate>): Promise<Song> => {
        const formData = new FormData()
        formData.append('file', file)

        if (metadata?.title) {
            formData.append('title', metadata.title)
        }
        if (metadata?.artist) {
            formData.append('artist', metadata.artist)
        }
        if (metadata?.album) {
            formData.append('album', metadata.album)
        }

        return apiClient.post('/songs', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 更新歌曲信息
    updateSong: (id: number, data: SongUpdate): Promise<Song> => {
        return apiClient.put(`/songs/${id}`, data)
    },

    // 删除歌曲
    deleteSong: (id: number): Promise<void> => {
        return apiClient.delete(`/songs/${id}`)
    },

    // 刷新歌曲封面
    refreshCover: (id: number): Promise<Song> => {
        return apiClient.post(`/songs/${id}/cover/refresh`)
    },

    // 获取歌曲流媒体URL
    getStreamUrl: (id: number): string => {
        return `${apiClient.defaults.baseURL}/songs/${id}/stream`
    }
}