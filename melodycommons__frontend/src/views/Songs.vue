<template>
  <div class="songs-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">音乐库</h1>
        <p class="page-subtitle">共 {{ songs.length }} 首歌曲</p>
      </div>
      <div class="header-right">
        <el-button
            type="primary"
            @click="showUpload = true"
            :icon="Upload"
        >
          上传音乐
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
          v-model="searchQuery"
          placeholder="搜索歌曲、艺术家、专辑..."
          :prefix-icon="Search"
          @input="handleSearch"
          clearable
          size="large"
          style="max-width: 500px;"
      />
    </div>

    <!-- 歌曲列表 -->
    <div class="songs-content">
      <div class="songs-table-header">
        <div class="header-cell title">标题</div>
        <div class="header-cell artist">艺术家</div>
        <div class="header-cell album">专辑</div>
        <div class="header-cell duration">时长</div>
        <div class="header-cell actions">操作</div>
      </div>

      <div
          class="songs-table-body"
          ref="scrollContainer"
          @scroll="handleScroll"
      >
        <div
            v-for="song in songs"
            :key="song.id"
            class="song-row"
            :class="{
            'playing': currentSong?.id === song.id,
            'loading': currentSong?.id === song.id && playerLoading
          }"
            @click="playSong(song)"
        >
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
          <div class="row-cell duration">{{ formatDuration(song.duration) }}</div>

          <div class="row-cell actions">
            <el-dropdown trigger="click">
              <el-button text :icon="MoreFilled" @click.stop/>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="editSong(song)">
                    <el-icon>
                      <Edit/>
                    </el-icon>
                    编辑信息
                  </el-dropdown-item>
                  <el-dropdown-item @click="refreshCover(song)">
                    <el-icon>
                      <Refresh/>
                    </el-icon>
                    刷新封面
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteSong(song)" divided>
                    <el-icon>
                      <Delete/>
                    </el-icon>
                    删除歌曲
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <!-- 加载更多指示器 -->
        <div v-if="loading" class="loading-indicator">
          <el-icon class="is-loading">
            <Loading/>
          </el-icon>
          <span>加载中...</span>
        </div>

        <!-- 没有更多数据提示 -->
        <div v-if="!hasMore && songs.length > 0" class="no-more-data">
          已显示全部歌曲
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && songs.length === 0" class="empty-state">
          <el-icon>
            <DocumentDelete/>
          </el-icon>
          <p>{{ searchQuery ? '没有找到匹配的歌曲' : '还没有上传任何音乐' }}</p>
          <el-button v-if="!searchQuery" type="primary" @click="showUpload = true">
            上传第一首歌曲
          </el-button>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
        v-model="showUpload"
        title="上传音乐"
        width="600px"
        :close-on-click-modal="false"
    >
      <SongUpload @success="handleUploadSuccess"/>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog
        v-model="showEdit"
        title="编辑歌曲信息"
        width="500px"
        :close-on-click-modal="false"
    >
      <SongEdit
          v-if="editingSong"
          v-model="showEdit"
          :song="editingSong"
          @success="handleEditSuccess"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {
  Search,
  Upload,
  VideoPlay,
  MoreFilled,
  Edit,
  Refresh,
  Delete,
  DocumentDelete,
  Mic,
  Loading
} from '@element-plus/icons-vue'

import type {Song} from '@/types'
import apiClient from '@/api'
import {usePlayerStore} from '@/stores/player'
import SongUpload from '@/components/Song/SongUpload.vue'
import SongEdit from '@/components/Song/SongEdit.vue'

const playerStore = usePlayerStore()

const songs = ref<Song[]>([])
const loading = ref(false)
const searchQuery = ref('')
const showUpload = ref(false)
const showEdit = ref(false)
const editingSong = ref<Song | null>(null)
const scrollContainer = ref<HTMLElement>()

const currentPage = ref(1)
const pageSize = ref(20)
const hasMore = ref(true)

let searchTimeout: NodeJS.Timeout | null = null

const currentSong = computed(() => playerStore.currentSong)
const isPlaying = computed(() => playerStore.isPlaying)
const playerLoading = computed(() => playerStore.loading)

const loadSongs = async (reset = false) => {
  if (loading.value) return
  loading.value = true
  try {
    const pageToFetch = reset ? 1 : currentPage.value
    const params: any = {page: pageToFetch, limit: pageSize.value}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await apiClient.get('/songs', {params})
    const songsData = Array.isArray(response) ? response : []

    hasMore.value = songsData.length === pageSize.value

    if (reset) {
      songs.value = songsData
      // === 关键修复：重置加载后，下一次应该从第2页开始加载 ===
      currentPage.value = 2
    } else {
      songs.value.push(...songsData)
      if (hasMore.value) {
        currentPage.value++
      }
    }
  } catch (error) {
    console.error('加载歌曲失败:', error)
    ElMessage.error('加载歌曲失败')
  } finally {
    loading.value = false
  }
}

