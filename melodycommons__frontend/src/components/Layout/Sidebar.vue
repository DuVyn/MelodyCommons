<template>
  <aside class="app-sidebar">
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="section-header">
          <h3 class="section-title">音乐库</h3>
        </div>
        <ul class="nav-list">
          <li class="nav-item">
            <router-link to="/popular" class="nav-link">
              <el-icon>
                <TrendCharts/>
              </el-icon>
              <span>🔥 热门歌曲</span>
            </router-link>
          </li>
        </ul>
      </div>

      <div class="nav-section">
        <div class="section-header">
          <h3 class="section-title">歌单</h3>
          <el-button text circle @click="showCreatePlaylistDialog" class="create-btn">
            <el-icon>
              <Plus/>
            </el-icon>
          </el-button>
        </div>
        <ul class="nav-list">
          <li v-for="playlist in playlistsStore.playlists" :key="playlist.id" class="nav-item"
              @mouseenter="hoveredPlaylistId = playlist.id"
              @mouseleave="hoveredPlaylistId = null"
          >
            <router-link :to="`/playlists/${playlist.id}`" class="nav-link playlist-link">
              <el-icon>
                <Menu/>
              </el-icon>
              <span class="playlist-name">{{ playlist.name }}</span>
            </router-link>
            <el-button
                v-show="hoveredPlaylistId === playlist.id"
                text
                circle
                class="delete-playlist-btn"
                :icon="Delete"
                @click.stop.prevent="handleDeletePlaylist(playlist)"
            />
          </li>
          <li v-if="playlistsStore.playlists.length === 0" class="nav-item empty">
            <span class="empty-text">暂无歌单</span>
          </li>
        </ul>
      </div>
    </nav>

    <el-dialog
        v-model="createDialogVisible"
        title="创建新歌单"
        width="400px"
        append-to-body
    >
      <el-form :model="newPlaylist" label-position="top">
        <el-form-item label="歌单名称" required>
          <el-input v-model="newPlaylist.name" placeholder="请输入歌单名称" maxlength="50" show-word-limit/>
        </el-form-item>
        <el-form-item label="描述 (可选)">
          <el-input v-model="newPlaylist.description" type="textarea" placeholder="请输入歌单描述" :rows="3"
                    maxlength="200" show-word-limit/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreatePlaylist" :loading="creating"
                   :disabled="!newPlaylist.name.trim()">
          创建
        </el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup lang="ts">
import {ref, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Headset, Menu, Plus, Delete, Promotion} from '@element-plus/icons-vue'
import {usePlaylistsStore} from '@/stores/playlists'
import type {Playlist} from '@/types'

const router = useRouter()
const playlistsStore = usePlaylistsStore()

const createDialogVisible = ref(false)
const creating = ref(false)
const newPlaylist = ref({name: '', description: ''})
const hoveredPlaylistId = ref<number | null>(null)

const showCreatePlaylistDialog = () => {
  newPlaylist.value = {name: '', description: ''}
  createDialogVisible.value = true
}

const handleCreatePlaylist = async () => {
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
    createDialogVisible.value = false
    ElMessage.success('歌单创建成功')
    router.push(`/playlists/${playlist.id}`)
  } catch (error) {
    ElMessage.error('创建歌单失败')
  } finally {
    creating.value = false
  }
}

const handleDeletePlaylist = async (playlist: Playlist) => {
  try {
    // === 关键修复：移除 appendToBody 属性来解决 TypeScript 报错 ===
    await ElMessageBox.confirm(`确定要删除歌单《${playlist.name}》吗？此操作不可恢复。`, '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })

    await playlistsStore.deletePlaylist(playlist.id)
    ElMessage.success('歌单删除成功')

    if (router.currentRoute.value.path === `/playlists/${playlist.id}`) {
      router.push('/songs')
    }

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除歌单失败')
      console.error('Failed to delete playlist:', error)
    }
  }
}

onMounted(() => {
  playlistsStore.loadPlaylists()
})
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px) saturate(180%);
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
  overflow-y: auto;
  z-index: var(--z-index-sidebar);
  padding-bottom: calc(var(--player-height) + var(--player-v-padding) * 2);
}

.sidebar-nav {
  padding: var(--spacing-4) 0;
}

.nav-section {
  margin-bottom: var(--spacing-6);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-5);
  margin-bottom: var(--spacing-2);
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
}

.create-btn {
  color: var(--color-text-secondary);
}

.nav-list {
  list-style: none;
}

.nav-item {
  position: relative;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-5);
  color: var(--color-text-regular);
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.3);
  color: var(--color-primary-dark);
}

/* === 关键修复：修改 router-link-active 的选择器 === */
.nav-item > .router-link-active {
  background-color: var(--color-primary);
  color: var(--color-background-light);
  font-weight: 600;
}

.nav-item > .router-link-active:hover {
  background-color: var(--color-primary);
}


.playlist-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-text {
  padding: var(--spacing-3) var(--spacing-5);
  color: var(--color-text-placeholder);
  font-size: 14px;
  font-style: italic;
}

.delete-playlist-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  padding: 4px;
  height: auto;
  width: auto;
}

.delete-playlist-btn:hover {
  color: var(--color-danger);
}
</style>