import axios from 'axios'
import {ElMessage} from 'element-plus'
import {useAuthStore} from '@/stores/auth'

export const API_BASE_URL = 'http://localhost:8000'

// 创建axios实例
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,  // 增加到60秒
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true  // 添加凭证支持
})

// 请求拦截器
apiClient.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 响应拦截器
apiClient.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error) => {
        console.error('API Error:', error)  // 添加错误日志

        if (error.response) {
            const {status, data} = error.response

            switch (status) {
                case 401:
                    // 未授权，可能token过期
                    const authStore = useAuthStore()
                    authStore.logout()
                    window.location.href = '/login'
                    ElMessage.error('登录已过期，请重新登录')
                    break
                case 403:
                    ElMessage.error('没有权限执行此操作')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 409:
                    ElMessage.error(data.detail || data.message || '资源冲突')
                    break
                case 413:
                    ElMessage.error('文件太大')
                    break
                case 415:
                    ElMessage.error('不支持的文件格式')
                    break
                case 422:
                    ElMessage.error(data.detail || data.message || '数据验证失败')
                    break
                case 500:
                    ElMessage.error('服务器内部错误')
                    break
                default:
                    ElMessage.error(data.detail || data.message || '请求失败')
            }
        } else if (error.request) {
            // 请求已发送但没有收到响应
            console.error('Network Error:', error.message)
            ElMessage.error('网络连接失败，请检查后端服务是否启动')
        } else {
            // 请求配置出错
            console.error('Request Error:', error.message)
            ElMessage.error('请求配置错误')
        }

        return Promise.reject(error)
    }
)

export default apiClient