import {createApp} from 'vue'
import {createPinia} from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

import './main.css'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 生产环境禁用调试信息
if (import.meta.env.PROD) {
    app.config.globalProperties.$devtools = false
    console.log = () => {
    }
    console.debug = () => {
    }
    console.info = () => {
    }
    console.warn = () => {
    }
}

app.mount('#app')