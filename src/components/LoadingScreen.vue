<script setup lang="ts">
import { computed } from 'vue'
import { loadingTower } from '../data/asciiArt'

const props = defineProps<{ progress: number; done: boolean }>()
const lines = loadingTower.split('\n').filter((l) => l.length)
const shown = computed(() => {
  // draw bottom-up, like the tower is being built
  const n = Math.round(props.progress * lines.length)
  return lines.map((l, i) => (i >= lines.length - n ? l : ''.padEnd(l.length, ' '))).join('\n')
})
const pct = computed(() => String(Math.round(props.progress * 100)).padStart(3, '0'))
const logs = computed(() => [
  ['MOUNT', 'sector/07'],
  ['LOAD', 'canyon.glb'],
  ['BAKE', 'walls_bake.jpg'],
  ['SYNC', 'feed // cam-07'],
  ['RAIN', '4.2 mm/h'],
].slice(0, 1 + Math.floor(props.progress * 4.99)))
</script>

<template>
  <Transition name="loader">
    <div v-if="!done" class="loader" role="status" :aria-label="`Loading ${pct}%`">
      <pre class="tower" aria-hidden="true">{{ shown }}</pre>
      <div class="meta mono">
        <div class="pct">{{ pct }}<span>%</span></div>
        <div class="bar"><span :style="{ transform: `scaleX(${progress})` }" /></div>
        <ul>
          <li v-for="[k, v] in logs" :key="k"><span>{{ k }}</span>{{ v }}</li>
        </ul>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.loader {
  position: fixed; inset: 0; z-index: 100;
  display: flex; align-items: center; justify-content: center; gap: clamp(24px, 6vw, 96px);
  background: var(--paper); color: #505a5f;
  padding: var(--gutter);
}
.tower { margin: 0; font: 12px/1.15 var(--font-mono); color: #7b858a; }
.meta { width: 220px; font-size: 11px; letter-spacing: 0.14em; }
.pct { font-size: 44px; font-weight: 400; color: #2a3236; letter-spacing: 0; }
.pct span { font-size: 14px; color: #7b858a; margin-left: 4px; }
.bar { height: 1px; background: #bec5c8; margin: 14px 0 18px; }
.bar span { display: block; height: 100%; background: var(--accent); transform-origin: left; transition: transform 0.3s; }
ul { list-style: none; margin: 0; padding: 0; }
li { color: #7b858a; line-height: 2; }
li span { display: inline-block; width: 64px; color: #4d6a70; }
.loader-leave-active { transition: opacity 0.9s var(--ease-io) 0.2s; }
.loader-leave-to { opacity: 0; }
@media (max-width: 640px) { .loader { flex-direction: column; } .tower { font-size: 9px; } }
</style>
