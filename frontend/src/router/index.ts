import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
        },
        {
          path: 'blog',
          name: 'blog',
          component: () => import('@/views/BlogView.vue'),
        },
        {
          path: 'demo',
          name: 'demo',
          component: () => import('@/views/DemoView.vue'),
        },
        {
          path: 'collection',
          name: 'collection',
          component: () => import('@/views/CollectionView.vue'),
        },
        {
          path: 'stream',
          name: 'stream',
          component: () => import('@/views/StreamView.vue'),
        },
        {
          path: 'webGame',
          name: 'webgame',
          component: () => import('@/views/WebGameView.vue'),
        },
      ],
    },
  ],
})

export default router
