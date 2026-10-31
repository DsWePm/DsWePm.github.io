<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { loadStats as S } from '../composables/loadStats'

// Loading screen: a survey of the shaft you are about to fall down. Each floor of the
// canyon is built out of noise as the fall frames that reach it arrive, a probe drops
// down the gap to the deepest frame fetched so far, and the side panel reads out the
// real transfer: frames, data, rate, the last requests, and a map of every frame.
// When everything is in it locks, then the whole sheet falls away under the slab.
// The pointer (or a finger) reveals the shaft around it (floors not fetched yet show
// through the noise, built windows light up) and sends rings of characters out across
// it like ripples. Both only swap characters, so nothing on the page moves.
const props = defineProps<{ progress: number; done: boolean }>()

const FLOOR_H = 2.8
const WALL = 7, GAP = 7
// ASCII only inside the shaft: the web font carries no block or box glyphs, and the
// fallback font's are wider, which would break the columns
const NOISE = ' .:-=+'
const WIN = '.*'            // window: dark, lit
const BODY0 = 5, BODY = WALL * 2 + GAP     // the walls and gap start at column 5 of a row ("F07 [")
const ROW_LEN = BODY0 + BODY + 1
const ASPECT = 2.2                          // a row is about this many columns tall
const WAVE = '~=-'                          // ripple ring, strongest first
const now = ref(performance.now() / 1000)
const hover = ref<{ row: number; col: number } | null>(null)
const ripples: { row: number; col: number; t0: number }[] = []
const shaft = ref<HTMLElement>()
let raf = 0, last = 0

// a fixed facade per floor and side, so built floors hold still
const hash = (n: number) => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x) }
function facade(f: number, side: number) {
  let s = ''
  for (let i = 0; i < WALL; i++) {
    const h = hash(f * 31 + side * 7 + i)
    s += i < 2 ? '#%'[Math.floor(h * 2)] : h < 0.18 ? ' ' : h < 0.6 ? WIN[0] : h < 0.7 ? '|' : '='
  }
  return side ? [...s].reverse().join('') : s
}
const floors = computed(() => Math.round(S.maxDepth / FLOOR_H))
const facades = computed(() => Array.from({ length: floors.value + 1 }, (_, f) => [facade(f, 0), facade(f, 1)]))
// the probe goes down with the frames in hand (the first ~40 % are still above the slab)
const probe = computed(() => Math.min(floors.value, (S.reached / S.total) * (floors.value + 1)))
const alt = computed(() => ((S.alt >= 0 ? '+' : '−') + Math.abs(S.alt).toFixed(1)).padStart(5, ' '))   // fixed width: the header sets the column's width
const locked = computed(() => props.progress >= 1)

function noise(n: number, t: number, seed: number) {
  let s = ''
  for (let i = 0; i < n; i++) s += NOISE[Math.floor(hash(seed + i * 13 + Math.floor(t * 9 + hash(i + seed) * 3)) * NOISE.length)]
  return s
}
/** a lit window here and there, flickering slowly, once the floor is up */
function light(wall: string, f: number, side: number, t: number) {
  return wall.replace(/\./g, (m, i: number) => (hash(f * 17 + side * 5 + i + Math.floor(t * 0.7 + hash(f + i))) > 0.82 ? WIN[1] : m))
}
/** distance from the pointer in rows, columns scaled to match */
const dist = (f: number, col: number, p: { row: number; col: number }) => Math.hypot((col - p.col) / ASPECT, f - p.row)
const rows = computed(() => {
  const t = now.value
  const p = probe.value, pf = Math.floor(p)
  return facades.value.map(([l, r], f) => {
    let left: string, right: string, state: string
    if (f < pf || locked.value) { left = light(l, f, 0, t); right = light(r, f, 1, t); state = 'built' }
    else if (f === pf) {
      // the floor under construction resolves character by character
      const k = p - pf
      const mix = (w: string, seed: number) => [...w].map((c, i) => (hash(seed + i) < k ? c : noise(1, t, seed + i))).join('')
      left = mix(l, f * 3); right = mix(r, f * 3 + 1); state = 'building'
    } else { left = noise(WALL, t, f * 7); right = noise(WALL, t, f * 7 + 3); state = 'pending' }
    // the gap: rain down the built part of the shaft
    let gap = ''
    for (let i = 0; i < GAP; i++) {
      const drop = hash(i * 3.7 + Math.floor(t * 14 - f + hash(i) * 40)) > 0.93
      gap += (f < pf || locked.value) && drop ? (i % 2 ? '|' : ':') : ' '
    }
    const at = f === pf && !locked.value
    const plan = l + ' '.repeat(GAP) + r
    const body = [...(left + gap + right)].map((c, i) => {
      const col = BODY0 + i
      if (at && i === WALL + 3) return c                     // the probe's cell
      // ripples: a ring of wave characters, fading as it spreads
      for (const w of ripples) {
        const age = t - w.t0, k = 1 - age / 1.4
        if (k > 0 && Math.abs(dist(f, col, w) - age * 7) < 0.55) return WAVE[Math.min(2, Math.floor((1 - k) * 3))]
      }
      // the reveal: a soft-edged disc around the pointer (dithered edge, no flicker)
      const h = hover.value
      if (h) {
        const k = 1 - dist(f, col, h) / 2.4
        if (k > 0 && hash(f * 41 + i * 7) < k * 1.6) {
          if (state === 'built') return c === WIN[0] ? WIN[1] : c
          if (i < WALL || i >= WALL + GAP) return plan[i]
        }
      }
      return c
    }).join('')
    left = body.slice(0, WALL); gap = body.slice(WALL, WALL + GAP); right = body.slice(WALL + GAP)
    return { tag: `F${String(f).padStart(2, '0')}`, left, gap: at ? [gap.slice(0, 3), gap.slice(4)] : [gap, ''], right, state, at }
  })
})

