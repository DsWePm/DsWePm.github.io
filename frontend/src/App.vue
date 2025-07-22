<template>
  <div id="app">
    <Preloader v-if="!useUIStore.isPreloading" />
    <component :is="currentLayout" />
    <div
      class="page-content"
      :class="pageContentClasses"
      :style="pageContentStyles"
    >
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useDeviceStore } from '@/stores/device'
import { useUIStore } from '@/stores/ui'
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

const pageContentClasses = computed(() => ({
  'with-topbar': !device.isMobile && currentLayout.value === TopbarDesktop,
  'with-sidebar': !device.isMobile && currentLayout.value === Sidebar,
  'mobile': device.isMobile,
}))

const pageContentStyles = computed(() => {
  if (pageContentClasses.value['with-sidebar']) {
    return {
      width: `calc(100vw - var(--sidebar-width, 400px))`,
      marginLeft: `var(--sidebar-width, 400px)`,
      paddingTop: '0',
      height: '100vh',
      boxSizing: 'border-box',
      overflowX: 'hidden',
    }
  }
  if (pageContentClasses.value['with-topbar']) {
    return {
      width: '100vw',
      marginLeft: '0',
      paddingTop: '60px',
      height: '100vh',
      boxSizing: 'border-box',
      overflowX: 'hidden',
    }
  }
  if (pageContentClasses.value['mobile']) {
    return {
      width: '100vw',
      marginLeft: '0',
      paddingTop: '0',
      height: '100vh',
      boxSizing: 'border-box',
      overflowX: 'hidden',
    }
  }
  // 默认样式
  return {
    width: '100vw',
    marginLeft: '0',
    paddingTop: '0',
    height: '100vh',
    boxSizing: 'border-box',
    overflowX: 'hidden',
  }
})
</script>

<style scoped>
#app {
  display: flex;
  font-family: 'Montserrat', sans-serif;
  position: relative;
  height: 100vh;
  overflow: hidden;
}

.page-content {
  /* 这里的基础样式已由动态样式覆盖 */
}

/* 你可以保留下面的class方便调试或备用 */
.page-content.with-topbar {
  /* padding-top: 60px; 由动态style处理 */
}

.page-content.with-sidebar {
  /* margin-left: var(--sidebar-width, 400px); 由动态style处理 */
}

.page-content.mobile {
  /* 移动端无额外样式 */
}
</style>
