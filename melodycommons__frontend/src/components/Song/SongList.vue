<template>
  <div class="song-list">
    <el-table
        :data="songs"
        stripe
        @row-dblclick="handlePlaySong"
        v-loading="loading"
        empty-text="暂无歌曲"
        class="songs-table"
    >
      <el-table-column width="60" align="center">
        <template #default="{ row, $index }">
          <div class="song-index">
            <span v-if="!isCurrentSong(row)" class="index-number">{{ $index + 1 }}</span>
            <el-icon v-else class="playing-icon">
              <VideoPlay v-if="!playerStore.isPlaying"/>
              <VideoPause v-else/>
            </el-icon>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="标题" min-width="200">
        <template #default="{ row }">
          <div class="song-title-cell">
            <img
                :src="row.cover_url || '/default-cover.png'"
                :alt="row.title"
                class="song-cover-small"
                @error="handleImageError"
            />
            <div class="song-info-text">
              <div class="song-title" :class="{ active: isCurrentSong(row) }">
                {{ row.title }}
              </div>
              <div class="song-artist">{{ row.artist }}</div>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="album" label="专辑" min-width="150" show-overflow-tooltip/>

      <el-table-column label="时长" width="80" align="center">
        <template #default="{ row }">
          <span class="duration">{{ formatDuration(row.duration) }}</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <div class="song-actions">
            <el-button
                text
                @click="handlePlaySong(row)"
                :title="isCurrentSong(row) && playerStore.isPlaying ? '暂停' : '播放'"
            >
              <el-icon>
                <VideoPlay v-if="!isCurrentSong(row) || !playerStore.isPlaying"/>
                <VideoPause v-else/>
              </el-icon>
            </el-button>

            <el-dropdown @command="(command: string) => handleSongAction(command, row)">
              <el-button text>
                <el-icon>
                  <MoreFilled/>
                </el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="addToPlaylist">添加到歌单</el-dropdown-item>
                  <el-dropdown-item command="edit">编辑信息</el-dropdown-item>
                  <el-dropdown-item command="refreshCover">刷新封面</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加到歌单对话框 -->
    <el-dialog
        v-model="addToPlaylistVisible"
        title="添加到歌单"
        width="400px"
    >
      <div class="playlist-selection">
        <el-radio-group v-model="selectedPlaylistId">
          <div
              v-for="playlist in playlistsStore.playlists"
              :key="playlist.id"
              class="playlist-option"
          >
            <el-radio :label="playlist.id">{{ playlist.name }}</el-radio>
          </div>
        </el-radio-group>
        <div v-if="playlistsStore.playlists.length === 0" class="no-playlists">
          <span>暂无歌单，请先创建歌单</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="addToPlaylistVisible = false">取消</el-button>
        <el-button
            type="primary"
            @click="confirmAddToPlaylist"
            :disabled="!selectedPlaylistId"
            :loading="addingToPlaylist"
        >
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {VideoPlay, VideoPause, MoreFilled} from '@element-plus/icons-vue'
import {usePlayerStore} from '@/stores/player'
import {useSongsStore} from '@/stores/songs'
import {usePlaylistsStore} from '@/stores/playlists'
import type {Song} from '@/types'

interface Props {
  songs: Song[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  editSong: [song: Song]
}>()

const playerStore = usePlayerStore()
const songsStore = useSongsStore()
const playlistsStore = usePlaylistsStore()

const addToPlaylistVisible = ref(false)
const selectedPlaylistId = ref<number | null>(null)
const addingToPlaylist = ref(false)
const currentActionSong = ref<Song | null>(null)

const isCurrentSong = (song: Song) => {
  return playerStore.currentSong?.id === song.id
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

const handlePlaySong = (song: Song) => {
  if (isCurrentSong(song)) {
    playerStore.togglePlay()
  } else {
    playerStore.playWithPlaylist(song, props.songs)
  }
}

const handleSongAction = async (command: string, song: Song) => {
  currentActionSong.value = song

  switch (command) {
    case 'addToPlaylist':
      if (playlistsStore.playlists.length === 0) {
        ElMessage.warning('请先创建歌单')
        return
      }
      selectedPlaylistId.value = null
      addToPlaylistVisible.value = true
      break

    case 'edit':
      emit('editSong', song)
      break

    case 'refreshCover':
      await refreshSongCover(song)
      break

    case 'delete':
      await deleteSong(song)
      break
  }
}

const confirmAddToPlaylist = async () => {
  if (!selectedPlaylistId.value || !currentActionSong.value) return

  addingToPlaylist.value = true
  try {
    await playlistsStore.addSongToPlaylist(selectedPlaylistId.value, currentActionSong.value.id)
    addToPlaylistVisible.value = false
    ElMessage.success('已添加到歌单')
  } catch (error: any) {
    if (error.response?.status === 409) {
      ElMessage.warning('歌曲已在该歌单中')
    } else {
      ElMessage.error('添加失败')
    }
  } finally {
    addingToPlaylist.value = false
  }
}

const refreshSongCover = async (song: Song) => {
  try {
    await songsStore.refreshCover(song.id)
    ElMessage.success('封面刷新成功')
  } catch (error) {
    ElMessage.error('封面刷新失败')
  }
}

const deleteSong = async (song: Song) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除歌曲《${song.title}》吗？此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await songsStore.deleteSong(song.id)
    ElMessage.success('歌曲删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.song-list {
  height: 100%;
}

.songs-table {
  height: 100%;
}

.song-index {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.index-number {
  color: #909399;
  font-size: 14px;
}

.playing-icon {
  color: #409eff;
  font-size: 16px;
}

.song-title-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.song-cover-small {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
  background: #f5f7fa;
}

.song-info-text {
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

.song-title.active {
  color: #409eff;
}

.song-artist {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.duration {
  color: #909399;
  font-size: 14px;
}

.song-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.playlist-selection {
  max-height: 300px;
  overflow-y: auto;
}

.playlist-option {
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.playlist-option:last-child {
  border-bottom: none;
}

.no-playlists {
  text-align: center;
  padding: 40px 0;
  color: #c0c4cc;
  font-style: italic;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}
</style>