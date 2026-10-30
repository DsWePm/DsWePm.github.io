<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { toHome, toSection } from '../composables/navigate'
import { router } from '../router'
import { profile } from '../data/profile'
import { categoriesIn, entries, type Collection } from '../data/posts'
import { years } from '../data/timeline'
import { filters } from '../composables/filters'
import { lang, theme, tr } from '../composables/prefs'
import { switchFrom } from '../composables/switchFx'
import NavMenu, { type MenuGroup } from './NavMenu.vue'

const BASE = import.meta.env.BASE_URL
const items = [['archive', 'Archive'], ['log', 'Log'], ['projects', 'Projects'], ['about', 'About'], ['timeline', 'Timeline'], ['contact', 'Contact']]

// Log and Projects drop their categories, Timeline its years
function show(c: Collection, cat: string) { filters[c] = cat; toSection(c) }
function entryGroups(c: Collection): MenuGroup[] {
  return [
    { key: 'all', label: tr({ zh: '全部', en: 'All' }), count: entries[c].length, go: () => show(c, 'all') },
    ...categoriesIn(c).map((g) => ({ key: g.category.id, label: tr(g.category.name), count: g.items.length, go: () => show(c, g.category.id) })),
  ]
}
const menus = computed<Record<string, MenuGroup[]>>(() => ({
  log: entryGroups('log'),
  projects: entryGroups('projects'),
  timeline: years.map((y) => ({ key: y.id, label: String(y.year), count: y.items.length, go: () => toSection(y.id) })),
}))

// The white slab and the paper-coloured pages take dark ink. Dark bands mark themselves
// data-nav-dark (a post's header; the pages after the landing in night mode) and get light
// ink while the nav sits over them. On a reading page, a veil in the page's own colour keeps
// the links off the text, except over the post's dark header.
const onLight = ref(true)
const onPost = ref(false)          // any page but home: the veil, and HOME shows on phones
const overHead = ref(false)
let raf = 0
const under = (sel: string) => [...document.querySelectorAll(sel)].some((el) => {
  const r = el.getBoundingClientRect()
  return r.top < 30 && r.bottom > 30
})
function check() {
  raf = requestAnimationFrame(check)
  onLight.value = !under('[data-nav-dark]')
  overHead.value = under('[data-nav-head]')
  onPost.value = router.currentRoute.value.name !== 'home'
}
onMounted(() => { raf = requestAnimationFrame(check) })
onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<template>
  <nav class="nav mono" :class="{ light: onLight, veil: onPost && !overHead }">
    <a :href="BASE" class="logo" @click.prevent="toHome">{{ profile.handle.toUpperCase() }}<span>/ARCHIVE</span></a>
    <ul>
      <li class="home" :class="{ away: onPost }">
        <a :href="BASE" @click.prevent="toHome" v-magnetic="0.2"><span aria-hidden="true">[</span>Home<span aria-hidden="true">]</span></a>
      </li>
      <template v-for="[id, label] in items" :key="id">
        <NavMenu v-if="menus[id]" :label="label" :groups="menus[id]" :go="() => toSection(id)" />
        <li v-else>
          <a :href="`#${id}`" @click.prevent="toSection(id)" v-magnetic="0.2"><span aria-hidden="true">[</span>{{ label }}<span aria-hidden="true">]</span></a>
        </li>
      </template>
    </ul>
    <div class="tools">
      <button type="button" class="lang" :aria-label="lang === 'zh' ? 'Switch to English' : '切换到中文'" data-cursor="quiet"
              @click="switchFrom($event, () => (lang = lang === 'zh' ? 'en' : 'zh'))" v-magnetic="0.2">
        <span :class="{ on: lang === 'zh' }">中</span><i aria-hidden="true">/</i><span :class="{ on: lang === 'en' }">EN</span>
      </button>
      <button type="button" class="mode" :aria-pressed="theme === 'dark'" :aria-label="tr({ zh: '档案夜间模式', en: 'Night mode for the archive' })" data-cursor="quiet"
              @click="switchFrom($event, () => (theme = theme === 'dark' ? 'light' : 'dark'), true)" v-magnetic="0.2">
        <span aria-hidden="true">{{ theme === 'dark' ? '☾' : '☼' }}</span>{{ theme === 'dark' ? 'NIGHT' : 'DAY' }}
      </button>
    </div>
  </nav>
</template>

<style scoped>
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 50; display: flex; justify-content: space-between; align-items: center;
  padding: 22px var(--gutter); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--fog);
  transition: color 0.5s;
}
.nav.light { color: #3c4448; }
/* reading pages: a soft veil in the page colour so the links never sit on top of text */
.nav { --veil: 227, 230, 231; }
:root[data-theme='dark'] .nav { --veil: 16, 20, 23; }
.nav::before { content: ''; position: absolute; inset: 0 0 -24px; z-index: -1; pointer-events: none; opacity: 0; transition: opacity 0.4s;
  background: linear-gradient(rgb(var(--veil)) 55%, rgba(var(--veil), 0)); }
.nav.veil::before { opacity: 1; }
.logo { font-weight: 500; letter-spacing: 0.24em; }
.logo span { opacity: 0.5; }
ul { display: flex; gap: 22px; list-style: none; margin: 0 0 0 auto; padding: 0; }
.tools { display: flex; gap: 14px; margin-left: 26px; padding-left: 22px; border-left: 1px solid currentColor; border-left-color: rgba(127, 136, 140, 0.35); }
.tools button { display: inline-flex; align-items: center; gap: 6px; font: inherit; letter-spacing: inherit; color: inherit; cursor: pointer; }
.lang span { opacity: 0.45; transition: opacity 0.2s; }
.lang span.on { opacity: 1; }
.lang i { font-style: normal; opacity: 0.35; }
.mode span { font-size: 13px; }
a span { opacity: 0; transition: opacity 0.2s; margin: 0 2px; }
a:hover span { opacity: 0.7; }
/* phones: the sections are one swipe away, so only HOME stays, on pages other than home */
@media (max-width: 760px) {
  ul > :not(.home), .home:not(.away) { display: none; }
  .tools { margin-left: 16px; padding-left: 14px; }
}
</style>
