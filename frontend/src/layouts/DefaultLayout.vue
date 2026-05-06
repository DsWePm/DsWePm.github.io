<template>
  <TopbarDesktop v-if="!device.isMobile" />
  <Sidebar v-if="device.isMobile" />
  <div
    class="page-content"
    ref="pageContentRef"
  >
    <RouterView />
  </div>
  <FloatingActions />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, provide } from 'vue'
import { useDeviceStore } from '@/stores/device'
import { scrollYRatioKey } from '@/types/injectionKeys'

import Sidebar from '@/components/layout/Sidebar.vue'
import TopbarDesktop from '@/components/layout/desktop/TopbarDesktop.vue'
import FloatingActions from '@/components/layout/FloatingActions.vue'

const device = useDeviceStore()

const scrollYRatio = ref(0)
const pageContentRef = ref<HTMLElement | null>(null)
provide(scrollYRatioKey, scrollYRatio)

function handleScroll() {
  if (pageContentRef.value) {
    scrollYRatio.value = pageContentRef.value.scrollTop / pageContentRef.value.scrollHeight
  }
}

onMounted(() => {
  device.detectDevice()
  pageContentRef.value?.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  pageContentRef.value?.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.page-content {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
}
</style>
