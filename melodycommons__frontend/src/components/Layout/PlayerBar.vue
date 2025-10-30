<template>
  <div v-if="currentSong" class="player-bar">
    <div class="player-content">
      <!-- Left Section: Song Info -->
      <div class="song-info">
        <div class="song-cover">
          <img v-if="currentSong.cover_url" :src="currentSong.cover_url" :alt="currentSong.title"
               @error="handleImageError"/>
          <div v-else class="cover-placeholder">
            <el-icon>
              <Mic/>
            </el-icon>
          </div>
        </div>
        <div class="song-details">
          <p class="song-title">{{ currentSong.title }}</p>
          <p class="song-artist">{{ currentSong.artist }}</p>
        </div>
      </div>

      <!-- Center Section: Player Controls -->
      <div class="player-controls">
        <!-- 关键改动：将两行合并为一行，用 Flexbox 直接控制 -->
        <div class="control-buttons">
          <el-button text circle :disabled="!hasPrevious" @click="previousSong" class="control-btn">
            <el-icon>
              <CaretLeft/>
            </el-icon>
          </el-button>
          <el-button :loading="loading" circle type="primary" @click="togglePlay" class="play-btn">
            <el-icon v-if="!loading">
              <VideoPause v-if="isPlaying"/>
              <VideoPlay v-else/>
            </el-icon>
          </el-button>
          <el-button text circle :disabled="!hasNext" @click="nextSong" class="control-btn">
            <el-icon>
              <CaretRight/>
            </el-icon>
          </el-button>
        </div>
        <div class="progress-section">
          <span class="time-display">{{ formatTime(currentTime) }}</span>
          <div class="progress-container">
            <el-slider v-model="progressValue" :show-tooltip="false" @change="handleSeekChange" @input="handleSeekInput"
                       class="progress-slider"/>
          </div>
          <span class="time-display">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- Right Section: Extra Controls -->
      <div class="player-extras">
        <el-button text circle @click="togglePlayMode" :title="getPlayModeTitle()" class="extra-btn">
          <el-icon>
            <RefreshRight v-if="playMode === 'repeat'"/>
            <Operation v-else-if="playMode === 'shuffle'"/>
            <Sort v-else/>
          </el-icon>
        </el-button>
        <div class="volume-section">
          <el-button text circle @click="toggleMute" class="extra-btn">
            <el-icon>
              <Mute v-if="isMuted || volume === 0"/>
              <Bell v-else/>
            </el-icon>
          </el-button>
          <div class="volume-container">
            <el-slider :model-value="volume" :show-tooltip="false" @input="setVolume" class="volume-slider"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import {
  VideoPlay,
  VideoPause,
  CaretLeft,
  CaretRight,
  Mute,
  Bell,
  Mic,
  Sort,
  RefreshRight,
  Operation
} from '@element-plus/icons-vue'
import {usePlayerStore} from '@/stores/player'

const playerStore = usePlayerStore()
const progressValue = ref(0)
const isDragging = ref(false)

const currentSong = computed(() => playerStore.currentSong)
const isPlaying = computed(() => playerStore.isPlaying)
const currentTime = computed(() => playerStore.currentTime)
const duration = computed(() => playerStore.duration)
const volume = computed(() => playerStore.volume)
const isMuted = computed(() => playerStore.isMuted)
const loading = computed(() => playerStore.loading)
const playMode = computed(() => playerStore.playMode)
const hasPrevious = computed(() => playerStore.hasPrevious)
const hasNext = computed(() => playerStore.hasNext)

watch(() => playerStore.progress, (newProgress) => {
  if (!isDragging.value) {
    progressValue.value = newProgress
  }
})

const togglePlay = () => playerStore.togglePlay()
const previousSong = () => playerStore.previousSong()
const nextSong = () => playerStore.nextSong()
const toggleMute = () => playerStore.toggleMute()
const setVolume = (value: number) => playerStore.setVolume(value)
const togglePlayMode = () => playerStore.togglePlayMode()

const handleSeekInput = (value: number) => {
  isDragging.value = true;
  progressValue.value = value
}
const handleSeekChange = (value: number) => {
  isDragging.value = false;
  playerStore.seek(value)
}

const formatTime = (seconds: number): string => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const getPlayModeTitle = () => {
  const titles = {repeat: '单曲循环', shuffle: '随机播放', sequential: '顺序播放'}
  return titles[playMode.value] || '顺序播放'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  (img.parentElement as HTMLElement).classList.add('no-cover');
  img.style.display = 'none';
}
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: var(--player-v-padding);
  left: var(--player-v-padding);
  right: var(--player-v-padding);
  height: var(--player-height);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2); /* === 修改这里 === */
  border-radius: var(--radius-lg);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.1);
  z-index: var(--z-index-player);
}

.player-content {
  height: 100%;
  padding: 0 var(--spacing-5);
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: var(--spacing-6);
}

/* --- COLUMNS --- */
.song-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  min-width: 0;
  justify-self: start;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  width: 1000px;
}

.control-buttons {
  display: flex;
  align-items: center;
}

.progress-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.player-extras {
  display: flex;
  align-items: center;
  justify-self: end;
  gap: var(--spacing-2);
}

/* --- COMPONENTS --- */
.song-cover {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background-color: var(--color-background-dark);
  flex-shrink: 0;
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
  color: var(--color-text-placeholder);
  font-size: 24px;
}

.song-cover.no-cover {
  border: 1px dashed var(--color-border);
}

.song-details {
  min-width: 0;
}

.song-details p {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.song-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-main);
}

.song-artist {
  font-size: 12px;
  color: var(--color-text-regular);
  margin-top: 2px;
}

.control-btn, .extra-btn {
  width: 34px;
  height: 34px;
  color: var(--color-text-regular);
}

.play-btn {
  width: 44px;
  height: 44px;
  font-size: 18px;
}

.time-display {
  font-size: 11px;
  color: var(--color-text-secondary);
  min-width: 35px;
  text-align: center;
}

.progress-container {
  flex-grow: 1;
}

.volume-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.volume-container {
  width: 100px;
}

/* Element Plus Slider Overrides */
.progress-slider, .volume-slider {
  --el-slider-height: 5px;
  --el-slider-button-size: 14px;
}

:deep(.el-slider__runway) {
  background-color: var(--color-border-light);
  border-radius: 3px;
}

:deep(.el-slider__bar) {
  background-color: var(--color-primary);
  border-radius: 3px;
}

:deep(.el-slider__button) {
  border: 2px solid var(--color-primary);
}
</style>