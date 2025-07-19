<template>
  <div id="app">
    <Preloader />
    <component
      :is="currentLayout"
    />
        <div
      class="page-content"
      :class="{
        'with-topbar': currentLayout==TopbarDesktop,
        'with-sidebar': currentLayout === Sidebar && !device.isMobile
       }"
    >
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDeviceStore } from '@/stores/device'
import Preloader from '@/components/layout/Preloader.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import TopbarDesktop from '@/components/layout/desktop/TopbarDesktop.vue'


const device = useDeviceStore()

onMounted(() => {
  device.detectDevice()
})

const currentLayout = computed(() => {
  if (device.isMobile) return Sidebar
  if (device.isDesktopButNarrow) return TopbarDesktop
  return Sidebar // 默认宽桌面布局
})

</script>

<style scoped>
#app {
  display: flex;
  font-family: 'Montserrat', sans-serif;
  position: relative;
}

.page-content {
  width: 100%;
}

.page-content.with-topbar {
  padding-top: 60px; /* 只在 TopbarDesktop 显示时添加 */
}

.page-content.with-sidebar {
    margin-left: var(--sidebar-width, 400px); /* 只在 TopbarDesktop 显示时添加 */
}
</style>
