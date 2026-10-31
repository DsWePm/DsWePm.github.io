<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { asciiCut, type CutOptions } from '../composables/useAsciiCut'
import { theme } from '../composables/prefs'

// The landing cut: a full black screen pours away in columns. Each column's front is
// not a line but a band of character cells dissolving at random, the same decode the
// hero opens with: black cells turn into bright glyphs on black, then clear to the page,
// and a short trail of dark glyphs settles into the page behind. Played upwards ('up')
// the black rises back over the page, the fall run backwards, and calls onCovered once
// the screen is all black, so whatever is behind can swap unseen.
const canvas = ref<HTMLCanvasElement>()
const on = ref(false)
const lifting = ref(false)          // after a rise: the black cover fades off the stage
let liftTimer = 0
const CELL = 14
const RAMP = ' .·:-=+*≡#%@'           // sparse -> dense
const BAND = 9                        // rows of dissolving cells at a column's front
const TRAIL = 5                       // rows of dark glyphs settling behind it
const DURATION = 1.15                 // s, slowest column
const BLACK = '#020303'
let raf = 0

const hash = (x: number, y: number) => { const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s) }

function play({ dir = 'down', onCovered }: CutOptions = {}) {
  const c = canvas.value
  if (!c || matchMedia('(prefers-reduced-motion: reduce)').matches) { onCovered?.(); return }
  cancelAnimationFrame(raf); clearTimeout(liftTimer)
  on.value = true; lifting.value = false
  const dpr = Math.min(devicePixelRatio, 2)
  const w = innerWidth, h = innerHeight
  c.width = w * dpr; c.height = h * dpr
  const ctx = c.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.font = `500 ${CELL - 2}px "JetBrains Mono", ui-monospace, monospace`
  ctx.textBaseline = 'top'
  const rows = Math.ceil(h / CELL) + 1
  const glyphs = [...RAMP]
  const span = rows + BAND + TRAIL
  // each column has its own delay and speed; neighbours stay close so it reads as one sheet
  let drift = Math.random()
  const cols = Array.from({ length: Math.ceil(w / CELL) }, () => {
    drift = Math.min(1, Math.max(0, drift + (Math.random() - 0.5) * 0.35))
    return { delay: drift * 0.32 + Math.random() * 0.06, dur: 0.55 + Math.random() * 0.2 }
  })
  // the trail settles into the page underneath: dark ink on the day archive, light at night
  const ink = theme.value === 'dark' ? '190,198,201' : '42,50,54'
  const up = dir === 'up'
  const t0 = performance.now()

  const frame = (now: number) => {
    const t = (now - t0) / 1000
    const tick = Math.floor(t * 12)          // glyphs re-roll a dozen times a second
    ctx.clearRect(0, 0, w, h)
    let alive = false
    cols.forEach((col, i) => {
      let k = Math.min(1, Math.max(0, (t - col.delay) / col.dur))
      if (k < 1) alive = true
      if (up) k = 1 - k                      // the fall run backwards: fast from the bottom, easing to the top
      // the front: black below it, the page above; it accelerates like the fall it follows
      const front = k * k * span - TRAIL
      const x = i * CELL
      const solid = Math.max(0, Math.ceil(front + BAND / 2))
      ctx.fillStyle = BLACK
      if (solid < rows) ctx.fillRect(x, solid * CELL, CELL, h - solid * CELL)
      const top = Math.floor(front - BAND / 2 - TRAIL)
      for (let y = Math.max(0, top); y < Math.min(rows, solid); y++) {
        const p = (front + BAND / 2 - y) / BAND          // 0 at the black side of the band, 1 at the page side
        const r = hash(i, y)
        const g = (n: number) => glyphs[Math.max(1, Math.min(glyphs.length - 1, Math.round(n * (glyphs.length - 1))))]
        if (p >= 1) {
          // past the band: a thinning trail of dark glyphs settling into the page
          const f = 1 - (p - 1) * BAND / TRAIL
          if (f > 0 && r < f * 0.7) { ctx.fillStyle = `rgba(${ink},${(0.45 * f).toFixed(3)})`; ctx.fillText(g(f * 0.8), x + 1, y * CELL) }
          continue
        }
        // in the band each cell flips at its own threshold: black, then a glyph cell, then clear
        if (r > p * 1.25 + 0.12) { ctx.fillStyle = BLACK; ctx.fillRect(x, y * CELL, CELL, CELL); continue }
        if (r > p * 1.25 - 0.22) {
          ctx.fillStyle = `rgba(2,3,3,${(0.92 - p * 0.5).toFixed(3)})`
          ctx.fillRect(x, y * CELL, CELL, CELL)
          ctx.fillStyle = `rgba(232,236,236,${(0.95 - p * 0.35).toFixed(3)})`
          ctx.fillText(g((1 - p) * 0.85 + hash(i + tick, y) * 0.3), x + 1, y * CELL)
        }
      }
    })
    if (alive || t < DURATION) raf = requestAnimationFrame(frame)
    else if (up) {
      // all black now: let what's behind change, then fade the cover off it
      onCovered?.()
      ctx.fillStyle = BLACK; ctx.fillRect(0, 0, w, h)
      raf = requestAnimationFrame(() => { raf = requestAnimationFrame(() => {
        lifting.value = true
        liftTimer = window.setTimeout(() => { on.value = false; lifting.value = false; ctx.clearRect(0, 0, w, h) }, 340)
      }) })
    } else { on.value = false; ctx.clearRect(0, 0, w, h) }
  }
  // the first painted frame must already be right: black for a cut away, clear for a rise
  if (!up) { ctx.fillStyle = BLACK; ctx.fillRect(0, 0, w, h) }
  raf = requestAnimationFrame(frame)
}

asciiCut.play = play
onBeforeUnmount(() => { cancelAnimationFrame(raf); clearTimeout(liftTimer); asciiCut.play = () => {} })
</script>

<template>
  <canvas ref="canvas" class="ascii-cut" :class="{ on, lifting }" aria-hidden="true" />
</template>

<style scoped>
.ascii-cut { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 70; pointer-events: none; visibility: hidden; }
.ascii-cut.on { visibility: visible; }
.ascii-cut.lifting { opacity: 0; transition: opacity 0.32s var(--ease-io); }
</style>
