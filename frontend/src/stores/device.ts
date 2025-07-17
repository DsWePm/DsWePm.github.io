// stores/device.ts
import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'

export const useDeviceStore = defineStore('device', () => {
  const isMobile = ref(false)
  const isDesktopButNarrow = ref(false)

  function detectDevice() {
    const check = () => {
      const width = window.innerWidth
      const ua = navigator.userAgent
      isMobile.value = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)
      isDesktopButNarrow.value = width < 1024 // 自定义“窄桌面”的阈值
    }

    check()
    window.addEventListener('resize', check)
  }

  onMounted(() => {
    detectDevice()
  })

  return { isMobile, isDesktopButNarrow, detectDevice }
})
