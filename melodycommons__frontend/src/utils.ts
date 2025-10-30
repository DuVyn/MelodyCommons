// 格式化时间
export const formatTime = (seconds: number): string => {
    if (!seconds || isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 格式化文件大小
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
export const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

// 防抖函数
export const debounce = <T extends (...args: any[]) => any>(
    func: T,
    wait: number
): ((...args: Parameters<T>) => void) => {
    let timeout: NodeJS.Timeout
    return (...args: Parameters<T>) => {
        clearTimeout(timeout)
        timeout = setTimeout(() => func.apply(null, args), wait)
    }
}

// 节流函数
export const throttle = <T extends (...args: any[]) => any>(
    func: T,
    limit: number
): ((...args: Parameters<T>) => void) => {
    let inThrottle: boolean
    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            func.apply(null, args)
            inThrottle = true
            setTimeout(() => inThrottle = false, limit)
        }
    }
}

// 检查是否为有效的音频文件
export const isValidAudioFile = (filename: string): boolean => {
    const allowedExtensions = ['.mp3', '.flac', '.wav']
    const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'))
    return allowedExtensions.includes(extension)
}

// 生成随机ID
export const generateId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
}