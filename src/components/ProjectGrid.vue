<script setup lang="ts">
import { computed } from 'vue'
import { entries, pathOf } from '../data/posts'
import { profile } from '../data/profile'
import { filters } from '../composables/filters'
import CategoryTabs from './CategoryTabs.vue'

// Projects: Markdown entries (src/content/projects) shown as cards that open the
// same detail page as the log. Stars and language come from repos.json when the
// entry's repo matches one.
const BASE = import.meta.env.BASE_URL
const shown = computed(() => entries.projects.filter((p) => filters.projects === 'all' || p.category.id === filters.projects))
const glyph = (lang?: string) => ({ TypeScript: '◆', JavaScript: '◇', Python: '●', 'C++': '■', Rust: '▲', Go: '▼' } as Record<string, string>)[lang ?? ''] ?? '○'
const src = (p: string) => (/^(https?:|\/)/.test(p) ? p : BASE + p)
</script>

<template>
  <CategoryTabs collection="projects" />
  <TransitionGroup name="card" tag="div" class="repos">
    <RouterLink v-for="p in shown" :key="p.slug" :to="pathOf(p)" class="repo" data-cursor="open" v-magnetic="0.06">
      <figure v-if="p.cover" class="cover"><img :src="src(p.cover)" alt="" loading="lazy"></figure>
      <header class="mono">
        <span>{{ p.code }} · {{ p.category.label }}</span>
        <span class="arrow" aria-hidden="true">──▶</span>
      </header>
      <h3>{{ p.title }}</h3>
      <p>{{ p.summary }}</p>
      <ul v-if="p.tags.length" class="topics mono"><li v-for="t in p.tags.slice(0, 4)" :key="t">{{ t }}</li></ul>
      <footer class="mono">
        <span v-if="p.status" class="status"><i aria-hidden="true">●</i> {{ p.status.toUpperCase() }}</span>
        <span v-if="p.language"><i aria-hidden="true">{{ glyph(p.language) }}</i> {{ p.language }}</span>
        <span v-if="p.stars !== undefined">★ {{ p.stars }}</span>
        <span class="date">{{ p.date }}</span>
      </footer>
      <span class="corner tl" aria-hidden="true">┌</span><span class="corner br" aria-hidden="true">┘</span>
    </RouterLink>
  </TransitionGroup>
  <p class="more mono">
    <a :href="`https://github.com/${profile.github}?tab=repositories`" target="_blank" rel="noopener">[ all repositories ── github.com/{{ profile.github }} ]</a>
  </p>
</template>

<style scoped>
.repos { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); border-top: 1px solid var(--line); border-left: 1px solid var(--line); }
.repo {
  position: relative; display: flex; flex-direction: column; gap: 10px; padding: 24px 24px 20px; min-height: 240px;
  background: var(--card); overflow: hidden;
  border-right: 1px solid var(--line); border-bottom: 1px solid var(--line);
  transition: background 0.35s;
}
.repo::before {
  content: ''; position: absolute; inset: 0; pointer-events: none; opacity: 0; transition: opacity 0.35s;
  background: repeating-linear-gradient(0deg, rgba(111, 138, 143, 0.05) 0 1px, transparent 1px 4px);
}
.repo:hover { background: var(--asphalt); }
.repo:hover::before { opacity: 1; }
.cover { margin: -24px -24px 8px; height: 150px; overflow: hidden; border-bottom: 1px solid var(--line); }
.cover img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0.5) contrast(0.95); transition: transform 1.2s var(--ease-out), filter 0.6s; }
.repo:hover .cover img { transform: scale(1.04); filter: saturate(0.8); }
header { display: flex; justify-content: space-between; font-size: 10px; letter-spacing: 0.18em; color: var(--fog-dim); }
.arrow { color: var(--accent-dim); transform: translateX(-8px); opacity: 0; transition: transform 0.4s var(--ease-out), opacity 0.3s; }
.repo:hover .arrow { transform: none; opacity: 1; color: var(--accent); }
h3 { margin: 8px 0 0; font: 400 20px/1.2 var(--font-sans); color: var(--mist); letter-spacing: 0.01em; }
p { margin: 0; color: var(--fog); font-size: 14px; flex: 1; }
.topics { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; padding: 0; margin: 0; }
.topics li { font-size: 10px; padding: 2px 8px; border: 1px solid var(--line); color: var(--fog-dim); }
footer { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 11px; color: var(--fog-dim); white-space: nowrap; }
footer i { font-style: normal; color: var(--accent); }
.status i { color: var(--sodium); }
.date { margin-left: auto; }
.corner { position: absolute; font: 14px var(--font-mono); color: var(--accent); opacity: 0; transition: opacity 0.3s, transform 0.4s var(--ease-out); }
.corner.tl { left: 6px; top: 2px; transform: translate(6px, 6px); }
.corner.br { right: 6px; bottom: 2px; transform: translate(-6px, -6px); }
.repo:hover .corner { opacity: 1; transform: none; }
.card-enter-from { opacity: 0; transform: translateY(10px); }
.card-enter-active { transition: opacity 0.4s, transform 0.5s var(--ease-out); }
.card-leave-active { display: none; }
.more { margin: 28px 0 0; font-size: 11px; letter-spacing: 0.12em; color: var(--fog-dim); }
.more a:hover { color: var(--mist); }
</style>
