<template>
  <el-dialog
      v-model="visible"
      :title="isEdit ? '编辑歌单' : '创建歌单'"
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
      <el-form-item label="歌单名称" prop="name">
        <el-input
            v-model="form.name"
            placeholder="请输入歌单名称"
            maxlength="50"
            show-word-limit
            @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入歌单描述（可选）"
            :rows="4"
            maxlength="200"
            show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
            type="primary"
            @click="handleSubmit"
            :loading="submitting"
            :disabled="!form.name.trim()"
        >
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {ref, computed, watch} from 'vue'
import {ElMessage, type FormInstance, type FormRules} from 'element-plus'
import {usePlaylistsStore} from '@/stores/playlists'
import type {Playlist} from '@/types'

interface Props {
  modelValue: boolean
  playlist?: Playlist | null
}

const props = withDefaults(defineProps<Props>(), {
  playlist: null
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: [playlist: Playlist]
}>()

const playlistsStore = usePlaylistsStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.playlist)

const form = ref({
  name: '',
  description: ''
})

const rules: FormRules = {
  name: [
    {required: true, message: '请输入歌单名称', trigger: 'blur'},
    {min: 1, max: 50, message: '歌单名称长度应在 1-50 个字符', trigger: 'blur'}
  ],
  description: [
    {max: 200, message: '描述长度不能超过 200 个字符', trigger: 'blur'}
  ]
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

const resetForm = () => {
  form.value = {
    name: '',
    description: ''
  }
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    submitting.value = true

    const formData = {
      name: form.value.name.trim(),
      description: form.value.description.trim() || undefined
    }

    let result: Playlist

    if (isEdit.value && props.playlist) {
      // 编辑模式
      result = await playlistsStore.updatePlaylist(props.playlist.id, formData)
      ElMessage.success('歌单信息更新成功')
    } else {
      // 创建模式
      result = await playlistsStore.createPlaylist(formData)
      ElMessage.success('歌单创建成功')
    }

    emit('success', result)
    handleClose()

  } catch (error: any) {
    if (error.response?.status === 409) {
      ElMessage.error('歌单名称已存在')
    } else {
      ElMessage.error(isEdit.value ? '更新失败，请重试' : '创建失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

// 监听歌单变化，初始化表单
watch(() => props.playlist, (newPlaylist) => {
  if (newPlaylist) {
    form.value = {
      name: newPlaylist.name,
      description: newPlaylist.description || ''
    }
  }
}, {immediate: true})

// 监听对话框显示，重置表单
watch(visible, (newVisible) => {
  if (newVisible) {
    if (props.playlist) {
      form.value = {
        name: props.playlist.name,
        description: props.playlist.description || ''
      }
    } else {
      resetForm()
    }
    formRef.value?.clearValidate()
  }
})
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>