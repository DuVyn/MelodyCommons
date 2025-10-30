<template>
  <el-dialog
      v-model="visible"
      title="编辑歌曲信息"
      width="500px"
      @close="handleClose"
  >
    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        @submit.prevent="handleSubmit"
    >
      <el-form-item label="标题" prop="title">
        <el-input
            v-model="form.title"
            placeholder="请输入歌曲标题"
            maxlength="100"
            show-word-limit
        />
      </el-form-item>

      <el-form-item label="艺术家" prop="artist">
        <el-input
            v-model="form.artist"
            placeholder="请输入艺术家"
            maxlength="100"
            show-word-limit
        />
      </el-form-item>

      <el-form-item label="专辑" prop="album">
        <el-input
            v-model="form.album"
            placeholder="请输入专辑名称（可选）"
            maxlength="100"
            show-word-limit
        />
      </el-form-item>

      <el-form-item label="封面">
        <div class="cover-section">
          <div class="current-cover">
            <img
                :src="currentCover"
                :alt="form.title"
                class="cover-image"
                @error="handleImageError"
            />
          </div>
          <div class="cover-actions">
            <el-button
                @click="refreshCover"
                :loading="refreshing"
                size="small"
            >
              重新获取封面
            </el-button>
            <div class="cover-tip">
              修改歌曲信息后，可以重新获取匹配的封面
            </div>
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
            type="primary"
            @click="handleSubmit"
            :loading="submitting"
        >
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {ref, computed, watch} from 'vue'
import {ElMessage, type FormInstance, type FormRules} from 'element-plus'
import {useSongsStore} from '@/stores/songs'
import type {Song} from '@/types'

interface Props {
  modelValue: boolean
  song: Song | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const songsStore = useSongsStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const refreshing = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const form = ref({
  title: '',
  artist: '',
  album: ''
})

const currentCover = computed(() => {
  return props.song?.cover_url || '/default-cover.png'
})

const rules: FormRules = {
  title: [
    {required: true, message: '请输入歌曲标题', trigger: 'blur'},
    {min: 1, max: 100, message: '标题长度应在 1-100 个字符', trigger: 'blur'}
  ],
  artist: [
    {required: true, message: '请输入艺术家', trigger: 'blur'},
    {min: 1, max: 100, message: '艺术家长度应在 1-100 个字符', trigger: 'blur'}
  ],
  album: [
    {max: 100, message: '专辑名长度不能超过 100 个字符', trigger: 'blur'}
  ]
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/default-cover.png'
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

const resetForm = () => {
  form.value = {
    title: '',
    artist: '',
    album: ''
  }
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!props.song) return

  try {
    await formRef.value?.validate()

    submitting.value = true

    // 检查是否有变化
    const hasChanges =
        form.value.title !== props.song.title ||
        form.value.artist !== props.song.artist ||
        form.value.album !== (props.song.album || '')

    if (!hasChanges) {
      ElMessage.info('没有修改任何信息')
      handleClose()
      return
    }

    await songsStore.updateSong(props.song.id, {
      title: form.value.title.trim(),
      artist: form.value.artist.trim(),
      album: form.value.album.trim() || undefined
    })

    ElMessage.success('歌曲信息更新成功')
    emit('success')
    handleClose()

  } catch (error) {
    ElMessage.error('更新失败，请重试')
  } finally {
    submitting.value = false
  }
}

const refreshCover = async () => {
  if (!props.song) return

  refreshing.value = true
  try {
    await songsStore.refreshCover(props.song.id)
    ElMessage.success('封面刷新成功')
    emit('success')
  } catch (error) {
    ElMessage.error('封面刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 监听歌曲变化，初始化表单
watch(() => props.song, (newSong) => {
  if (newSong) {
    form.value = {
      title: newSong.title,
      artist: newSong.artist,
      album: newSong.album || ''
    }
  }
}, {immediate: true})

// 监听对话框显示，重置表单验证
watch(visible, (newVisible) => {
  if (newVisible && props.song) {
    form.value = {
      title: props.song.title,
      artist: props.song.artist,
      album: props.song.album || ''
    }
    formRef.value?.clearValidate()
  }
})
</script>

<style scoped>
.cover-section {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.current-cover {
  flex: 0 0 80px;
}

.cover-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
}

.cover-actions {
  flex: 1;
}

.cover-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.4;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>