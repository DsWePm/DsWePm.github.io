// 导入路由创建函数
import { createRouter, createWebHistory } from 'vue-router'

// 导入视图组件（后面会创建）
import HomeView from '@/views/HomeView.vue'
import BlogView from '@/views/BlogView.vue'
import PostView from '@/views/PostView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

// 定义路由规则
const routes = [
  {
    path: '/',         // 访问根路径时
    name: 'home',      // 路由名称（用于导航）
    component: HomeView // 显示HomeView组件
  },
  {
    path: '/blog',
    name: 'blog',
    component: BlogView
  },
  {
    // :id是动态参数，可以匹配 /post/1, /post/abc 等
    path: '/blog/post/:id',
    name: 'post',
    component: PostView,
    props: true // 将路由参数作为props传给组件（推荐方式）
  },
  {
    // 匹配所有未定义的路由
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用浏览器History API
  routes // 应用定义的路由规则
})

export default router