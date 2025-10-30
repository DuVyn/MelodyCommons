<template>
  <div class="song-item" :class="{ active: isActive, playing: isPlaying }">
    <div class="song-cover">
      <img
          :src="song.cover_url || '/default-cover.png'"
          :alt="song.title"
          @error="handleImageError"
      />
      <div class="play-overlay" @click="handlePlay">
        <el-icon class="play-icon">
          <VideoPlay v-if="!isPlaying"/>
          <VideoPause v-else/>
        </el-icon>
      </div>
    </div>

    <div class="song-info">
      <div class="song-title" :title="song.title">{{ song.title }}</div>
      <div class="song-artist" :title="song.artist">{{ song.artist }}</div>
      <div class="song-album" v-if="song.album" :title="song.album">{{ song.album }}</div>
    </div>

    <div class="song-duration">{{ formatDuration(song.duration) }}</div>

    <div class="song-actions" v-if="showActions">
      <el-dropdown @command="handleAction" trigger="click">
        <el-button text size="small">
          <el-icon>
            <MoreFilled/>
          </el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="play">播放</el-dropdown-item>
            <el-dropdown-item command="addToPlaylist">添加到歌单</el-dropdown-item>
            <el-dropdown-item command="edit" divided>编辑</el-dropdown-item>
            <el-dropdown-item command="refreshCover">刷新封面</el-dropdown-item>
            <el-dropdown-item command="delete">删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed} from 'vue'
import {VideoPlay, VideoPause, MoreFilled} from '@element-plus/icons-vue'
import {usePlayerStore} from '@/stores/player'
import type {Song} from '@/types'

interface Props {
  song: Song
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

const emit = defineEmits<{
  play: [song: Song]
  action: [action: string, song: Song]
}>()

const playerStore = usePlayerStore()

const isActive = computed(() => playerStore.currentSong?.id === props.song.id)
const isPlaying = computed(() => isActive.value && playerStore.isPlaying)

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

const handlePlay = () => {
  emit('play', props.song)
}

const handleAction = (command: string) => {
  if (command === 'play') {
    handlePlay()
  } else {
    emit('action', command, props.song)
  }
}
</script>

<style scoped>
.song-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
}

.song-item:hover {
  background-color: #f5f7fa;
}

.song-item.active {
  background-color: #e6f3ff;
}

.song-item.playing {
  background-color: #d4edda;
}

.song-cover {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.song-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #f5f7fa;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-cover:hover .play-overlay,
.song-item.active .play-overlay {
  opacity: 1;
}

.play-icon {
  color: white;
  font-size: 20px;
}

.song-info {
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

.song-item.active .song-title {
  color: #409eff;
}

.song-artist {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
}

.song-album {
  font-size: 11px;
  color: #c0c4cc;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-duration {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  margin-right: 8px;
}

.song-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.3s;
}

.song-item:hover .song-actions {
  opacity: 1;
}
</style>