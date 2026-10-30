<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { asciiCut } from '../composables/useAsciiCut'
import { theme } from '../composables/prefs'

// The landing cut: a full black screen pours away in columns of characters.
// Each column's head is a bright glyph on black; behind it the archive is
// already there and a short trail of dark glyphs settles into the page.
const canvas = ref<HTMLCanvasElement>()
const on = ref(false)
const CELL = 14
const TRAIL = ' .·:-=+*≡#%@'          // sparse -> dense, densest right behind the head
const DURATION = 1.15                 // s, slowest column
let raf = 0

function play() {
  const c = canvas.value
  if (!c) return
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return
  cancelAnimationFrame(raf)
  on.value = true
  const dpr = Math.min(devicePixelRatio, 2)
  const w = innerWidth, h = innerHeight
  c.width = w * dpr; c.height = h * dpr
  const ctx = c.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.font = `500 ${CELL - 2}px "JetBrains Mono", ui-monospace, monospace`
  ctx.textBaseline = 'top'
  const rows = Math.ceil(h / CELL) + 1
  const glyphs = [...TRAIL]
  // each column falls with its own delay and speed; neighbours stay close so it reads as one sheet
  let drift = Math.random()
  const cols = Array.from({ length: Math.ceil(w / CELL) }, () => {
    drift = Math.min(1, Math.max(0, drift + (Math.random() - 0.5) * 0.35))
    return { delay: drift * 0.32 + Math.random() * 0.06, dur: 0.55 + Math.random() * 0.2, len: 6 + ((Math.random() * 10) | 0), seed: Math.random() * 1000 }
  })
  // the trail settles into the page underneath: dark ink on the day archive, light at night
  const trail = theme.value === 'dark' ? '190,198,201' : '42,50,54'
  const t0 = performance.now()
  const frame = (now: number) => {
    const t = (now - t0) / 1000
    ctx.clearRect(0, 0, w, h)
    let alive = false
    cols.forEach((col, i) => {
      const k = Math.min(1, Math.max(0, (t - col.delay) / col.dur))
      const head = (k * k) * (rows + col.len)          // accelerates, like the fall it follows
      if (k < 1) alive = true
      const x = i * CELL
      const hy = Math.floor(head)
      // still-black part below the head
      ctx.fillStyle = '#020303'
      ctx.fillRect(x, hy * CELL, CELL, h - hy * CELL)
      // bright head
      const flick = (n: number) => glyphs[1 + (((n * 7.13 + col.seed + Math.floor(t * 24)) | 0) % (glyphs.length - 1))]
      if (hy < rows) {
        ctx.fillStyle = 'rgba(232,236,236,0.95)'
        ctx.fillText(flick(hy), x + 1, hy * CELL)
      }
      // trail settling into the page: dense and dark near the head, thinning upward
      for (let j = 1; j <= col.len; j++) {
        const y = hy - j
        if (y < 0 || y >= rows) continue
        const f = 1 - j / (col.len + 1)
        ctx.fillStyle = `rgba(${trail},${(0.55 * f).toFixed(3)})`
        ctx.fillText(glyphs[Math.max(1, Math.round(f * (glyphs.length - 1)))], x + 1, y * CELL)
      }
    })
    if (alive || t < DURATION) raf = requestAnimationFrame(frame)
    else { on.value = false; ctx.clearRect(0, 0, w, h) }
  }
  // the first painted frame must already be black: draw it now, synchronously
  ctx.fillStyle = '#020303'; ctx.fillRect(0, 0, w, h)
  raf = requestAnimationFrame(frame)
}

asciiCut.play = play
onBeforeUnmount(() => { cancelAnimationFrame(raf); asciiCut.play = () => {} })
</script>

<template>
  <canvas ref="canvas" class="ascii-cut" :class="{ on }" aria-hidden="true" />
</template>

<style scoped>
.ascii-cut { position: fixed; inset: 0; width: 100vw; height: 100vh; z-index: 70; pointer-events: none; visibility: hidden; }
.ascii-cut.on { visibility: visible; }
</style>
