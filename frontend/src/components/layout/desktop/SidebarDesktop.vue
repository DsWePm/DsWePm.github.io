<template>
  <aside class="desktop-sidebar">
    <!-- 背景图层 -->
    <div class="background-media">
      <video autoplay muted loop playsinline>
        <source src="@/assets/video/test.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>

    <!-- 毛玻璃遮罩和内容 -->
    <div class="leftpart_inner blur-layer">
      <div class="logo">
        <RouterLink to="#home">
          <img src="~@/assets/logo/light.png" alt="Logo" />
        </RouterLink>
      </div>

      <nav class="menu">
        <ul @mouseleave="hoverIndex = null">
          <li
            v-for="(item, index) in menuItems"
            :key="index"
            :class="{
              active: hoverIndex === index,
              faded: hoverIndex !== null && hoverIndex !== index,
            }"
            @mouseenter="hoverIndex = index"
          >
            <a :href="item.href">{{ item.label }}</a>
          </li>
        </ul>
      </nav>

      <div class="copyright">
        <p>
          Copyright &copy; 2025.
          <a target="_blank" href="https://github.com/DsWePm">DWP</a>
        </p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { menuItems } from '@/components/layout/data/bar_menu/menuItems'

const hoverIndex = ref<number | null>(null)
</script>

<style scoped>
.desktop-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width, 400px);
  height: 100vh;
  overflow: hidden;
  z-index: 1000;
}

.background-media {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.background-media video,
.background-media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blur-layer {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中所有子元素 */
  color: #fff;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.4);
}

/* Logo 区域 - 上边留白并水平居中 */
.logo {
  flex: 0 0 auto;
  margin-top: 5vh; /* 视口高度的 5% 自适应留白 */
  margin-bottom: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.logo img {
  max-width: 70%;
  height: auto;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.2));
}

/* Menu 主体自适应居中区域 */
.menu {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  justify-content: center; /* 垂直居中 */
  overflow-y: auto;
  padding: 0 10px;
}

.menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
}

.menu li {
  text-align: center;
  margin: 15px 0;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 260px;
}

.menu a {
  color: #ddd;
  text-decoration: none;
  font-weight: 500;
  padding: 10px 12px;
  display: block;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 16px;
  text-align: center;
}

/* 活跃状态放大加粗 */
.menu li.active a {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

/* hover 淡出效果 */
.menu li.faded a {
  transform: scale(0.9);
  filter: blur(1px);
  opacity: 0.5;
}

/* 页脚版权始终在底部并水平居中 */
.copyright {
  flex: 0 0 auto;
  font-size: 13px;
  text-align: center;
  color: #aaa;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  width: 100%;
}
</style>
