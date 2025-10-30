<template>
  <div class="playlist-detail" v-loading="loading">
    <div v-if="playlist" class="playlist-content">
      <!-- 歌单头部信息 -->
      <div class="playlist-header">
        <div class="playlist-cover">
          <div class="cover-placeholder">
            <el-icon>
              <Menu/>
            </el-icon>
          </div>
        </div>

        <div class="playlist-info">
          <h1 class="playlist-title">{{ playlist.name }}</h1>
          <p class="playlist-description" v-if="playlist.description">
            {{ playlist.description }}
          </p>
          <div class="playlist-meta">
            <span class="song-count">{{ songs.length }} 首歌曲</span>
            <span class="created-date">创建于 {{ formatDate(playlist.created_at) }}</span>
          </div>

          <div class="playlist-actions">
            <el-button
                type="primary"
                @click="playAll"
                :disabled="songs.length === 0"
            >
              <el-icon>
                <VideoPlay/>
              </el-icon>
              播放全部
            </el-button>

            <el-button @click="showEditDialog = true">
              <el-icon>
                <Edit/>
              </el-icon>
              编辑信息
            </el-button>

            <el-button @click="showAddSongsDialog = true">
              <el-icon>
                <Plus/>
              </el-icon>
              添加歌曲
            </el-button>
          </div>
        </div>
      </div>

      <!-- 歌曲列表 -->
      <div class="songs-section">
        <div class="section-header">
          <h3>歌曲列表</h3>
          <div class="section-actions" v-if="songs.length > 0">
            <el-button
                text
                @click="toggleSortMode"
                :disabled="songs.length < 2"
            >
              <el-icon>
                <Sort/>
              </el-icon>
              {{ sortMode ? '完成排序' : '调整顺序' }}
            </el-button>
          </div>
        </div>

        <div v-if="songs.length === 0" class="empty-songs">
          <el-empty description="歌单中还没有歌曲">
            <el-button type="primary" @click="showAddSongsDialog = true">
              添加歌曲
            </el-button>
          </el-empty>
        </div>

        <div v-else class="songs-container">
          <draggable
              v-model="sortableSongs"
              :disabled="!sortMode"
              @end="handleSortEnd"
              item-key="id"
              class="songs-list"
          >
            <template #item="{ element, index }">
              <div
                  class="song-item"
                  :class="{
                  sortable: sortMode,
                  active: isCurrentSong(element.song)
                }"
              >
                <div class="song-index">
                  <el-icon v-if="sortMode" class="drag-handle">
                    <Rank/>
                  </el-icon>
                  <span v-else-if="!isCurrentSong(element.song)">{{ index + 1 }}</span>
                  <el-icon v-else class="playing-icon">
                    <VideoPlay v-if="!playerStore.isPlaying"/>
                    <VideoPause v-else/>
                  </el-icon>
                </div>

                <div class="song-content" @dblclick="playSong(element.song, index)">
                  <div class="song-info">
                    <img
                        :src="element.song.cover_url || '/default-cover.png'"
                        :alt="element.song.title"
                        class="song-cover"
                        @error="handleImageError"
                    />
                    <div class="song-details">
                      <div class="song-title">{{ element.song.title }}</div>
                      <div class="song-artist">{{ element.song.artist }}</div>
                    </div>
                  </div>

                  <div class="song-album" v-if="element.song.album">
                    {{ element.song.album }}
                  </div>

                  <div class="song-duration">
                    {{ formatDuration(element.song.duration) }}
                  </div>
                </div>

                <div class="song-actions" v-if="!sortMode">
                  <el-button
                      text
                      @click="playSong(element.song, index)"
                  >
                    <el-icon>
                      <VideoPlay v-if="!isCurrentSong(element.song) || !playerStore.isPlaying"/>
                      <VideoPause v-else/>
                    </el-icon>
                  </el-button>

                  <el-button
                      text
                      @click="removeSong(element.song.id)"
                      type="danger"
                  >
                    <el-icon>
                      <Delete/>
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </div>

    <!-- 编辑歌单对话框 -->
    <el-dialog
        v-model="showEditDialog"
        title="编辑歌单信息"
        width="400px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="歌单名称" required>
          <el-input
              v-model="editForm.name"
              placeholder="请输入歌单名称"
              maxlength="50"
              show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
              v-model="editForm.description"
              type="textarea"
              placeholder="请输入歌单描述（可选）"
              :rows="3"
              maxlength="200"
              show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
            type="primary"
            @click="updatePlaylist"
            :loading="updating"
            :disabled="!editForm.name.trim()"
        >
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加歌曲对话框 -->
    <el-dialog
        v-model="showAddSongsDialog"
        title="添加歌曲到歌单"
        width="800px"
        top="5vh"
    >
      <div class="add-songs-content">
        <div class="search-section">
          <el-input
              v-model="searchQuery"
              placeholder="搜索歌曲..."
              clearable
              @input="searchSongs"
          >
            <template #prefix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </div>

        <div class="available-songs" v-loading="loadingSongs">
          <div
              v-for="song in availableSongs"
              :key="song.id"
              class="available-song-item"
              :class="{ selected: selectedSongs.includes(song.id) }"
              @click="toggleSongSelection(song.id)"
          >
            <el-checkbox
                :model-value="selectedSongs.includes(song.id)"
                @change="toggleSongSelection(song.id)"
            />
            <img
                :src="song.cover_url || '/default-cover.png'"
                :alt="song.title"
                class="song-cover-small"
                @error="handleImageError"
            />
            <div class="song-info-text">
              <div class="song-title">{{ song.title }}</div>
              <div class="song-artist">{{ song.artist }}</div>
            </div>
          </div>

          <div v-if="availableSongs.length === 0 && !loadingSongs" class="no-songs">
            <span>没有找到可添加的歌曲</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <span class="selected-count">已选择 {{ selectedSongs.length }} 首歌曲</span>
          <div>
            <el-button @click="showAddSongsDialog = false">取消</el-button>
            <el-button
                type="primary"
                @click="addSelectedSongs"
                :loading="addingSongs"
                :disabled="selectedSongs.length === 0"
            >
              添加到歌单
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import draggable from 'vuedraggable'
import {
  Menu,
  VideoPlay,
  VideoPause,
  Edit,
  Plus,
  Sort,
  Rank,
  Delete,
  Search
} from '@element-plus/icons-vue'
import {usePlaylistsStore} from '@/stores/playlists'
import {useSongsStore} from '@/stores/songs'
import {usePlayerStore} from '@/stores/player'
import type {Playlist, Song, SongInPlaylist} from '@/types'

