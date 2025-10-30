import apiClient from './index'
import type {User, UserCreate, Token} from '@/types'

export const authApi = {
    // 登录
    login: (credentials: UserCreate): Promise<Token> => {
        return apiClient.post('/auth/login', credentials)
    },

    // 注册
    register: (userData: UserCreate): Promise<User> => {
        return apiClient.post('/auth/register', userData)
    },

    // 获取当前用户信息
    getCurrentUser: (): Promise<User> => {
        return apiClient.get('/auth/me')
    }
}