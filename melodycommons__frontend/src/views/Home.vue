<template>
  <div class="home-page">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎来到 MelodyCommons</h1>
      <p class="welcome-subtitle">您的共享音乐库</p>
    </div>

    <div class="stats-section">
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon>
                  <Headset/>
                </el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ songCount }}</div>
                <div class="stats-label">首歌曲</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon>
                  <Menu/>
                </el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ playlistCount }}</div>
                <div class="stats-label">个歌单</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon">
                <el-icon>
                  <Clock/>
                </el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-number">{{ formatTotalDuration }}</div>
                <div class="stats-label">总时长</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="actions-section">
      <h2>快速开始</h2>
      <el-row :gutter="24">
        <el-col :span="12">
          <el-card class="action-card" @click="$router.push('/songs')">
            <div class="action-content">
              <div class="action-icon">
                <el-icon>
                  <Mic/>
                </el-icon>
              </div>
              <div class="action-info">
                <h3>浏览音乐库</h3>
                <p>查看所有已上传的歌曲</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="action-card" @click="showUploadDialog = true">
            <div class="action-content">
              <div class="action-icon">
                <el-icon>
                  <Upload/>
                </el-icon>
              </div>
              <div class="action-info">
                <h3>上传音乐</h3>
                <p>添加新的音乐文件到库中</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="recent-section" v-if="recentSongs.length > 0">
      <h2>最近添加</h2>
      <div class="recent-songs">
        <div
            v-for="song in recentSongs"
            :key="song.id"
            class="recent-song-item"
            @click="playSong(song)"
        >
          <img
              :src="song.cover_url || '/default-cover.png'"
              :alt="song.title"
              class="recent-song-cover"
              @error="handleImageError"
          />
          <div class="recent-song-info">
            <div class="recent-song-title">{{ song.title }}</div>
            <div class="recent-song-artist">{{ song.artist }}</div>
          </div>
          <div class="recent-song-actions">
            <el-button circle @click.stop="playSong(song)">
              <el-icon>
                <VideoPlay/>
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
        v-model="showUploadDialog"
        title="上传音乐"
        width="600px"
        @close="showUploadDialog = false"
    >
      <SongUpload @success="handleUploadSuccess"/>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted} from 'vue'
import {ElMessage} from 'element-plus'
import {
  Headset,
  Menu,
  Clock,
  Mic,
  Upload,
  VideoPlay
} from '@element-plus/icons-vue'
import {useSongsStore} from '@/stores/songs'
import {usePlaylistsStore} from '@/stores/playlists'
import {usePlayerStore} from '@/stores/player'
import SongUpload from '@/components/Song/SongUpload.vue'
import type {Song} from '@/types'

const songsStore = useSongsStore()
const playlistsStore = usePlaylistsStore()
const playerStore = usePlayerStore()

const showUploadDialog = ref(false)
const recentSongs = ref<Song[]>([])

const songCount = computed(() => songsStore.total)
const playlistCount = computed(() => playlistsStore.playlists.length)

const formatTotalDuration = computed(() => {
  const totalSeconds = songsStore.songs.reduce((total, song) => total + (song.duration || 0), 0)
  if (totalSeconds === 0) return '0分钟'

  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
})

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/default-cover.png'
}

const playSong = (song: Song) => {
  playerStore.play(song)
  ElMessage.success(`开始播放《${song.title}》`)
}

const handleUploadSuccess = (_count: number) => {
  showUploadDialog.value = false
  loadData() // 重新加载数据
}

const loadData = async () => {
  try {
    // 加载歌曲数据
    await songsStore.loadSongs()

    // 加载歌单数据
    await playlistsStore.loadPlaylists()

    // 获取最近添加的歌曲（最新的5首）
    recentSongs.value = songsStore.songs
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5)

  } catch (error) {
    console.error('Failed to load home data:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 48px;
}

.welcome-title {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 12px 0;
}

.welcome-subtitle {
  font-size: 18px;
  color: #909399;
  margin: 0;
}

.stats-section {
  margin-bottom: 48px;
}

.stats-card {
  height: 120px;
  cursor: default;
}

.stats-content {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 20px;
}

.stats-icon {
  flex: 0 0 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stats-info {
  flex: 1;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.actions-section {
  margin-bottom: 48px;
}

.actions-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px 0;
}

.action-card {
  height: 120px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.action-content {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 20px;
}

.action-icon {
  flex: 0 0 60px;
  height: 60px;
  background: linear-gradient(135deg, #409eff 0%, #36cfc9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.action-info {
  flex: 1;
}

.action-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.action-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.recent-section {
  margin-bottom: 48px;
}

.recent-section h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px 0;
}

.recent-songs {
  display: grid;
  gap: 16px;
}

.recent-song-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.recent-song-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.recent-song-cover {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  background: #f5f7fa;
}

.recent-song-info {
  flex: 1;
  min-width: 0;
}

.recent-song-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.recent-song-artist {
  font-size: 14px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-song-actions {
  flex: 0 0 auto;
  opacity: 0;
  transition: opacity 0.3s;
}

.recent-song-item:hover .recent-song-actions {
  opacity: 1;
}
</style>