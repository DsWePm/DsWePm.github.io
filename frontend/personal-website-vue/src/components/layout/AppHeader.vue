<template>
  <header class="app-header">
    <!-- router-link 是 Vue Router 提供的导航组件 -->
    <router-link to="/" class="logo">
      <!-- logo 可以先放文字 -->
      我的技术博客
    </router-link>
    
    <!-- 导航菜单 -->
    <nav class="nav-menu">
      <!-- :class="{}" 动态绑定类名，根据当前路由高亮菜单 -->
      <router-link 
        to="/" 
        :class="{ active: $route.path === '/' }"
      >
        首页
      </router-link>
      <router-link 
        to="/blog"
        :class="{ active: $route.path.startsWith('/blog') }"
      >
        博客
      </router-link>
      <router-link 
        to="/live"
        :class="{ active: $route.path.startsWith('/live') }"
      >
        直播
      </router-link>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'AppHeader'
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: #333;
}

.nav-menu a {
  margin-left: 1.5rem;
  text-decoration: none;
  color: #555;
  position: relative;
}

.nav-menu a:hover {
  color: #007bff;
}

.nav-menu a.active {
  color: #007bff;
  font-weight: bold;
}

/* 在活动链接下方添加指示条 */
.nav-menu a.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #007bff;
}
</style>