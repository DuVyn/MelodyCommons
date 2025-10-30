<template>
  <div class="playlist-list">
    <div class="list-header">
      <h2>我的歌单</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon>
          <Plus/>
        </el-icon>
        创建歌单
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated/>
    </div>

    <div v-else-if="playlists.length === 0" class="empty-container">
      <el-empty description="暂无歌单">
        <el-button type="primary" @click="showCreateDialog = true">
          创建第一个歌单
        </el-button>
      </el-empty>
    </div>

    <div v-else class="playlists-grid">
      <div
          v-for="playlist in playlists"
          :key="playlist.id"
          class="playlist-card"
          @click="$router.push(`/playlists/${playlist.id}`)"
      >
        <div class="playlist-cover">
          <div class="cover-placeholder">
            <el-icon>
              <Menu/>
            </el-icon>
          </div>
          <div class="playlist-overlay">
            <el-button circle @click.stop="playPlaylist(playlist)">
              <el-icon>
                <VideoPlay/>
              </el-icon>
            </el-button>
          </div>
        </div>

        <div class="playlist-info">
          <h3 class="playlist-name" :title="playlist.name">{{ playlist.name }}</h3>
          <p class="playlist-description" v-if="playlist.description" :title="playlist.description">
            {{ playlist.description }}
          </p>
          <div class="playlist-meta">
            <span class="created-date">{{ formatDate(playlist.created_at) }}</span>
          </div>
        </div>

        <div class="playlist-actions" @click.stop>
          <el-dropdown @command="(command: string) => handlePlaylistAction(command, playlist)">
            <el-button text>
              <el-icon>
                <MoreFilled/>
              </el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="play">播放全部</el-dropdown-item>
                <el-dropdown-item command="edit" divided>编辑信息</el-dropdown-item>
                <el-dropdown-item command="delete">删除歌单</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 创建歌单对话框 -->
    <el-dialog
        v-model="showCreateDialog"
        title="创建歌单"
        width="400px"
    >
      <el-form :model="newPlaylist" label-width="80px">
        <el-form-item label="歌单名称" required>
          <el-input
              v-model="newPlaylist.name"
              placeholder="请输入歌单名称"
              maxlength="50"
              show-word-limit
              @keyup.enter="createPlaylist"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
              v-model="newPlaylist.description"
              type="textarea"
              placeholder="请输入歌单描述（可选）"
              :rows="3"
              maxlength="200"
              show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button
            type="primary"
            @click="createPlaylist"
            :loading="creating"
            :disabled="!newPlaylist.name.trim()"
        >
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑歌单对话框 -->
    <el-dialog
        v-model="showEditDialog"
        title="编辑歌单"
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
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Plus, Menu, VideoPlay, MoreFilled} from '@element-plus/icons-vue'
import {usePlaylistsStore} from '@/stores/playlists'
import {usePlayerStore} from '@/stores/player'
import type {Playlist} from '@/types'

const router = useRouter()
const playlistsStore = usePlaylistsStore()
const playerStore = usePlayerStore()

const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const creating = ref(false)
const updating = ref(false)
const currentEditPlaylist = ref<Playlist | null>(null)

const newPlaylist = ref({
  name: '',
  description: ''
})

const editForm = ref({
  name: '',
  description: ''
})

const playlists = computed(() => playlistsStore.playlists)

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadPlaylists = async () => {
  loading.value = true
  try {
    await playlistsStore.loadPlaylists()
  } catch (error) {
    ElMessage.error('加载歌单失败')
  } finally {
    loading.value = false
  }
}

const createPlaylist = async () => {
  if (!newPlaylist.value.name.trim()) {
    ElMessage.warning('请输入歌单名称')
    return
  }

  creating.value = true
  try {
    const playlist = await playlistsStore.createPlaylist({
      name: newPlaylist.value.name.trim(),
      description: newPlaylist.value.description.trim() || undefined
    })

    showCreateDialog.value = false
    newPlaylist.value = {name: '', description: ''}
    ElMessage.success('歌单创建成功')

    // 跳转到新创建的歌单
    router.push(`/playlists/${playlist.id}`)
  } catch (error) {
    ElMessage.error('创建歌单失败')
  } finally {
    creating.value = false
  }
}

const playPlaylist = async (playlist: Playlist) => {
  try {
    const songs = await playlistsStore.getPlaylistSongs(playlist.id)
    if (songs.length === 0) {
      ElMessage.warning('歌单为空')
      return
    }

    const songList = songs.map(item => item.song)
    playerStore.playWithPlaylist(songList[0], songList)
    ElMessage.success(`开始播放歌单《${playlist.name}》`)
  } catch (error) {
    ElMessage.error('播放失败')
  }
}

const handlePlaylistAction = async (command: string, playlist: Playlist) => {
  switch (command) {
    case 'play':
      await playPlaylist(playlist)
      break

    case 'edit':
      currentEditPlaylist.value = playlist
      editForm.value = {
        name: playlist.name,
        description: playlist.description || ''
      }
      showEditDialog.value = true
      break

    case 'delete':
      await deletePlaylist(playlist)
      break
  }
}

const updatePlaylist = async () => {
  if (!currentEditPlaylist.value || !editForm.value.name.trim()) {
    return
  }

  updating.value = true
  try {
    await playlistsStore.updatePlaylist(currentEditPlaylist.value.id, {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim() || undefined
    })

    showEditDialog.value = false
    ElMessage.success('歌单信息更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const deletePlaylist = async (playlist: Playlist) => {
  try {
    await ElMessageBox.confirm(
        `确定要删除歌单《${playlist.name}》吗？此操作不可恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    await playlistsStore.deletePlaylist(playlist.id)
    ElMessage.success('歌单删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadPlaylists()
})
</script>

<style scoped>
.playlist-list {
  padding: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.list-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.loading-container {
  padding: 20px 0;
}

.empty-container {
  padding: 60px 0;
}

.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.playlist-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.playlist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.playlist-cover {
  position: relative;
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-placeholder {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.8);
}

.playlist-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.playlist-card:hover .playlist-overlay {
  opacity: 1;
}

.playlist-info {
  padding: 20px;
}

.playlist-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.playlist-meta {
  font-size: 12px;
  color: #909399;
}

.playlist-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  opacity: 0;
  transition: opacity 0.3s;
}

.playlist-card:hover .playlist-actions {
  opacity: 1;
}

.playlist-actions :deep(.el-button) {
  background: rgba(255, 255, 255, 0.9);
  border: none;
}

.playlist-actions :deep(.el-button:hover) {
  background: white;
}
</style>