<template>
  <nav class="topbar" :class="{ hidden: isHidden }" @mouseenter="onBarEnter" @mouseleave="onBarLeave">
    <ul class="menu">
      <li
        v-for="item in menuItems"
        :key="item.label"
        class="menu-item"
        @mouseenter="activeSubmenu = item.label"
        @mouseleave="activeSubmenu = null"
      >
        <a
          href="javascript:void(0)"
          class="menu-link"
          @click.prevent="scrollToSection(item.href.replace('#', ''))"
        >
          {{ item.label }}
          <span v-if="item.children" class="arrow">&#9662;</span>
        </a>
        <ul
          v-if="item.children"
          class="submenu"
          :class="{ open: activeSubmenu === item.label }"
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
              @click.prevent="scrollToSection(child.href.replace('#', ''))"
            >
              {{ child.label }}
            </a>
          </li>
        </ul>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
import { ref, inject, onMounted, onUnmounted } from 'vue'
import { menuItems } from '@/components/layout/data/bar_menu/menuItems'
import { scrollYRatioKey } from '@/types/injectionKeys'
import { useScroll } from '@/utils/useScroll'

const { scrollToSection } = useScroll()
const scrollYRatio = inject(scrollYRatioKey, ref(0))

const activeSubmenu = ref<string | null>(null)
const isHidden = ref(false)

let mouseNearTop = false
let mouseOnBar = false

function updateHidden() {
  const scrolled = scrollYRatio.value > 0.01
  isHidden.value = scrolled && !mouseNearTop && !mouseOnBar
}

function onMouseMove(e: MouseEvent) {
  mouseNearTop = e.clientY < 80
  updateHidden()
}

function onBarEnter() {
  mouseOnBar = true
  updateHidden()
}

function onBarLeave() {
  mouseOnBar = false
  updateHidden()
}

onMounted(() => {
  document.addEventListener('mousemove', onMouseMove)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
})
</script>

<style scoped>
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  transition:
    opacity 0.35s ease,
    transform 0.35s ease;
}

.topbar.hidden {
  opacity: 0;
  transform: translateY(-100%);
  pointer-events: none;
}

.menu {
  list-style: none;
  display: flex;
  gap: 2.5rem;
  margin: 0;
  padding: 0;
}

.menu-item {
  position: relative;
}

.menu-link {
  color: #1a1a1a;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
  padding: 8px 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: color 0.2s;
}

.menu-link:hover {
  color: #000;
}

.arrow {
  font-size: 10px;
  opacity: 0.6;
  transition: transform 0.2s;
}

.menu-item:hover .arrow {
  transform: rotate(180deg);
}

/* ===== Submenu ===== */
.submenu {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  list-style: none;
  margin: 0;
  padding: 6px 0;
  min-width: 170px;
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition:
    max-height 0.35s ease,
    opacity 0.25s ease;
  pointer-events: none;
}

.submenu.open {
  max-height: 300px;
  opacity: 1;
  pointer-events: auto;
}

.submenu-item {
  opacity: 0;
  transform: translateY(-8px);
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.submenu.open .submenu-item {
  opacity: 1;
  transform: translateY(0);
}

.submenu-link {
  display: block;
  padding: 8px 16px;
  color: #1a1a1a;
  text-decoration: none;
  font-size: 14px;
  font-weight: 400;
  border-left: 2px solid #333;
  margin-left: 8px;
  cursor: pointer;
  transition:
    border-color 0.2s,
    color 0.2s,
    padding-left 0.2s;
}

.submenu-link:hover {
  border-left-color: #000;
  padding-left: 24px;
  color: #000;
}
</style>
