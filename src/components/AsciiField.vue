<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

// Sparse character rain behind the content. Glyphs near the pointer brighten
// and are pushed aside; frozen when reduced motion is requested.
const canvas = ref<HTMLCanvasElement>()
const CHARS = '01░▒│┤┐└┴┬├─┼┘┌:.·=+*#'
const CELL = 16
let raf = 0
let cols: { y: number; speed: number; len: number }[] = []
let mouse = { x: -999, y: -999 }
let last = 0

function resize() {
  const c = canvas.value!
  const dpr = Math.min(devicePixelRatio, 2)
  c.width = innerWidth * dpr; c.height = innerHeight * dpr
  c.getContext('2d')!.setTransform(dpr, 0, 0, dpr, 0, 0)
  const n = Math.ceil(innerWidth / CELL)
  cols = Array.from({ length: n }, () => ({ y: Math.random() * -innerHeight, speed: 20 + Math.random() * 60, len: 4 + ((Math.random() * 14) | 0) }))
}

function draw(t: number) {
  raf = requestAnimationFrame(draw)
  if (t - last < 33) return
  const dt = (t - last) / 1000
  last = t
  const ctx = canvas.value!.getContext('2d')!
  ctx.clearRect(0, 0, innerWidth, innerHeight)
  ctx.font = `12px "JetBrains Mono", monospace`
  ctx.textBaseline = 'top'
  cols.forEach((col, i) => {
    if (i % 3 !== 0) return            // keep it sparse
    col.y += col.speed * Math.min(dt, 0.1)
    if (col.y - col.len * CELL > innerHeight) { col.y = Math.random() * -200; col.speed = 20 + Math.random() * 60 }
    for (let k = 0; k < col.len; k++) {
      let x = i * CELL, y = Math.floor(col.y / CELL) * CELL - k * CELL
      if (y < -CELL || y > innerHeight) continue
      const dx = x - mouse.x, dy = y - mouse.y
      const d = Math.hypot(dx, dy)
      const near = Math.max(0, 1 - d / 120)
      x += (dx / (d || 1)) * near * 18
      const a = (1 - k / col.len) * 0.13 + near * 0.35
      ctx.fillStyle = near > 0.05 ? `rgba(77,106,112,${a})` : `rgba(80,90,95,${a * 0.8})`
      // head flickers, the tail keeps stable glyphs
      const ch = k === 0 ? CHARS[(Math.random() * CHARS.length) | 0] : CHARS[(i * 7 + (y / CELL) * 13) % CHARS.length | 0]
      ctx.fillText(ch, x, y)
    }
  })
}

const onMove = (e: PointerEvent) => { mouse = { x: e.clientX, y: e.clientY } }

onMounted(() => {
  resize()
  window.addEventListener('resize', resize)
  window.addEventListener('pointermove', onMove, { passive: true })
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { draw(1000); cancelAnimationFrame(raf) }
  else raf = requestAnimationFrame(draw)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', resize)
  window.removeEventListener('pointermove', onMove)
})
</script>

<template>
  <div class="ascii-wrap" aria-hidden="true"><canvas ref="canvas" class="ascii-field" /></div>
</template>

<style scoped>
/* spans only the content area; the canvas sticks to the viewport while it scrolls */
.ascii-wrap { position: absolute; inset: 0; pointer-events: none; z-index: 0; }
.ascii-field { position: sticky; top: 0; display: block; width: 100%; height: 100vh; }
</style>
