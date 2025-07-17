<template>
  <aside class="desktop-sidebar">
    <!-- 背景图层 -->
    <div class="background-media">
      <video autoplay muted loop playsinline>
        <source src="@/assets/video/test.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <!-- 或者使用GIF -->
      <!-- <img src="@/assets/img/2.gif" alt="Background GIF" /> -->
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
        <p>Copyright &copy; 2025. <a target="_blank" href="https://github.com/DsWePm">DWP</a></p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { menuItems } from '@/components/layout/Sidebar/menuItems'

const hoverIndex = ref<number | null>(null)
</script>

<style scoped>
/* 主容器 */
.desktop-sidebar {
  position: relative;
  width: 400px;
  height: 100vh;
  overflow: hidden;
}

/* 背景媒体层（GIF 或视频） */
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

/* 毛玻璃内容层 */
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
  color: #fff;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.4);
}

/* Logo 样式 */
.logo {
  margin-top: 10%;
  margin-bottom: auto;
}

.logo img {
  max-width: 100%;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.2));
}

/* 菜单 */
.menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.menu li {
  text-align: center;
  margin: 15px 0;
  transition: all 0.3s ease;
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
}

/* 聚焦效果：当前项 */
.menu li.active a {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

/* 非选中项变小且轻微模糊 */
.menu li.faded a {
  transform: scale(0.9);
  filter: blur(1px);
  opacity: 0.5;
}

/* 页脚版权 */
.copyright {
  margin-top: auto;
  font-size: 13px;
  text-align: center;
  color: #aaa;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
