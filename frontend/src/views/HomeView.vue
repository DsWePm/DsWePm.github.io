<template>
  <component :is="currentLayout" />
  <div
    class="page-content"
    ref="pageContentRef"
    :class="pageContentClasses"
    :style="pageContentStyles"
  >
    <HeroSection />
    <AboutSection />
    <PortfolioSection />
    <SkillsSection />
    <NewsSection />
    <PartnersSection />
    <ContactFormSection />
    <Footer />
  </div>
</template>

<script setup lang="ts">
// Import sections
import HeroSection from '@/components/sections/desktop/HeroSection.vue'
import AboutSection from '@/components/sections/desktop/AboutSection.vue'
import PortfolioSection from '@/components/sections/desktop/PortfolioSection.vue'
import SkillsSection from '@/components/sections/desktop/SkillsSection.vue'
import NewsSection from '@/components/sections/desktop/NewsSection.vue'
import PartnersSection from '@/components/sections/desktop/PartnersSection.vue'
import ContactFormSection from '@/components/sections/desktop/ContactFormSection.vue'

// Import layout components
import Sidebar from '@/components/layout/Sidebar.vue'
import TopbarDesktop from '@/components/layout/desktop/TopbarDesktop.vue'
import Footer from '@/components/layout/Footer.vue'

// Import functions and stores
import { provide, ref, onMounted, onBeforeUnmount, computed } from 'vue'
import type { CSSProperties } from 'vue'
import { useDeviceStore } from '@/stores/device'


// Layout and styling
const device = useDeviceStore()
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

const pageContentStyles = computed<CSSProperties>(() => {
  if (pageContentClasses.value['with-sidebar']) {
    return {
      width: `calc(100vw - var(--sidebar-width, 400px))`,
      marginLeft: `var(--sidebar-width, 400px)`,
      paddingTop: '0',
      height: '100vh',
      boxSizing: 'border-box' as const,
      overflowX: 'auto',
    }
  }
  if (pageContentClasses.value['with-topbar']) {
    return {
      width: '100vw',
      marginLeft: '0',
      paddingTop: '60px',
      height: '100vh',
      boxSizing: 'border-box' as const,
      overflowX: 'hidden',
    }
  }
  if (pageContentClasses.value['mobile']) {
    return {
      width: '100vw',
      marginLeft: '0',
      paddingTop: '0',
      height: '100vh',
      boxSizing: 'border-box' as const,
      overflowX: 'hidden',
    }
  }
  // Default case for desktop layout
  return {
    width: '100vw',
    marginLeft: '0',
    paddingTop: '0',
    height: '100vh',
    boxSizing: 'border-box' as const,
    overflowX: 'auto',
  }
})


// Scroll handling
const scrollY = ref(0)
const pageContentRef = ref<HTMLElement | null>(null)
provide('scrollY', scrollY)

function handleScroll() {
  if (pageContentRef.value) {
    scrollY.value = pageContentRef.value.scrollTop
  }
}

onMounted(() => {
  device.detectDevice()
  if (pageContentRef.value) {
    pageContentRef.value.addEventListener('scroll', handleScroll)
  }
})
onBeforeUnmount(() => {
  if (pageContentRef.value) {
    pageContentRef.value.removeEventListener('scroll', handleScroll)
  }
})
</script>


<style scoped>
</style>