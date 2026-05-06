<template>
  <div
    class="floating-actions"
    @mouseenter="menuOpen = true"
    @mouseleave="menuOpen = false"
  >
    <button
      class="action-btn back-to-top"
      :class="{ visible: showBackToTop }"
      @click="scrollToTop"
      aria-label="Back to top"
    >
      <span class="debug-icon">&#9650;</span>
    </button>

    <div class="menu-items" :class="{ open: menuOpen }" :style="menuItemsStyle">
      <button
        v-for="(item, i) in actionItems"
        :key="item.id"
        class="action-btn menu-item-btn"
        :style="{ transitionDelay: `${i * 50}ms` }"
        @click="item.action?.()"
      >
        <span class="debug-icon">{{ item.debugIcon }}</span>
      </button>
    </div>

    <button
      class="action-btn menu-toggle"
      :class="{ active: menuOpen }"
      @click="menuOpen = !menuOpen"
      aria-label="Toggle menu"
    >
      <span class="debug-icon menu-toggle-icon" :class="{ open: menuOpen }">&#9776;</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { scrollYRatioKey } from '@/types/injectionKeys'

interface ActionItem {
  id: string
  debugIcon: string
  action?: () => void
}

const actionItems: ActionItem[] = [
  { id: 'item1', debugIcon: '1' },
  { id: 'item2', debugIcon: '2' },
  { id: 'item3', debugIcon: '3' },
]

const scrollYRatio = inject(scrollYRatioKey, ref(0))
const menuOpen = ref(false)
const itemCount = actionItems.length

const showBackToTop = computed(() => scrollYRatio.value > 0.05)

const menuItemsStyle = computed(() => ({
  '--item-count': itemCount,
}))

function scrollToTop() {
  const container = document.querySelector('.page-content')
  if (container) {
    container.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>

<style scoped>
.floating-actions {
  position: fixed;
  right: 28px;
  bottom: 40px;
  z-index: 900;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

/* ===== Shared button style ===== */
.action-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.debug-icon {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  transition: color 0.2s;
}

.action-btn:hover .debug-icon {
  color: #fff;
}

/* ===== Back to top ===== */
.back-to-top {
  opacity: 0;
  transform: translateY(8px);
  pointer-events: none;
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.back-to-top.visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

/* ===== Menu items container — matches TopbarDesktop submenu ===== */
.menu-items {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition:
    max-height 0.35s ease,
    opacity 0.25s ease;
}

.menu-items.open {
  max-height: calc(var(--item-count, 3) * 54px);
  opacity: 1;
}

.menu-item-btn {
  opacity: 0;
  transform: translateY(-8px);
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.menu-items.open .menu-item-btn {
  opacity: 1;
  transform: translateY(0);
}

/* ===== Menu toggle ===== */
.menu-toggle-icon {
  transition: transform 0.3s ease;
}

.menu-toggle-icon.open {
  transform: rotate(90deg);
}
</style>
