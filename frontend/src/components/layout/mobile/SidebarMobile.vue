<template>
  <div
    class="mobile-sidebar"
    :class="{ open: isOpen }"
    :style="maskStyle"
    @click.self="closeSidebar"
  >
    <nav class="sidebar-menu">
      <ul class="menu-list">
        <li v-for="item in menuItems" :key="item.label">
          <a :href="item.href">{{ item.label }}</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUIStore } from '@/stores/ui';
import { menuItems } from '@/components/layout/data/bar_menu/menuItems';

const uiStore = useUIStore();

const isOpen = computed(() => uiStore.sidebarOpen);
const centerX = computed(() => uiStore.hamburgerPos.x);
const centerY = computed(() => uiStore.hamburgerPos.y);

// 动态计算遮罩的clip-path半径，动画中用CSS transition
const maskStyle = computed(() => {
  if (!isOpen.value) {
    // 关闭状态：小圆 + 透明
    return {
      clipPath: `circle(20px at ${centerX.value}px ${centerY.value}px)`,
      opacity: 0,
    };
  } else {
    // 展开状态：大圆覆盖屏幕
    const maxRadius = Math.hypot(window.innerWidth, window.innerHeight);
    return {
      clipPath: `circle(${maxRadius}px at ${centerX.value}px ${centerY.value}px)`,
    };
  }
});

function closeSidebar() {
  uiStore.sidebarOpen = false;
}
</script>

<style scoped>
.mobile-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: white;
  overflow: hidden;
  pointer-events: none; /* 默认不可点 */
  z-index: 1000;

  /* 固定过渡属性：clip-path 和 opacity 同步过渡 */
  transition: clip-path 0.4s ease-in-out, opacity 0.4s ease-in-out;

  &.open {
    pointer-events: auto; /* 打开后可点击 */
  }
}

.sidebar-menu {
  padding: 60px 20px 20px 20px;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-list li {
  margin-bottom: 1.5rem;
}

.menu-list li a {
  text-decoration: none;
  font-size: 1.2rem;
  color: #333;
}
</style>