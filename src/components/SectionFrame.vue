<script setup lang="ts">
import ScrambleText from './ScrambleText.vue'

defineProps<{ id: string; index: string; title: string; subtitle?: string }>()
</script>

<template>
  <section :id="id" class="frame" :data-hud-mark="title">
    <header class="head mono">
      <span class="idx">┌─[ {{ index }} ]─</span>
      <ScrambleText :text="title" as="h2" class="title" />
      <span class="rule" aria-hidden="true" />
      <span v-if="subtitle" class="sub">{{ subtitle }}</span>
      <span class="end" aria-hidden="true">─┐</span>
    </header>
    <div class="body"><slot /></div>
    <footer class="foot mono" aria-hidden="true"><span>└</span><span class="rule" /><span>┘</span></footer>
  </section>
</template>

<style scoped>
.frame { position: relative; z-index: 1; padding: clamp(80px, 14vh, 160px) var(--gutter) 0; max-width: 1360px; margin: 0 auto; }
.head { display: flex; align-items: baseline; gap: 12px; color: var(--fog-dim); font-size: 12px; letter-spacing: 0.16em; }
.idx, .end { color: var(--accent-dim); white-space: nowrap; }
.title { margin: 0; font: 500 13px/1 var(--font-mono); letter-spacing: 0.32em; color: var(--mist); white-space: nowrap; }
.sub { white-space: nowrap; font-family: var(--font-sans); letter-spacing: 0.1em; }
.rule { flex: 1; height: 1px; align-self: center; background: repeating-linear-gradient(90deg, var(--line) 0 6px, transparent 6px 9px); min-width: 24px; }
.body { padding: 48px 0 32px; }
.foot { display: flex; align-items: center; gap: 8px; color: var(--accent-dim); font-size: 12px; }
@media (max-width: 640px) { .sub { display: none; } }
</style>
