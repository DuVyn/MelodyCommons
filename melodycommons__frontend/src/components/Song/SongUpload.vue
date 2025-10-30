<template>
  <div class="song-upload">
    <!-- 添加元数据输入表单 -->
    <div class="metadata-form" v-if="showMetadataForm">
      <h3>歌曲信息</h3>
      <el-form :model="metadata" label-width="80px" style="margin-bottom: 20px;">
        <el-form-item label="标题">
          <el-input v-model="metadata.title" placeholder="歌曲标题（可选，留空将自动识别）"/>
        </el-form-item>
        <el-form-item label="艺术家">
          <el-input v-model="metadata.artist" placeholder="艺术家（可选，留空将自动识别）"/>
        </el-form-item>
        <el-form-item label="专辑">
          <el-input v-model="metadata.album" placeholder="专辑名称（可选）"/>
        </el-form-item>
      </el-form>
      <el-button @click="showMetadataForm = false" style="margin-bottom: 20px;">
        隐藏信息设置
      </el-button>
    </div>

    <div v-else style="margin-bottom: 20px;">
      <el-button @click="showMetadataForm = true" type="text">
        <el-icon>
          <Setting/>
        </el-icon>
        自定义歌曲信息
      </el-button>
    </div>

    <el-upload
        ref="uploadRef"
        :action="`${API_BASE}/songs/`"
        :headers="uploadHeaders"
        :data="uploadData"
        :before-upload="beforeUpload"
        :on-success="onSuccess"
        :on-error="onError"
        :on-progress="onProgress"
        :show-file-list="false"
        drag
        multiple
        accept=".mp3,.flac,.wav"
        class="upload-area"
    >
      <div class="upload-content">
        <el-icon class="upload-icon">
          <UploadFilled/>
        </el-icon>
        <div class="upload-text">
          <div class="main-text">点击或拖拽音频文件到此处上传</div>
          <div class="sub-text">支持 MP3、FLAC、WAV 格式，单个文件最大 50MB</div>
        </div>
      </div>
    </el-upload>

    <!-- 上传进度部分保持不变 -->
    <div v-if="uploadQueue.length > 0" class="upload-progress">
      <div class="progress-header">
        <span>上传进度 ({{ completedCount }}/{{ uploadQueue.length }})</span>
        <el-button text @click="clearCompleted" :disabled="!hasCompleted">
          清除已完成
        </el-button>
      </div>

      <div class="progress-list">
        <div
            v-for="item in uploadQueue"
            :key="item.id"
            class="progress-item"
            :class="{ completed: item.status === 'success', error: item.status === 'error' }"
        >
          <div class="file-info">
            <div class="file-name">{{ item.file.name }}</div>
            <div class="file-size">{{ formatFileSize(item.file.size) }}</div>
          </div>

          <div class="progress-bar">
            <el-progress
                :percentage="item.progress"
                :status="getProgressStatus(item.status)"
                :show-text="false"
                :stroke-width="6"
            />
          </div>

          <div class="progress-status">
            <span v-if="item.status === 'uploading'">{{ item.progress }}%</span>
            <el-icon v-else-if="item.status === 'success'" class="success-icon">
              <Check/>
            </el-icon>
            <el-icon v-else-if="item.status === 'error'" class="error-icon">
              <Close/>
            </el-icon>
          </div>

          <div class="progress-actions">
            <el-button
                v-if="item.status === 'error'"
                text
                size="small"
                @click="retryUpload(item)"
            >
              重试
            </el-button>
            <el-button
                text
                size="small"
                @click="removeFromQueue(item.id)"
            >
              移除
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, computed} from 'vue'
import {ElMessage, type UploadInstance} from 'element-plus'
import {UploadFilled, Check, Close, Setting} from '@element-plus/icons-vue'
import {useAuthStore} from '@/stores/auth'
import {useSongsStore} from '@/stores/songs'

interface UploadItem {
  id: string
  file: File
  progress: number
  status: 'uploading' | 'success' | 'error'
  response?: any
  error?: string
}

const emit = defineEmits<{
  success: [count: number]
}>()

const uploadRef = ref<UploadInstance>()
const authStore = useAuthStore()
const songsStore = useSongsStore()

