<template>
  <header class="app-header">
    <div class="header-left">
      <h1 class="logo">🎵 MelodyCommons</h1>
    </div>

    <div class="header-right">
      <el-dropdown @command="handleUserAction" trigger="click">
        <div class="user-avatar">
          <el-avatar>{{ authStore.user?.username?.charAt(0).toUpperCase() }}</el-avatar>
          <span class="username">{{ authStore.user?.username }}</span>
          <el-icon class="arrow-down">
            <ArrowDown/>
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人信息</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import {useRouter} from 'vue-router'
import {ElMessage} from 'element-plus'
import {ArrowDown} from '@element-plus/icons-vue' // 移除了未使用的 Search 图标
import {useAuthStore} from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleUserAction = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break;
    case 'logout':
      authStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
      break;
  }
}
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  /* === 修改开始 === */
  background: rgba(255, 255, 255, 0.7); /* 半透明背景 */
  backdrop-filter: blur(10px) saturate(180%); /* 磨砂玻璃效果 */
  -webkit-backdrop-filter: blur(10px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2); /* 半透明边框 */
  /* === 修改结束 === */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-6);
  flex-shrink: 0;
  z-index: var(--z-index-header);
}

.logo {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: var(--color-primary);
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-md);
  transition: background-color 0.2s ease;
}

.user-avatar:hover {
  background-color: rgba(255, 255, 255, 0.3); /* 悬浮效果也改为半透明 */
}

.username {
  font-size: 14px;
  color: var(--color-text-regular);
}

.arrow-down {
  color: var(--color-text-secondary);
}
</style>