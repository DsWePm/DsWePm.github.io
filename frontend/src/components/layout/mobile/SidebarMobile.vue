<template>
  <div
    class="mobile-sidebar"
    :class="{ open: isOpen }"
    :style="maskStyle"
    @click.self="closeSidebar"
  >
    <nav class="sidebar-nav">
      <ul class="menu-list">
        <li
          v-for="item in menuItems"
          :key="item.label"
          class="menu-item"
        >
          <a
            href="javascript:void(0)"
            class="menu-link"
            :class="{ 'has-children': item.children }"
            @click="item.children ? toggleExpand(item.label) : navigateTo(item.href)"
          >
            {{ item.label }}
            <span v-if="item.children" class="arrow" :class="{ expanded: expandedItem === item.label }">
              &#9662;
            </span>
          </a>
          <ul
            v-if="item.children"
            class="submenu"
            :class="{ open: expandedItem === item.label }"
          >
            <li
              v-for="(child, i) in item.children"
              :key="child.label"
              class="submenu-item"
              :style="{ transitionDelay: `${i * 50}ms` }"
            >
              <a
                href="javascript:void(0)"
                class="submenu-link"
                @click="navigateTo(child.href)"
              >
                {{ child.label }}
              </a>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useUIStore } from '@/stores/ui'
import { menuItems } from '@/components/layout/data/bar_menu/menuItems'
import { useScroll } from '@/utils/useScroll'

const uiStore = useUIStore()
const { scrollToSection } = useScroll()

const expandedItem = ref<string | null>(null)

const isOpen = computed(() => uiStore.sidebarOpen)
const centerX = computed(() => uiStore.hamburgerPos.x)
const centerY = computed(() => uiStore.hamburgerPos.y)

const maskStyle = computed(() => {
  if (!isOpen.value) {
    return {
      clipPath: `circle(20px at ${centerX.value}px ${centerY.value}px)`,
      opacity: 0,
    }
  }
  const maxRadius = Math.hypot(window.innerWidth, window.innerHeight)
  return {
    clipPath: `circle(${maxRadius}px at ${centerX.value}px ${centerY.value}px)`,
  }
})

function toggleExpand(label: string) {
  expandedItem.value = expandedItem.value === label ? null : label
}

function navigateTo(href: string) {
  const id = href.replace('#', '')
  closeSidebar()
  scrollToSection(id)
}

function closeSidebar() {
  uiStore.closeSidebar()
}
</script>

<style scoped>
.mobile-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #fff;
  overflow-y: auto;
  pointer-events: none;
  z-index: 1000;
  transition: clip-path 0.4s ease-in-out, opacity 0.4s ease-in-out;
}

.mobile-sidebar.open {
  pointer-events: auto;
}

.sidebar-nav {
  padding: 80px 32px 40px 32px;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin-bottom: 4px;
}

.menu-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
  color: #1a1a1a;
  padding: 14px 0;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: color 0.2s;
}

.menu-link:hover,
.menu-link:active {
  color: #000;
}

.arrow {
  font-size: 12px;
  opacity: 0.5;
  transition: transform 0.25s ease;
}

.arrow.expanded {
  transform: rotate(180deg);
}

/* ===== Submenu ===== */
.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition:
    max-height 0.35s ease,
    opacity 0.25s ease;
}

.submenu.open {
  max-height: 300px;
  opacity: 1;
}

.submenu-item {
  opacity: 0;
  transform: translateX(-8px);
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.submenu.open .submenu-item {
  opacity: 1;
  transform: translateX(0);
}

.submenu-link {
  display: block;
  padding: 10px 0 10px 20px;
  color: #1a1a1a;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 400;
  border-left: 2px solid #333;
  margin-left: 8px;
  cursor: pointer;
  transition:
    border-color 0.2s,
    padding-left 0.2s;
}

.submenu-link:hover,
.submenu-link:active {
  border-left-color: #000;
  padding-left: 28px;
}
</style>
