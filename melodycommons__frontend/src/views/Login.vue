<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1 class="logo">🎵 MelodyCommons</h1>
        <p class="subtitle">共享音乐库系统</p>
      </div>

      <el-card class="login-card">
        <el-tabs v-model="activeTab" class="login-tabs">
          <!-- 登录标签页 -->
          <el-tab-pane label="登录" name="login">
            <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                @submit.prevent="handleLogin"
            >
              <el-form-item prop="username">
                <el-input
                    v-model="loginForm.username"
                    placeholder="用户名"
                    size="large"
                    prefix-icon="User"
                    @keyup.enter="handleLogin"
                    autocomplete="username"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="密码"
                    size="large"
                    prefix-icon="Lock"
                    show-password
                    @keyup.enter="handleLogin"
                    autocomplete="new-password"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                    type="primary"
                    size="large"
                    style="width: 100%"
                    :loading="loginLoading"
                    @click="handleLogin"
                >
                  登录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 注册标签页 -->
          <el-tab-pane label="注册" name="register">
            <el-form
                ref="registerFormRef"
                :model="registerForm"
                :rules="registerRules"
                @submit.prevent="handleRegister"
            >
              <el-form-item prop="username">
                <el-input
                    v-model="registerForm.username"
                    placeholder="用户名"
                    size="large"
                    prefix-icon="User"
                    autocomplete="username"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                    v-model="registerForm.password"
                    type="password"
                    placeholder="密码"
                    size="large"
                    prefix-icon="Lock"
                    show-password
                    autocomplete="new-password"
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                    v-model="registerForm.confirmPassword"
                    type="password"
                    placeholder="确认密码"
                    size="large"
                    prefix-icon="Lock"
                    show-password
                    @keyup.enter="handleRegister"
                    autocomplete="new-password"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                    type="primary"
                    size="large"
                    style="width: 100%"
                    :loading="registerLoading"
                    @click="handleRegister"
                >
                  注册
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <div class="login-footer">
        <p>本地部署的共享音乐库系统</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, type FormInstance, type FormRules} from 'element-plus'
import {useAuthStore} from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateUsername = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3) {
    callback(new Error('用户名至少3个字符'))
  } else if (value.length > 20) {
    callback(new Error('用户名不能超过20个字符'))
  } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字和下划线'))
  } else {
    callback()
  }
}

const validatePassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6个字符'))
  } else if (value.length > 50) {
    callback(new Error('密码不能超过50个字符'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const loginRules: FormRules = {
  username: [{validator: validateUsername, trigger: 'blur'}],
  password: [{validator: validatePassword, trigger: 'blur'}]
}

const registerRules: FormRules = {
  username: [{validator: validateUsername, trigger: 'blur'}],
  password: [{validator: validatePassword, trigger: 'blur'}],
  confirmPassword: [{validator: validateConfirmPassword, trigger: 'blur'}]
}

const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()

    loginLoading.value = true

    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    ElMessage.success('登录成功')
    router.push('/songs')

  } catch (error: any) {
    if (error.response?.status === 401) {
      ElMessage.error('用户名或密码错误')
    } else {
      ElMessage.error('登录失败，请重试')
    }
  } finally {
    loginLoading.value = false
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value?.validate()

    registerLoading.value = true

    await authStore.register({
      username: registerForm.username,
      password: registerForm.password
    })

    ElMessage.success('注册成功，请登录')

    const registeredUsername = registerForm.username;
    registerForm.username = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    activeTab.value = 'login'

    loginForm.username = registeredUsername

  } catch (error: any) {
    if (error.response?.status === 409) {
      ElMessage.error('用户名已存在')
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 36px;
  font-weight: bold;
  color: white;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.login-tabs {
  padding: 24px;
}

:deep(.el-tabs__header) {
  margin-bottom: 24px;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.login-footer p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 0;
}
</style>