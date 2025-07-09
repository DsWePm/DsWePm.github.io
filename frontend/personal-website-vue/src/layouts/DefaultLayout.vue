<template>
  <div class="default-layout">
    <!-- 顶部导航 -->
    <AppHeader />
    
    <!-- 主内容区 -->
    <main class="main-content">
      <!-- slot是插槽，放置页面内容 -->
      <slot />
    </main>
    
    <!-- 底部信息 -->
    <AppFooter />
  </div>
</template>

<script>
// 导入组件
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

export default {
  name: 'DefaultLayout',
  components: {
    AppHeader,
    AppFooter
  }
}
</script>

<style scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* 确保布局占满整个屏幕高度 */
}

.main-content {
  flex: 1; /* 占据剩余空间 */
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}
</style>