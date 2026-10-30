import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'

// Home stays mounted (KeepAlive in App.vue) so the hero doesn't reload after reading a post.
// Scrolling is handled in composables/navigate.ts because Lenis owns the page scroll.
const PostView = () => import('./views/PostView.vue')

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/log/:slug', name: 'log', component: PostView, meta: { collection: 'log' } },
    { path: '/projects/:slug', name: 'projects', component: PostView, meta: { collection: 'projects' } },
    { path: '/file/:slug', redirect: (to) => `/log/${to.params.slug}` },
    { path: '/:rest(.*)', redirect: '/' },
  ],
})
