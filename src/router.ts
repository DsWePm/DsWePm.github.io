import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'

// Home stays mounted (KeepAlive in App.vue) so the hero doesn't reload after reading a post.
// Scrolling is handled in composables/navigate.ts because Lenis owns the page scroll.
const PostView = () => import('./views/PostView.vue')

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    // these four notes were published as logs for a few hours before they were filed under their project
    ...['obs18-memory-and-safety', 'sac-pid-asymmetric-actor-critic', 'sim2real-actuator-and-latency', 'chain-integration-switching']
      .map((slug) => ({ path: `/log/${slug}`, redirect: `/projects/${slug}` })),
    { path: '/log/:slug', name: 'log', component: PostView, meta: { collection: 'log' } },
    { path: '/projects/:slug', name: 'projects', component: PostView, meta: { collection: 'projects' } },
    { path: '/file/:slug', redirect: (to) => `/log/${to.params.slug}` },
    { path: '/:rest(.*)', redirect: '/' },
  ],
})
