import {defineStore} from 'pinia'
import {ref} from 'vue'
import {authApi} from '@/api/auth'
import type {User, UserCreate} from '@/types'

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const token = ref<string | null>(null)
    const isAuthenticated = ref(false)

    // 初始化认证状态
    const initAuth = () => {
        const savedToken = localStorage.getItem('token')
        const savedUser = localStorage.getItem('user')

        if (savedToken && savedUser) {
            token.value = savedToken
            user.value = JSON.parse(savedUser)
            isAuthenticated.value = true
        }
    }

    // 登录
    const login = async (credentials: UserCreate) => {
        try {
            const response = await authApi.login(credentials)

            token.value = response.access_token
            isAuthenticated.value = true

            // 获取用户信息
            const userInfo = await authApi.getCurrentUser()
            user.value = userInfo

            // 保存到本地存储
            localStorage.setItem('token', response.access_token)
            localStorage.setItem('user', JSON.stringify(userInfo))

            return response
        } catch (error) {
            logout()
            throw error
        }
    }

    // 注册
    const register = async (userData: UserCreate) => {
        try {
            const response = await authApi.register(userData)
            return response
        } catch (error) {
            throw error
        }
    }

    // 退出登录
    const logout = () => {
        user.value = null
        token.value = null
        isAuthenticated.value = false

        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    // 获取当前用户信息
    const getCurrentUser = async () => {
        try {
            const userInfo = await authApi.getCurrentUser()
            user.value = userInfo
            localStorage.setItem('user', JSON.stringify(userInfo))
            return userInfo
        } catch (error) {
            logout()
            throw error
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        initAuth,
        login,
        register,
        logout,
        getCurrentUser
    }
})