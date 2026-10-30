<script setup lang="ts">
import { ref } from 'vue'
import { profile } from '../data/profile'
import { brandIcons } from '../data/brandIcons'
import ScrambleText from './ScrambleText.vue'
import { useVisibleLoop } from '../composables/visibleLoop'

const BARS = '▁▂▃▄▅▆▇'
const wave = ref('')
const copied = ref(false)
const root = ref<HTMLElement>()
let energy = 0.2

function tick(t: number) {
  energy += (0.2 - energy) * 0.06
  let s = ''
  for (let i = 0; i < 64; i++) {
    const v = (Math.sin(i * 0.35 + t * 0.003) * 0.5 + 0.5) * energy + Math.random() * energy * 0.6
    s += BARS[Math.min(BARS.length - 1, Math.floor(v * BARS.length))]
  }
  wave.value = s
}
async function copyEmail() {
  try { await navigator.clipboard.writeText(profile.email); copied.value = true; setTimeout(() => (copied.value = false), 1800) } catch { location.href = `mailto:${profile.email}` }
}
useVisibleLoop(root, tick)
</script>

<template>
  <div ref="root" class="contact" @pointermove="energy = Math.min(1, energy + 0.02)">
    <ScrambleText text="OPEN A CHANNEL" as="p" class="big" />
    <pre class="wave" aria-hidden="true">{{ wave }}</pre>
    <div class="row">
      <button v-if="profile.email" class="email mono" v-magnetic="0.25" @click="copyEmail">
        <span>{{ copied ? '✓ copied to clipboard' : profile.email }}</span><em>{{ copied ? '' : '[ copy ]' }}</em>
      </button>
      <ul class="links mono">
        <li v-for="l in profile.links" :key="l.label">
          <a :href="l.href" target="_blank" rel="noopener" v-magnetic="0.3" :style="l.icon ? { '--brand': brandIcons[l.icon]?.hex } : {}">
            <svg v-if="l.icon && brandIcons[l.icon]" class="ico" viewBox="0 0 24 24" aria-hidden="true"><path :d="brandIcons[l.icon].path" /></svg>
            <span>{{ l.label }}</span><i aria-hidden="true">↗</i>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.contact { padding: 24px 0 40px; }
.big { margin: 0; font: 300 clamp(40px, 8vw, 120px)/1 var(--font-sans); letter-spacing: 0.06em; color: var(--mist); }
.wave { margin: 24px 0 40px; font: 14px/1 var(--font-mono); color: var(--accent-dim); overflow: hidden; }
.row { display: flex; flex-wrap: wrap; gap: 32px; align-items: center; justify-content: space-between; }
.email { display: inline-flex; gap: 16px; align-items: baseline; padding: 18px 26px; border: 1px solid var(--line); font-size: 15px; color: var(--mist); transition: border-color 0.3s, background 0.3s; }
.email:hover { border-color: var(--accent-dim); background: var(--asphalt); }
.email em { font-style: normal; font-size: 11px; color: var(--fog-dim); letter-spacing: 0.14em; }
.links { display: flex; gap: 28px; list-style: none; padding: 0; margin: 0; font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; }
.links a { display: inline-flex; align-items: center; gap: 10px; color: var(--fog); padding: 8px 0; transition: color 0.3s; }
.links a i { font-style: normal; opacity: 0.6; }
.links a:hover { color: var(--mist); }
/* brand marks stay in the site's grey ink and take their own colour on hover */
.ico { width: 18px; height: 18px; fill: currentColor; transition: fill 0.3s, transform 0.4s var(--ease-out); }
.links a:hover .ico { fill: var(--brand, currentColor); transform: translateY(-1px); }
</style>
