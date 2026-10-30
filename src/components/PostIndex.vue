<script setup lang="ts">
import { computed } from 'vue'
import { posts, pathOf } from '../data/posts'
import { filters } from '../composables/filters'
import ScrambleText from './ScrambleText.vue'
import CategoryTabs from './CategoryTabs.vue'

// The log: a file index, filtered by category. Hovering a row decodes its title again.
const kinds = { skill: 'SKILL FILE', note: 'FIELD NOTE', project: 'PROJECT' }
const shown = computed(() => posts.filter((p) => filters.log === 'all' || p.category.id === filters.log))
</script>

<template>
  <div class="index">
    <CategoryTabs collection="log" />
    <header class="cols mono" aria-hidden="true">
      <span>NO.</span><span>DATE</span><span>TITLE</span><span class="k">TYPE</span><span class="r">READ</span>
    </header>
    <TransitionGroup name="row" tag="div">
      <RouterLink v-for="p in shown" :key="p.slug" :to="pathOf(p)" class="row" data-cursor="open">
        <span class="no mono">{{ p.code }}</span>
        <span class="date mono">{{ p.date }}</span>
        <span class="main">
          <ScrambleText :text="p.title" trigger="hover" class="title" />
          <span class="sum">{{ p.summary }}</span>
        </span>
        <span class="k mono">{{ p.category.label }} · {{ kinds[p.kind] }}</span>
        <span class="r mono">{{ String(p.minutes).padStart(2, '0') }} MIN <span class="arrow" aria-hidden="true">──▶</span></span>
      </RouterLink>
    </TransitionGroup>
    <p v-if="!posts.length" class="empty mono">NO ENTRIES ── add Markdown files to src/content/log</p>
  </div>
</template>

<style scoped>
.cols, .row { display: grid; grid-template-columns: 88px 104px minmax(0, 1fr) 150px 112px; gap: 20px; align-items: baseline; }
.cols { padding: 0 0 12px; font-size: 10px; letter-spacing: 0.18em; color: var(--fog-dim); border-bottom: 1px solid var(--line); }
.row { position: relative; padding: 22px 0; border-bottom: 1px dashed var(--line); color: var(--fog); transition: color 0.3s, padding 0.5s var(--ease-out); }
.row::before { content: ''; position: absolute; inset: 0 auto 0 -12px; width: 2px; background: var(--accent); transform: scaleY(0); transition: transform 0.4s var(--ease-out); }
.row:hover { color: var(--mist); padding-left: 12px; }
.row:hover::before { transform: none; }
.row-enter-from, .row-leave-to { opacity: 0; transform: translateY(8px); }
.row-enter-active { transition: opacity 0.4s, transform 0.5s var(--ease-out); }
.row-leave-active { display: none; }
.no { font-size: 11px; color: var(--accent); letter-spacing: 0.08em; }
.date, .k, .r { font-size: 11px; letter-spacing: 0.08em; color: var(--fog-dim); }
.r { text-align: right; white-space: nowrap; }
.title { display: block; font: 300 22px/1.3 var(--font-sans); color: var(--mist); }
.sum { display: block; margin-top: 6px; font-size: 13px; line-height: 1.6; color: var(--fog); max-width: 62ch; }
.arrow { display: inline-block; margin-left: 6px; opacity: 0; transform: translateX(-8px); transition: opacity 0.3s, transform 0.4s var(--ease-out); color: var(--accent); }
.row:hover .arrow { opacity: 1; transform: none; }
.empty { font-size: 11px; color: var(--fog-dim); letter-spacing: 0.14em; padding: 24px 0; }
@media (max-width: 760px) {
  .cols { display: none; }
  .row { grid-template-columns: auto 1fr; gap: 6px 14px; }
  .main { grid-column: 1 / -1; }
  .k { display: none; }
}
</style>
