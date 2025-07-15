<template>
  <div id="app" class="app-wrapper">
    <!-- 页面预加载器 -->
    <Preloader />

    <!-- 顶部导航栏 -->
    <Header />

    <!-- 移动菜单（仅在小屏时显示） -->
    <MobileMenu />

    <!-- 主体内容由路由渲染 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 页脚 -->
    <Footer />

    <!-- 返回顶部按钮 -->
    <BackToTopButton />
  </div>
</template>

<script lang="ts" setup>
// 全局样式，在 main.ts 中已经 import '@/assets/css/style.css'
import Preloader from '@/components/layout/Preloader.vue';
import Header from '@/components/layout/Header.vue';
import MobileMenu from '@/components/layout/MobileMenu.vue';
import Footer from '@/components/layout/Footer.vue';
import BackToTopButton from '@/components/layout/BackToTopButton.vue';
</script>

<style>
/* 全局未 scoped 的布局样式 */

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f9fafb;
}

/* main 部分撑满剩余空间 */
.main-content {
  flex: 1;
}

/* 控制 Header 和 Footer 宽度及居中 */
header,
footer {
  width: 100%;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 返回顶部按钮固定到页面右下角 */
.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 100;
}

/* 在小屏幕隐藏主导航，显示移动菜单按钮 */
/* 你可以在 Header.vue 中配合 media query 控制具体元素显示/隐藏 */
@media (max-width: 768px) {
  .main-content {
    padding-top: 0; /* 如果 Header 在小屏中占用额外高度，可在此修正 */
  }
}
</style>
