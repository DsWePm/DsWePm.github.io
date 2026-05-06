import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDeviceStore = defineStore('device', () => {
  const isMobile = ref(false)
  const isDesktopButNarrow = ref(false)

  function detectDevice() {
    const width = window.innerWidth
    const ua = navigator.userAgent
    isMobile.value = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)
    isDesktopButNarrow.value = width < 1024
  }

  return { isMobile, isDesktopButNarrow, detectDevice }
})
