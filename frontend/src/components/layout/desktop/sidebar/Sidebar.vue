<template>
  <div>
    <!-- 移动端菜单按钮 -->
    <transition name="fade">
      <button v-if="!uiStore.isPreloading && device.isMobile" ref="hamburgerRef" class="menu-toggle"
        :class="{ active: uiStore.sidebarOpen }" @click="uiStore.toggleSidebar" aria-label="Toggle Menu">
        <span class="hamburger-icon"></span>
      </button>
    </transition>


    <!-- 使用移动或桌面 Sidebar -->
    <component :is="device.isMobile ? SidebarMobile : SidebarDesktop" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useDeviceStore } from '@/stores/device'
import { useUIStore } from '@/stores/ui'
import SidebarDesktop from './SidebarDesktop.vue'
import SidebarMobile from './SidebarMobile.vue'

const device = useDeviceStore()
const uiStore = useUIStore()

const hamburgerRef = ref<HTMLElement | null>(null)


function updateHamburgerPos() {
  if (hamburgerRef.value) {
    const rect = hamburgerRef.value.getBoundingClientRect()
    uiStore.setHamburgerPos({
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    })
  }
}


watch(() => device.isMobile, (isMobile) => {
  if (!isMobile) {
    uiStore.closeSidebar()
  }
})

const onResize = () => {
  nextTick(updateHamburgerPos)
}

onMounted(() => {
  nextTick(updateHamburgerPos)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>


<style scoped>
.menu-toggle {
  position: fixed;
  top: 10px;
  left: 10px;
  z-index: 9999;
  /* 保证始终在最上层 */
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  border-radius: 50%;
  /* 圆形背景 */
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition:
    top 0.4s ease,
    left 0.4s ease,
    width 0.4s ease,
    height 0.4s ease,
    border-radius 0.4s ease,
    background-color 0.4s ease;
}

.menu-toggle.active {
  background: transparent;
  box-shadow: none;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.6s ease;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: scale(1);
}

.hamburger-icon {
  display: block;
  position: relative;
  width: 20px;
  height: 2px;
  background-color: #333;
  border-radius: 1px;
  transition: all 0.3s ease;
  margin: auto;
}

.hamburger-icon::before,
.hamburger-icon::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  background-color: #333;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.hamburger-icon::before {
  top: -6px;
  left: 0;
}

.hamburger-icon::after {
  top: 6px;
  left: 0;
}

.menu-toggle.active .hamburger-icon {
  background: transparent;
}

.menu-toggle.active .hamburger-icon::before {
  top: 0;
  transform: rotate(45deg);
}

.menu-toggle.active .hamburger-icon::after {
  top: 0;
  transform: rotate(-45deg);
}
</style>