const handleScroll = async () => {
  if (!scrollContainer.value || loading.value || !hasMore.value) return
  const {scrollTop, scrollHeight, clientHeight} = scrollContainer.value
  if (scrollTop + clientHeight >= scrollHeight - 100) {
    await loadSongs()
  }
}

const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(async () => {
    await loadSongs(true)
  }, 300)
}

const playSong = (song: Song) => {
  playerStore.playWithPlaylist(song, songs.value)
}

const editSong = (song: Song) => {
  editingSong.value = song;
  showEdit.value = true
}

const refreshCover = async (song: Song) => {
  try {
    await apiClient.post(`/songs/${song.id}/cover/refresh`)
    ElMessage.success('封面刷新成功')
    await loadSongs(true)
  } catch (error) {
    console.error('刷新封面失败:', error)
    ElMessage.error('刷新封面失败')
  }
}

const deleteSong = async (song: Song) => {
  try {
    await ElMessageBox.confirm(`确定要删除歌曲《${song.title}》吗？此操作不可恢复。`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })

    playerStore.removeFromPlaylist(song.id)

    await apiClient.delete(`/songs/${song.id}`)
    ElMessage.success('歌曲删除成功')
    const index = songs.value.findIndex(s => s.id === song.id)
    if (index > -1) {
      songs.value.splice(index, 1)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除歌曲失败:', error);
      ElMessage.error('删除歌曲失败')
    }
  }
}

const handleUploadSuccess = () => {
  showUpload.value = false;
  loadSongs(true)
}
const handleEditSuccess = () => {
  showEdit.value = false;
  editingSong.value = null;
  loadSongs(true)
}

const formatDuration = (seconds: number): string => {
  if (!seconds || seconds === 0) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.style.display = 'none'
}

onMounted(() => {
  loadSongs(true)
})
</script>

<style scoped>
/* === 修改开始 === */
.songs-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: rgba(255, 255, 255, 0.6); /* 半透明背景 */
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2); /* 添加边框以统一风格 */
}

.page-header {
  border-bottom: 1px solid rgba(228, 231, 237, 0.5); /* 半透明边框 */
}

.search-bar {
  border-bottom: 1px solid rgba(240, 242, 245, 0.5); /* 半透明边框 */
}

.songs-table-header {
  background: transparent; /* 移除表头背景色 */
  border-bottom: 1px solid rgba(228, 231, 237, 0.5); /* 半透明边框 */
}

.song-row {
  border-bottom: 1px solid rgba(240, 242, 245, 0.5); /* 半透明边框 */
}

.song-row:hover {
  background-color: rgba(0, 0, 0, 0.03); /* 悬浮效果 */
}

.song-row.playing {
  background-color: rgba(64, 158, 255, 0.1); /* 播放中效果 */
  border-color: transparent; /* 移除播放中的边框 */
}

/* === 修改结束 === */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  flex-shrink: 0;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.search-bar {
  padding: 20px 32px;
  flex-shrink: 0;
}

.songs-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.songs-table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 100px 120px;
  gap: 16px;
  padding: 16px 32px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.songs-table-body {
  flex: 1;
  overflow-y: auto;
  padding: 0 32px;
}

.song-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 100px 120px;
  gap: 16px;
  padding: 12px 0;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  margin-bottom: 4px;
}

.row-cell {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
  overflow: hidden;
}

.row-cell.title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-indicator {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-row:hover .play-indicator,
.song-row.playing .play-indicator {
  opacity: 1;
}

.playing-icon {
  color: #409eff;
  animation: pulse 1.5s infinite;
}

.loading-icon {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.song-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  overflow: hidden;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  color: #c0c4cc;
  font-size: 16px;
}

.song-info {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
}

.song-subtitle {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-cell.actions {
  opacity: 0;
  transition: opacity 0.3s;
  gap: 4px;
}

.song-row:hover .row-cell.actions {
  opacity: 1;
}

.loading-indicator, .no-more-data, .empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #909399;
  font-size: 14px;
  text-align: center;
}

.empty-state {
  flex-direction: column;
  padding: 60px 20px;
  flex: 1;
}

.empty-state .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #dcdfe6;
}

.empty-state p {
  margin: 0 0 20px 0;
  font-size: 16px;
}

/* 自定义滚动条 */
.songs-table-body::-webkit-scrollbar {
  width: 6px;
}

.songs-table-body::-webkit-scrollbar-track {
  background: transparent;
}

.songs-table-body::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.songs-table-body::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

</style>