const API_BASE = 'http://localhost:8000'
const uploadQueue = ref<UploadItem[]>([])
const showMetadataForm = ref(false)

// 添加元数据表单
const metadata = ref({
  title: '',
  artist: '',
  album: ''
})

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}))

// 添加上传数据，包含元数据
const uploadData = computed(() => {
  const data: Record<string, string> = {}
  if (metadata.value.title.trim()) {
    data.title = metadata.value.title.trim()
  }
  if (metadata.value.artist.trim()) {
    data.artist = metadata.value.artist.trim()
  }
  if (metadata.value.album.trim()) {
    data.album = metadata.value.album.trim()
  }
  return data
})

const completedCount = computed(() => {
  return uploadQueue.value.filter(item => item.status === 'success').length
})

const hasCompleted = computed(() => {
  return uploadQueue.value.some(item => item.status === 'success')
})

const beforeUpload = (file: File) => {
  // 检查文件格式
  const allowedTypes = ['.mp3', '.flac', '.wav']
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()

  if (!allowedTypes.includes(fileExt)) {
    ElMessage.error(`不支持的文件格式: ${fileExt}`)
    return false
  }

  // 检查文件大小 (50MB)
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }

  // 添加到上传队列
  const uploadItem: UploadItem = {
    id: Date.now() + '-' + Math.random().toString(36).substr(2, 9),
    file,
    progress: 0,
    status: 'uploading'
  }

  uploadQueue.value.push(uploadItem)

  return true
}

const onProgress = (event: ProgressEvent, file: File) => {
  const item = uploadQueue.value.find(item => item.file === file)
  if (item) {
    item.progress = Math.round((event.loaded / event.total) * 100)
  }
}

const onSuccess = (response: any, file: File) => {
  const item = uploadQueue.value.find(item => item.file === file)
  if (item) {
    item.status = 'success'
    item.response = response
    item.progress = 100
  }

  // 刷新歌曲列表
  songsStore.loadSongs()

  ElMessage.success(`《${response.title}》 上传成功`)

  // 发出成功事件
  const successCount = uploadQueue.value.filter(item => item.status === 'success').length
  emit('success', successCount)

  // 清空元数据表单（如果需要的话）
  // metadata.value = { title: '', artist: '', album: '' }
}

const onError = (error: any, file: File) => {
  const item = uploadQueue.value.find(item => item.file === file)
  if (item) {
    item.status = 'error'
    item.error = error.message || '上传失败'
  }

  ElMessage.error(`${file.name} 上传失败`)
}

const getProgressStatus = (status: string) => {
  switch (status) {
    case 'success':
      return 'success'
    case 'error':
      return 'exception'
    default:
      return undefined
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const retryUpload = (item: UploadItem) => {
  // 重置状态
  item.status = 'uploading'
  item.progress = 0
  item.error = undefined

  // 重新上传逻辑需要手动实现
  ElMessage.info('重新上传功能开发中...')
}

const removeFromQueue = (id: string) => {
  const index = uploadQueue.value.findIndex(item => item.id === id)
  if (index > -1) {
    uploadQueue.value.splice(index, 1)
  }
}

const clearCompleted = () => {
  uploadQueue.value = uploadQueue.value.filter(item => item.status !== 'success')
}
</script>

<style scoped>
.song-upload {
  width: 100%;
}

.metadata-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.metadata-form h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.upload-area {
  width: 100%;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.main-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.sub-text {
  font-size: 14px;
  color: #909399;
}

.upload-progress {
  margin-top: 24px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 500;
}

.progress-list {
  max-height: 400px;
  overflow-y: auto;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.3s;
}

.progress-item:last-child {
  border-bottom: none;
}

.progress-item:hover {
  background-color: #f8f9fa;
}

.progress-item.completed {
  background-color: #f0f9ff;
}

.progress-item.error {
  background-color: #fef0f0;
}

.file-info {
  flex: 0 0 200px;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.progress-bar {
  flex: 1;
  margin: 0 16px;
}

.progress-status {
  flex: 0 0 60px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.success-icon {
  color: #67c23a;
  font-size: 16px;
}

.error-icon {
  color: #f56c6c;
  font-size: 16px;
}

.progress-actions {
  flex: 0 0 auto;
  display: flex;
  gap: 8px;
}
</style>