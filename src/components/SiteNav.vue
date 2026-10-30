<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { toHome, toSection } from '../composables/navigate'
import { router } from '../router'
import { profile } from '../data/profile'
import { categoriesIn, entries, type Collection } from '../data/posts'
import { years } from '../data/timeline'
import { filters } from '../composables/filters'
import NavMenu, { type MenuGroup } from './NavMenu.vue'

const BASE = import.meta.env.BASE_URL
const items = [['archive', 'Archive'], ['log', 'Log'], ['projects', 'Projects'], ['about', 'About'], ['timeline', 'Timeline'], ['contact', 'Contact']]

// Log and Projects drop their categories, Timeline its years
function show(c: Collection, cat: string) { filters[c] = cat; toSection(c) }
function entryGroups(c: Collection): MenuGroup[] {
  return [
    { key: 'all', label: 'All', count: entries[c].length, go: () => show(c, 'all') },
    ...categoriesIn(c).map((g) => ({ key: g.category.id, label: g.category.name, count: g.items.length, go: () => show(c, g.category.id) })),
  ]
}
const menus: Record<string, MenuGroup[]> = {
  log: entryGroups('log'),
  projects: entryGroups('projects'),
  timeline: years.map((y) => ({ key: y.id, label: String(y.year), count: y.items.length, go: () => toSection(y.id) })),
}
// the white slab and the paper-coloured pages take dark ink; dark bands (a post's header) mark
// themselves data-nav-dark and get light ink while the nav sits over them
const onLight = ref(true)
const onPost = ref(false)          // any page but home: the veil, and HOME shows on phones
let raf = 0
function check() {
  raf = requestAnimationFrame(check)
  let dark = false
  document.querySelectorAll('[data-nav-dark]').forEach((el) => {
    const r = el.getBoundingClientRect()
    if (r.top < 30 && r.bottom > 30) dark = true
  })
  onLight.value = !dark
  onPost.value = router.currentRoute.value.name !== 'home'
}
onMounted(() => { raf = requestAnimationFrame(check) })
onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<template>
  <nav class="nav mono" :class="{ light: onLight, veil: onPost && onLight }">
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
  </nav>
</template>

<style scoped>
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 50; display: flex; justify-content: space-between; align-items: center;
  padding: 22px var(--gutter); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--fog);
  transition: color 0.5s;
}
.nav.light { color: #3c4448; }
/* reading pages: a soft paper veil so the links never sit on top of text */
.nav::before { content: ''; position: absolute; inset: 0 0 -24px; z-index: -1; pointer-events: none; opacity: 0; transition: opacity 0.4s;
  background: linear-gradient(var(--paper) 55%, rgba(227, 230, 231, 0)); }
.nav.veil::before { opacity: 1; }
.logo { font-weight: 500; letter-spacing: 0.24em; }
.logo span { opacity: 0.5; }
ul { display: flex; gap: 22px; list-style: none; margin: 0; padding: 0; }
a span { opacity: 0; transition: opacity 0.2s; margin: 0 2px; }
a:hover span { opacity: 0.7; }
/* phones: the sections are one swipe away, so only HOME stays, on pages other than home */
@media (max-width: 760px) {
  ul > :not(.home), .home:not(.away) { display: none; }
}
</style>