const fmt = (n: number, d = 1) => n.toFixed(d)
const elapsed = computed(() => Math.max(0.001, now.value - S.start / 1000))
const rate = computed(() => S.bytes / 1048576 / elapsed.value)
const eta = computed(() => {
  if (!S.done || locked.value) return '00:00'
  const total = (S.bytes / S.done) * S.total, s = Math.max(0, (total - S.bytes) / 1048576 / Math.max(rate.value, 0.01))
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(Math.ceil(s % 60)).padStart(2, '0')}`
})
let lastRipple = 0
function onPointer(e: PointerEvent) {
  const pre = shaft.value
  if (!pre) return
  const r = pre.getBoundingClientRect()
  const p = { row: ((e.clientY - r.top) / r.height) * rows.value.length - 0.5, col: ((e.clientX - r.left) / r.width) * ROW_LEN }
  hover.value = p
  // a ring every so often while moving, one on every tap
  const t = performance.now() / 1000
  if (e.type === 'pointerdown' || t - lastRipple > 0.22) {
    lastRipple = t
    ripples.push({ ...p, t0: t })
    if (ripples.length > 6) ripples.shift()
  }
}

const pct = computed(() => String(Math.round(props.progress * 100)).padStart(3, '0'))
const status = computed(() => (locked.value ? 'SIGNAL LOCKED ▸ DESCEND' : S.done ? 'SURVEYING SHAFT' : 'MOUNTING SECTOR/07'))

function tick(t: number) {
  raf = requestAnimationFrame(tick)
  if (t - last < 33) return
  last = t
  now.value = t / 1000
  while (ripples.length && now.value - ripples[0].t0 > 1.4) ripples.shift()
}
onMounted(() => { raf = requestAnimationFrame(tick) })
onBeforeUnmount(() => cancelAnimationFrame(raf))
</script>

<template>
  <Transition name="loader">
    <div v-if="!done" class="loader" :class="{ locked }" role="status" :aria-label="`Loading ${pct}%`">
      <section class="shaft mono" aria-hidden="true" data-cursor="scan" @pointermove="onPointer" @pointerdown="onPointer" @pointerleave="hover = null">
        <p class="hd">┌─ SHAFT SURVEY // SECTOR 07 ─ Z {{ alt }}m</p>
        <!-- the probe sits in a one-character box so its wider fallback glyph keeps the columns -->
        <pre ref="shaft"><span v-for="r in rows" :key="r.tag" class="row" :class="[r.state, { at: r.at }]"><i>{{ r.tag }}</i> [{{ r.left }}<b>{{ r.gap[0] }}<u v-if="r.at" class="probe">▼</u>{{ r.gap[1] }}</b>{{ r.right }}]
</span></pre>
        <p class="hd">└─ FLOOR ─ {{ fmt(S.maxDepth) }}m</p>
      </section>

      <section class="meta mono">
        <div class="pct">{{ pct }}<span>%</span></div>
        <div class="bar"><span :style="{ transform: `scaleX(${progress})` }" /></div>
        <p class="status"><em class="blink">■</em> {{ status }}</p>
        <dl>
          <dt>FRAMES</dt><dd>{{ String(S.done).padStart(3, '0') }}/{{ S.total }}</dd>
          <dt>DATA</dt><dd>{{ fmt(S.bytes / 1048576) }} MB</dd>
          <dt>RATE</dt><dd>{{ fmt(rate) }} MB/s</dd>
          <dt>ETA</dt><dd>{{ eta }}</dd>
          <dt>ALT</dt><dd>{{ alt }} m</dd>
        </dl>
        <p class="map" aria-hidden="true">{{ S.map }}</p>
        <ul class="log" aria-hidden="true">
          <li v-for="(l, i) in S.log" :key="l" :style="{ opacity: 1 - i * 0.18 }">{{ l }}</li>
        </ul>
      </section>
    </div>
  </Transition>
</template>

<style scoped>
.loader {
  position: fixed; inset: 0; z-index: 100;
  display: flex; align-items: center; justify-content: center; gap: clamp(28px, 6vw, 104px);
  background: var(--paper); color: #505a5f;
  padding: var(--gutter);
}
/* the shaft */
.shaft { font-size: 12px; color: #7b858a; }
.shaft pre { margin: 0; font: inherit; line-height: 1.22; }
.hd { margin: 0; font-size: 10px; letter-spacing: 0.18em; color: #91a4a8; line-height: 2.2; white-space: pre; }
.row { transition: color 0.4s; }
.row i { font-style: normal; color: #a6b0b4; }
.row b { font-weight: inherit; color: #91a4a8; }
.row.pending { color: #c4cbce; }
.row.building { color: #4d6a70; }
.row.built { color: #505a5f; }
.row.at i { color: #4d6a70; }
.row.at b { color: var(--sodium); }
.shaft { touch-action: none; }
.probe { display: inline-block; width: 1ch; text-decoration: none; text-align: center; overflow: visible; font-size: 0.8em; line-height: 1; }
/* telemetry */
.meta { width: 268px; font-size: 11px; letter-spacing: 0.14em; }
.pct { font-size: 44px; color: #2a3236; letter-spacing: 0; font-variant-numeric: tabular-nums; }
.pct span { font-size: 14px; color: #7b858a; margin-left: 4px; }
.bar { height: 1px; background: #bec5c8; margin: 14px 0 12px; }
.bar span { display: block; height: 100%; background: var(--accent); transform-origin: left; transition: transform 0.3s; }
.status { margin: 0 0 14px; color: #4d6a70; font-size: 10px; letter-spacing: 0.2em; }
.status em { font-style: normal; font-size: 8px; margin-right: 6px; vertical-align: 1px; }
.blink { animation: blink 1s steps(2) infinite; }
.locked .status { color: #2a3236; }
.locked .blink { animation: none; color: var(--sodium); }
dl { display: grid; grid-template-columns: 70px 1fr; margin: 0 0 14px; line-height: 1.9; }
dt { color: #4d6a70; }
dd { margin: 0; color: #505a5f; font-variant-numeric: tabular-nums; }
.map { margin: 0 0 12px; font-size: 9px; line-height: 1.15; letter-spacing: 0; color: #91a4a8; word-break: break-all; line-break: anywhere; width: 41ch; max-width: 100%; }
.log { list-style: none; margin: 0; padding: 0; font-size: 9px; letter-spacing: 0.06em; color: #7b858a; line-height: 1.7; white-space: pre; overflow: hidden; }
@keyframes blink { 50% { opacity: 0; } }
/* out: once locked, the whole sheet drops away and the slab is under it */
.loader-leave-active { transition: transform 0.9s cubic-bezier(0.6, 0, 0.9, 0.35) 0.5s; }
.loader-leave-to { transform: translateY(104%); }
@media (max-width: 640px) {
  .loader { flex-direction: column; gap: 18px; }
  .shaft { font-size: 9px; }
  .meta { width: min(100%, 300px); }
  .pct { font-size: 34px; }
  dl { grid-template-columns: repeat(2, auto 1fr); column-gap: 10px; line-height: 1.7; }
  .log { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .loader-leave-active { transition: opacity 0.4s; }
  .loader-leave-to { transform: none; opacity: 0; }
}
</style>