const route = useRoute()
const router = useRouter()
const playlistsStore = usePlaylistsStore()
const songsStore = useSongsStore()
const playerStore = usePlayerStore()

const loading = ref(false)
const sortMode = ref(false)
const showEditDialog = ref(false)
const showAddSongsDialog = ref(false)
const updating = ref(false)
const loadingSongs = ref(false)
const addingSongs = ref(false)
const searchQuery = ref('')
const selectedSongs = ref<number[]>([])
const availableSongs = ref<Song[]>([])

const playlist = ref<Playlist | null>(null)
const songs = ref<SongInPlaylist[]>([])
const sortableSongs = ref<SongInPlaylist[]>([])

const editForm = ref({
  name: '',
  description: ''
})

const playlistId = computed(() => Number(route.params.id))

const isCurrentSong = (song: Song) => {
  return playerStore.currentSong?.id === song.id
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const formatDuration = (seconds: number): string => {
  if (!seconds) return '--:--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/default-cover.png'
}

const loadPlaylistDetail = async () => {
  if (!playlistId.value) return

  loading.value = true
  try {
    playlist.value = await playlistsStore.getPlaylist(playlistId.value)
    songs.value = await playlistsStore.getPlaylistSongs(playlistId.value)
    sortableSongs.value = [...songs.value]

    editForm.value = {
      name: playlist.value.name,
      description: playlist.value.description || ''
    }
  } catch (error) {
    ElMessage.error('加载歌单失败')
    router.push('/playlists')
  } finally {
    loading.value = false
  }
}

const playAll = () => {
  if (songs.value.length === 0) return

  const songList = songs.value.map(item => item.song)
  playerStore.playWithPlaylist(songList[0], songList)
  ElMessage.success(`开始播放歌单《${playlist.value?.name}》`)
}

const playSong = (song: Song, _index: number) => {
  const songList = songs.value.map(item => item.song)
  if (isCurrentSong(song)) {
    playerStore.togglePlay()
  } else {
    playerStore.playWithPlaylist(song, songList)
  }
}

const toggleSortMode = () => {
  if (sortMode.value) {
    // 保存排序
    saveSortOrder()
  } else {
    // 进入排序模式
    sortableSongs.value = [...songs.value]
  }
  sortMode.value = !sortMode.value
}

const handleSortEnd = () => {
  // 拖拽结束后自动保存
  saveSortOrder()
}

const saveSortOrder = async () => {
  try {
    const songOrders = sortableSongs.value.map((item, index) => ({
      song_id: item.song.id,
      order_index: index
    }))

    await playlistsStore.updatePlaylistSongOrder(playlistId.value, songOrders)
    songs.value = [...sortableSongs.value]
    ElMessage.success('歌曲顺序已保存')
  } catch (error) {
    ElMessage.error('保存顺序失败')
    sortableSongs.value = [...songs.value] // 恢复原顺序
  }
}

const updatePlaylist = async () => {
  if (!playlist.value || !editForm.value.name.trim()) return

  updating.value = true
  try {
    await playlistsStore.updatePlaylist(playlist.value.id, {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim() || undefined
    })

    playlist.value.name = editForm.value.name.trim()
    playlist.value.description = editForm.value.description.trim() || ''

    showEditDialog.value = false
    ElMessage.success('歌单信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const removeSong = async (songId: number) => {
  try {
    await ElMessageBox.confirm('确定要从歌单中移除这首歌曲吗？', '移除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await playlistsStore.removeSongFromPlaylist(playlistId.value, songId)
    songs.value = songs.value.filter(item => item.song.id !== songId)
    sortableSongs.value = [...songs.value]
    ElMessage.success('歌曲已移除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

const searchSongs = async () => {
  loadingSongs.value = true
  try {
    const allSongs = await songsStore.getSongs({search: searchQuery.value})
    const currentSongIds = songs.value.map(item => item.song.id)
    availableSongs.value = allSongs.filter(song => !currentSongIds.includes(song.id))
  } catch (error) {
    ElMessage.error('搜索歌曲失败')
  } finally {
    loadingSongs.value = false
  }
}

const toggleSongSelection = (songId: number) => {
  const index = selectedSongs.value.indexOf(songId)
  if (index > -1) {
    selectedSongs.value.splice(index, 1)
  } else {
    selectedSongs.value.push(songId)
  }
}

const addSelectedSongs = async () => {
  if (selectedSongs.value.length === 0) return

  addingSongs.value = true
  try {
    let successCount = 0
    for (const songId of selectedSongs.value) {
      try {
        await playlistsStore.addSongToPlaylist(playlistId.value, songId)
        successCount++
      } catch (error) {
        console.warn(`Failed to add song ${songId}:`, error)
      }
    }

    if (successCount > 0) {
      ElMessage.success(`成功添加 ${successCount} 首歌曲`)
      showAddSongsDialog.value = false
      selectedSongs.value = []
      loadPlaylistDetail() // 重新加载歌单
    } else {
      ElMessage.error('添加歌曲失败')
    }
  } catch (error) {
    ElMessage.error('添加歌曲失败')
  } finally {
    addingSongs.value = false
  }
}

// 监听对话框显示，加载可用歌曲
watch(showAddSongsDialog, (show) => {
  if (show) {
    searchQuery.value = ''
    selectedSongs.value = []
    searchSongs()
  }
})

onMounted(() => {
  loadPlaylistDetail()
})

// 监听路由变化
watch(() => route.params.id, () => {
  if (route.name === 'PlaylistDetail') {
    loadPlaylistDetail()
  }
})
</script>

<style scoped>
.playlist-detail {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.playlist-header {
  display: flex;
  gap: 32px;
  margin-bottom: 48px;
  align-items: flex-start;
}

.playlist-cover {
  flex: 0 0 200px;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: rgba(255, 255, 255, 0.8);
}

.playlist-info {
  flex: 1;
}

.playlist-title {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 16px 0;
}

.playlist-description {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.playlist-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  font-size: 14px;
  color: #909399;
}

.playlist-actions {
  display: flex;
  gap: 12px;
}

.songs-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.empty-songs {
  padding: 60px 0;
}

.songs-list {
  space-y: 1px;
}

.song-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.song-item:hover {
  background-color: #f5f7fa;
}

.song-item.active {
  background-color: #e6f3ff;
}

.song-item.sortable {
  cursor: move;
  border: 1px dashed #d9d9d9;
}

.song-index {
  flex: 0 0 40px;
  text-align: center;
  font-size: 14px;
  color: #909399;
}

.drag-handle {
  cursor: move;
  color: #409eff;
}

.playing-icon {
  color: #409eff;
}

.song-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.song-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.song-cover {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.song-details {
  flex: 1;
  min-width: 0;
}

.song-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.song-artist {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-album {
  flex: 0 0 200px;
  font-size: 14px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-duration {
  flex: 0 0 60px;
  text-align: right;
  font-size: 14px;
  color: #909399;
}

.song-actions {
  flex: 0 0 auto;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-item:hover .song-actions {
  opacity: 1;
}

.add-songs-content {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.search-section {
  margin-bottom: 16px;
}

.available-songs {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.available-song-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.available-song-item:hover {
  background-color: #f5f7fa;
}

.available-song-item.selected {
  background-color: #e6f3ff;
}

.song-cover-small {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.song-info-text {
  flex: 1;
  min-width: 0;
}

.no-songs {
  text-align: center;
  padding: 40px 0;
  color: #c0c4cc;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-count {
  font-size: 14px;
  color: #606266;
}
</style>