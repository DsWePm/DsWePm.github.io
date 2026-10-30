<script setup lang="ts">
import { ref } from 'vue'
import { profile } from '../data/profile'
import { tr } from '../composables/prefs'
import { useVisibleLoop } from '../composables/visibleLoop'

// "Subject portrait": an ASCII noise field that sharpens around the pointer.
const W = 34, H = 18
const RAMP = ' .·:-=+*#%@'
const portrait = ref('')
const root = ref<HTMLElement>()
let mx = -1, my = -1

function render(now: number) {
  const t = now / 1000
  let s = ''
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      // head-and-shoulders silhouette as a signed distance
      const nx = (x - W / 2) / (W / 2), ny = (y - H / 2) / (H / 2)
      const head = 1 - Math.hypot(nx * 2.1, (ny + 0.3) * 1.5)
      const body = 1 - Math.hypot(nx * 1.1, (ny - 1.25) * 1.6)
      let v = Math.max(head, body)
      const near = mx >= 0 ? Math.max(0, 1 - Math.hypot(x - mx, (y - my) * 2) / 9) : 0
      v += (Math.sin(x * 0.7 + t * 2) * Math.cos(y * 0.9 - t) * 0.18) * (1 - near)
      v = Math.max(0, Math.min(0.999, v * (0.8 + near * 0.6)))
      s += RAMP[Math.floor(v * RAMP.length)]
    }
    s += '\n'
  }
  portrait.value = s
}
function onMove(e: PointerEvent) {
  const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
  mx = ((e.clientX - r.left) / r.width) * W
  my = ((e.clientY - r.top) / r.height) * H
}
useVisibleLoop(root, render)
</script>

<template>
  <div ref="root" class="about">
    <figure class="portrait" data-cursor @pointermove="onMove" @pointerleave="mx = -1">
      <pre aria-hidden="true">{{ portrait }}</pre>
      <figcaption class="mono">
        <dl>
          <template v-for="[k, v] in profile.fields" :key="k"><dt>{{ k }}</dt><dd>{{ v }}</dd></template>
        </dl>
      </figcaption>
    </figure>
    <div class="text">
      <p v-for="(p, i) in tr(profile.about)" :key="i" :class="{ lead: i === 0 }">{{ p }}</p>
      <h3 class="label">research directions</h3>
      <ul class="research">
        <li v-for="(r, i) in tr(profile.research)" :key="r"><span class="mono">R-{{ String(i + 1).padStart(2, '0') }}</span>{{ r }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.about { display: grid; grid-template-columns: minmax(0, 420px) minmax(0, 1fr); gap: clamp(32px, 6vw, 96px); align-items: start; }
.portrait { margin: 0; border: 1px solid var(--line); background: var(--card); }
.portrait pre { margin: 0; padding: 20px; font: 12px/1.05 var(--font-mono); color: var(--fog); text-align: center; letter-spacing: 1px; }
figcaption { border-top: 1px dashed var(--line); padding: 14px 20px; font-size: 11px; letter-spacing: 0.14em; }
dl { margin: 0; display: grid; grid-template-columns: 90px 1fr; row-gap: 6px; }
dt { color: var(--fog-dim); }
dd { margin: 0; color: var(--mist); }
.text p { margin: 0 0 18px; color: var(--fog); max-width: 60ch; }
.text p.lead { font: 300 clamp(20px, 2.2vw, 28px)/1.45 var(--font-sans); color: var(--mist); }
.text .label { margin: 40px 0 14px; }
.research { list-style: none; padding: 0; margin: 0; border-top: 1px solid var(--line); }
.research li { display: flex; gap: 20px; padding: 14px 0; border-bottom: 1px solid var(--line); color: var(--mist); transition: padding 0.4s var(--ease-out), color 0.2s; }
.research li:hover { padding-left: 10px; color: var(--ground); }
.research span { font-size: 11px; color: var(--accent); padding-top: 3px; }
@media (max-width: 860px) { .about { grid-template-columns: 1fr; } }
</style>
