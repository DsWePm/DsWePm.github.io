<template>
  <div id="app">
    <!-- 初始显示 Preloader -->
    <Preloader />
    <RouterView />

    <!-- 加载完成后再显示主视图 -->
    <HomeView v-if="!uiStore.isPreloading" />
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
import Preloader from '@/components/layout/Preloader.vue'
import HomeView from '@/views/HomeView.vue'

const uiStore = useUIStore()
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  font-family: 'Montserrat', sans-serif;
  position: relative;
  background-color: #fff; /* 可选：确保背景干净 */
}

</style>
