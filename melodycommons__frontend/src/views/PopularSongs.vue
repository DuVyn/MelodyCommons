<template>
  <div class="popular-songs-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">🔥 热门歌曲</h1>
        <p class="page-subtitle">根据播放次数推荐最受欢迎的歌曲</p>
      </div>
      <div class="header-right">
        <el-button @click="fetchPopularSongs" :icon="Refresh" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && popularSongs.length === 0" class="loading-container">
      <el-icon class="is-loading" :size="40">
        <Loading/>
      </el-icon>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-empty :description="error">
        <el-button type="primary" @click="fetchPopularSongs">重试</el-button>
      </el-empty>
    </div>

    <!-- 歌曲列表 -->
    <div v-else class="songs-content">
      <div class="songs-table-header">
        <div class="header-cell rank">排名</div>
        <div class="header-cell title">标题</div>
        <div class="header-cell artist">艺术家</div>
        <div class="header-cell album">专辑</div>
        <div class="header-cell play-count">播放次数</div>
        <div class="header-cell duration">时长</div>
      </div>

      <div class="songs-table-body">
        <div
            v-for="(song, index) in popularSongs"
            :key="song.id"
            class="song-row"
            :class="{
              'playing': currentSong?.id === song.id,
              'top-rank': index < 3
            }"
            @click="handlePlaySong(song)"
        >
          <div class="row-cell rank">
            <div class="rank-number" :class="`rank-${index + 1}`">
              {{ index + 1 }}
            </div>
          </div>

          <div class="row-cell title">
            <div class="play-indicator">
              <el-icon v-if="currentSong?.id === song.id && isPlaying" class="playing-icon">
                <VideoPlay/>
              </el-icon>
              <el-icon v-else-if="currentSong?.id === song.id && playerLoading" class="loading-icon">
                <Loading/>
              </el-icon>
              <el-icon v-else class="play-icon">
                <VideoPlay/>
              </el-icon>
            </div>

            <div class="song-cover">
              <img
                  v-if="song.cover_url"
                  :src="song.cover_url"
                  :alt="song.title"
                  @error="handleImageError"
              />
              <div v-else class="cover-placeholder">
                <el-icon>
                  <Mic/>
                </el-icon>
              </div>
            </div>

            <div class="song-info">
              <div class="song-title">{{ song.title }}</div>
              <div class="song-subtitle">{{ song.artist }}</div>
            </div>
          </div>

          <div class="row-cell artist">{{ song.artist }}</div>
          <div class="row-cell album">{{ song.album || '未知专辑' }}</div>
          <div class="row-cell play-count">
            <el-icon class="play-count-icon">
              <VideoPlay/>
            </el-icon>
            <span>{{ formatPlayCount(song.play_count) }}</span>
          </div>
          <div class="row-cell duration">{{ formatDuration(song.duration) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, onMounted, computed} from 'vue'
import {ElMessage} from 'element-plus'
import {VideoPlay, Loading, Mic, Refresh} from '@element-plus/icons-vue'
import {usePlayerStore} from '@/stores/player'
import apiClient from '@/api/index'
import type {Song} from '@/types'

const playerStore = usePlayerStore()

const popularSongs = ref<Song[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const currentSong = computed(() => playerStore.currentSong)
const isPlaying = computed(() => playerStore.isPlaying)
const playerLoading = computed(() => playerStore.loading)

// 获取热门歌曲
async function fetchPopularSongs() {
  try {
    loading.value = true
    error.value = null

    popularSongs.value = await apiClient.get('/songs/popular/top?limit=10')
  } catch (e: any) {
    const errorMsg = e.response?.data?.detail || e.message || '获取热门歌曲失败'
    error.value = errorMsg
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 播放歌曲
function handlePlaySong(song: Song) {
  playerStore.playWithPlaylist(song, popularSongs.value)
}

// 格式化播放次数
function formatPlayCount(count: number): string {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`
  }
  return count.toString()
}

// 格式化时长
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 处理图片加载错误
function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement
  target.style.display = 'none'
}

onMounted(() => {
  fetchPopularSongs()
})
</script>

<style scoped>
.popular-songs-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #1f1f1f;
}

.page-subtitle {
  font-size: 14px;
  color: #8e8e93;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #8e8e93;
}

.songs-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.songs-table-header {
  display: grid;
  grid-template-columns: 60px 2fr 1fr 1fr 120px 100px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  font-weight: 600;
  color: #8e8e93;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.songs-table-body {
  flex: 1;
  overflow-y: auto;
}

.song-row {
  display: grid;
  grid-template-columns: 60px 2fr 1fr 1fr 120px 100px;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f7;
  cursor: pointer;
  transition: background-color 0.2s;
  align-items: center;
}

.song-row:hover {
  background-color: #f9f9fb;
}

.song-row.playing {
  background-color: rgba(0, 122, 255, 0.05);
}

.song-row.top-rank {
  background-color: #fffbf0;
}

.song-row.top-rank:hover {
  background-color: #fff8e1;
}

.row-cell {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #1f1f1f;
  overflow: hidden;
}

.row-cell.rank {
  justify-content: center;
}

.rank-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  border-radius: 4px;
  background: #f5f5f7;
  color: #8e8e93;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #fff;
  box-shadow: 0 2px 8px rgba(192, 192, 192, 0.3);
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e8b17a);
  color: #fff;
  box-shadow: 0 2px 8px rgba(205, 127, 50, 0.3);
}

.row-cell.title {
  gap: 12px;
}

.play-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.song-row:hover .play-indicator {
  opacity: 1;
}

.song-row.playing .play-indicator {
  opacity: 1;
}

.play-icon {
  color: #007aff;
}

.playing-icon {
  color: #007aff;
  animation: pulse 1.5s ease-in-out infinite;
}

.loading-icon {
  color: #007aff;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.song-cover {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f7;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 20px;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.song-subtitle {
  font-size: 13px;
  color: #8e8e93;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-cell.artist,
.row-cell.album {
  color: #8e8e93;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-cell.play-count {
  gap: 4px;
  color: #007aff;
  font-weight: 500;
}

.play-count-icon {
  font-size: 14px;
}

.row-cell.duration {
  color: #8e8e93;
  font-variant-numeric: tabular-nums;
}

/* 滚动条样式 */
.songs-table-body::-webkit-scrollbar {
  width: 8px;
}

.songs-table-body::-webkit-scrollbar-track {
  background: transparent;
}

.songs-table-body::-webkit-scrollbar-thumb {
  background: #d1d1d6;
  border-radius: 4px;
}

.songs-table-body::-webkit-scrollbar-thumb:hover {
  background: #b4b4b9;
}

/* 响应式 */
@media (max-width: 1200px) {
  .songs-table-header,
  .song-row {
    grid-template-columns: 60px 2fr 1fr 120px 100px;
  }

  .row-cell.album {
    display: none;
  }
}

@media (max-width: 768px) {
  .songs-table-header,
  .song-row {
    grid-template-columns: 50px 1fr 80px;
  }

  .row-cell.artist,
  .row-cell.album,
  .row-cell.duration {
    display: none;
  }
}
</style>

