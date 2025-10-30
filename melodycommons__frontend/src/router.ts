import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: {requiresAuth: false}
    },
    {
        path: '/',
        redirect: '/songs'
    },
    {
        path: '/songs',
        name: 'Songs',
        component: () => import('@/views/Songs.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/playlists',
        name: 'Playlists',
        component: () => import('@/views/Playlists.vue'),
        meta: {requiresAuth: true}
    },
    {
        path: '/playlists/:id',
        name: 'PlaylistDetail',
        component: () => import('@/components/Playlist/PlaylistDetail.vue'),
        meta: {requiresAuth: true}
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
    const authStore = useAuthStore()

    // 初始化认证状态
    if (!authStore.isAuthenticated) {
        authStore.initAuth()
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login')
    } else if (to.path === '/login' && authStore.isAuthenticated) {
        next('/songs')
    } else {
        next()
    }
})

export default router