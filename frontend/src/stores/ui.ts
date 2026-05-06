import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const hamburgerPos = ref({ x: 30, y: 30 })
  const isPreloading = ref(true)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function setHamburgerPos(pos: { x: number; y: number }) {
    hamburgerPos.value = pos
  }

  function finishPreloading() {
    isPreloading.value = false
  }

  return {
    sidebarOpen,
    hamburgerPos,
    toggleSidebar,
    setHamburgerPos,
    closeSidebar,
    isPreloading,
    finishPreloading,
  }
})
