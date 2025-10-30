<template>
  <router-view v-if="!isAuthenticated"/>
  <div v-else class="app-layout">
    <Header/>
    <div class="app-main">
      <Sidebar/>
      <main class="app-content">
        <router-view/>
      </main>
    </div>
    <PlayerBar/>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted} from 'vue'
import {useAuthStore} from '@/stores/auth'
import Header from '@/components/Layout/Header.vue'
import Sidebar from '@/components/Layout/Sidebar.vue'
import PlayerBar from '@/components/Layout/PlayerBar.vue'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(() => {
  authStore.initAuth()
})
</script>
