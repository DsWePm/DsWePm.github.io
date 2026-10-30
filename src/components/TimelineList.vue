<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { years } from '../data/timeline'
import ScrambleText from './ScrambleText.vue'
import { tr } from '../composables/prefs'

// Entries grouped under a year rule; each lights up as it scrolls into view.
const root = ref<HTMLElement>()
const seen = ref<Record<string, boolean>>({})
let io: IntersectionObserver | undefined
const pad = (n: number) => String(n).padStart(2, '0')

onMounted(() => {
  io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) seen.value[(e.target as HTMLElement).dataset.k!] = true
  }, { threshold: 0.5 })
  root.value?.querySelectorAll('[data-k]').forEach((el) => io!.observe(el))
})
onBeforeUnmount(() => io?.disconnect())
</script>

<template>
  <div ref="root" class="timeline">
    <section v-for="y in years" :id="y.id" :key="y.year" class="year">
      <header class="yh mono" :data-k="y.id" :class="{ seen: seen[y.id] }">
        <span class="yr">{{ y.year }}</span>
        <span class="rule" aria-hidden="true" />
        <span class="count">{{ pad(y.items.length) }} {{ y.items.length === 1 ? 'ENTRY' : 'ENTRIES' }}</span>
      </header>
      <ol>
        <li v-for="(t, i) in y.items" :key="i" :data-k="`${y.id}-${i}`" :class="{ seen: seen[`${y.id}-${i}`] }">
          <div class="when mono">{{ t.when }}</div>
          <div class="node mono" aria-hidden="true">{{ seen[`${y.id}-${i}`] ? '◆' : '◇' }}</div>
          <div class="what">
            <span class="kind mono">[{{ t.kind.toUpperCase() }}]</span>
            <ScrambleText :text="tr(t.title)" as="h3" />
            <p class="where mono">{{ tr(t.where) }}</p>
            <p class="detail">{{ tr(t.detail) }}</p>
          </div>
        </li>
      </ol>
    </section>
  </div>
</template>

<style scoped>
.year { position: relative; scroll-margin-top: 90px; }
.yh { display: flex; align-items: baseline; gap: 16px; margin: 0 0 32px; opacity: 0.3; transform: translateY(10px); transition: opacity 0.8s, transform 0.8s var(--ease-out); }
.yh.seen { opacity: 1; transform: none; }
.yr { font: 300 44px/1 var(--font-sans); letter-spacing: -0.01em; color: var(--mist); width: 120px; text-align: right; padding-right: 20px; flex: 0 0 auto; }
.yh .rule { flex: 1; height: 1px; align-self: center; background: var(--line); }
.count { font-size: 10px; letter-spacing: 0.2em; color: var(--fog-dim); }
ol { list-style: none; margin: 0; padding: 0 0 24px; position: relative; }
ol::before { content: ''; position: absolute; left: 140px; top: 8px; bottom: 32px; width: 1px; background: repeating-linear-gradient(180deg, var(--line) 0 4px, transparent 4px 8px); }
li { display: grid; grid-template-columns: 120px 40px minmax(0, 1fr); gap: 0; padding: 0 0 48px; opacity: 0.25; transform: translateY(16px); transition: opacity 0.8s, transform 0.8s var(--ease-out); }
li.seen { opacity: 1; transform: none; }
.when { font-size: 12px; color: var(--fog-dim); padding-top: 4px; letter-spacing: 0.1em; text-align: right; padding-right: 20px; }
.node { color: var(--accent); text-align: center; position: relative; left: 1px; font-size: 13px; padding-top: 2px; }
.what { padding-left: 16px; }
.kind { font-size: 10px; letter-spacing: 0.2em; color: var(--accent); }
h3 { margin: 6px 0 4px; font: 400 22px/1.3 var(--font-sans); color: var(--mist); }
.where { margin: 0 0 10px; font-size: 11px; letter-spacing: 0.12em; color: var(--fog-dim); }
.detail { margin: 0; color: var(--fog); max-width: 60ch; }
@media (max-width: 640px) {
  .yr { width: auto; text-align: left; font-size: 34px; }
  ol::before { left: 8px; }
  li { grid-template-columns: 18px minmax(0, 1fr); }
  .when { grid-column: 2; text-align: left; padding: 0 0 4px 16px; }
  .node { grid-row: 1; grid-column: 1; }
  .what { grid-column: 2; }
}
</style>
