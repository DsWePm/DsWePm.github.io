<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

// HUD cursor. A centred SVG reticle morphs by what is under the pointer
// (data-cursor="link|button|slide|view|scan|text", or inferred from a/button/
// inputs). Brackets snap onto links, buttons and media; a short glitch plays on
// every change of state. Elements with v-magnetic still lean toward it.
type State = 'default' | 'link' | 'button' | 'slide' | 'view' | 'scan' | 'text'
const LABELS: Record<State, string> = { default: '', link: 'LINK ↗', button: 'EXEC', slide: '◀ SLIDE ▶', view: 'VIEW', scan: 'SCAN', text: 'READ' }
const LOCK: State[] = ['link', 'button', 'view']

const enabled = ref(false)
const state = ref<State>('default')
const glitch = ref(false)
const pos = reactive({ x: -100, y: -100 })
const box = reactive({ x: 0, y: 0, w: 34, h: 34, locked: false })
const trail = ref<{ id: number; x: number; y: number; ch: string }[]>([])
const TRAIL = '.·:+'
let target = { x: -100, y: -100 }
let lockEl: Element | null = null
let raf = 0, id = 0, last = 0, glitchTimer = 0

function onMove(e: PointerEvent) {
  target = { x: e.clientX, y: e.clientY }
  const now = performance.now()
  if (now - last > 50) {
    last = now
    trail.value.push({ id: id++, x: e.clientX, y: e.clientY, ch: TRAIL[(Math.random() * TRAIL.length) | 0] })
    if (trail.value.length > 18) trail.value.shift()
  }
}

function resolve(t: Element): [State, Element | null] {
  const el = t.closest('[data-cursor], a, button, input, textarea, select')
  if (!el) return ['default', null]
  const attr = (el as HTMLElement).dataset.cursor as State | undefined
  // a link or button inside a data-cursor region still wins
  const inner = t.closest('a, button')
  if (inner && el.contains(inner) && inner !== el) return [inner.tagName === 'A' ? 'link' : 'button', inner]
  if (attr && attr in LABELS) return [attr, el]
  if (el.tagName === 'A') return ['link', el]
  if (el.tagName === 'BUTTON') return ['button', el]
  return ['text', el]
}

function onOver(e: Event) {
  const [s, el] = resolve(e.target as Element)
  lockEl = LOCK.includes(s) ? el : null
  box.locked = !!lockEl
  if (s !== state.value) {
    state.value = s
    glitch.value = false
    requestAnimationFrame(() => { glitch.value = true })
    clearTimeout(glitchTimer)
    glitchTimer = window.setTimeout(() => (glitch.value = false), 220)
  }
}

function loop() {
  raf = requestAnimationFrame(loop)
  pos.x += (target.x - pos.x) * 0.38
  pos.y += (target.y - pos.y) * 0.38
  if (lockEl && lockEl.isConnected) {
    const r = lockEl.getBoundingClientRect()
    box.x = r.left - 6; box.y = r.top - 6; box.w = r.width + 12; box.h = r.height + 12
  } else {
    const s = state.value === 'slide' || state.value === 'scan' ? 46 : 34
    box.x = pos.x - s / 2; box.y = pos.y - s / 2; box.w = s; box.h = s
  }
}

onMounted(() => {
  enabled.value = matchMedia('(pointer: fine)').matches
  if (!enabled.value) return
  document.body.classList.add('has-hud-cursor')
  window.addEventListener('pointermove', onMove, { passive: true })
  document.addEventListener('pointerover', onOver)
  raf = requestAnimationFrame(loop)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  clearTimeout(glitchTimer)
  window.removeEventListener('pointermove', onMove)
  document.removeEventListener('pointerover', onOver)
  document.body.classList.remove('has-hud-cursor')
})
</script>

<template>
  <div v-if="enabled" class="hud-cursor mono" :class="[`s-${state}`, { glitch, locked: box.locked }]" aria-hidden="true">
    <span v-for="t in trail" :key="t.id" class="trail" :style="{ left: `${t.x}px`, top: `${t.y}px` }">{{ t.ch }}</span>

    <div class="box" :style="{ transform: `translate(${box.x}px, ${box.y}px)`, width: `${box.w}px`, height: `${box.h}px` }">
      <i class="c tl" /><i class="c tr" /><i class="c bl" /><i class="c br" />
      <span v-if="box.locked" class="tag">◢ {{ LABELS[state] }}</span>
    </div>

    <div class="reticle" :style="{ transform: `translate(${pos.x - 32}px, ${pos.y - 32}px)` }">
      <svg viewBox="0 0 64 64" width="64" height="64">
        <!-- default: symmetric crosshair with a gap and a centre dot -->
        <g class="g g-default">
          <line x1="32" y1="21" x2="32" y2="28" /><line x1="32" y1="36" x2="32" y2="43" />
          <line x1="21" y1="32" x2="28" y2="32" /><line x1="36" y1="32" x2="43" y2="32" />
          <circle cx="32" cy="32" r="1.3" class="fill" />
        </g>
        <g class="g g-link"><path d="M32 25 L39 32 L32 39 L25 32 Z" /><circle cx="32" cy="32" r="1.3" class="fill" /></g>
        <g class="g g-button"><rect x="26" y="26" width="12" height="12" /><rect x="30" y="30" width="4" height="4" class="fill" /></g>
        <g class="g g-slide">
          <path d="M22 26 L16 32 L22 38" /><path d="M42 26 L48 32 L42 38" />
          <line x1="27" y1="32" x2="37" y2="32" /><line x1="32" y1="29" x2="32" y2="35" />
        </g>
        <g class="g g-view"><path d="M28 25 L39 32 L28 39 Z" class="fill" /><circle cx="32" cy="32" r="11" class="thin" /></g>
        <g class="g g-scan">
          <circle cx="32" cy="32" r="14" class="dash" />
          <line x1="32" y1="14" x2="32" y2="18" /><line x1="32" y1="46" x2="32" y2="50" />
          <line x1="14" y1="32" x2="18" y2="32" /><line x1="46" y1="32" x2="50" y2="32" />
          <circle cx="32" cy="32" r="1.3" class="fill" />
        </g>
        <g class="g g-text"><line x1="32" y1="22" x2="32" y2="42" /><line x1="28" y1="22" x2="36" y2="22" /><line x1="28" y1="42" x2="36" y2="42" /></g>
      </svg>
    </div>

    <div class="readout" :style="{ transform: `translate(${pos.x + 24}px, ${pos.y + 16}px)` }">
      <span v-if="LABELS[state] && !box.locked" class="lbl">{{ LABELS[state] }}</span>
      <span>{{ String(Math.round(pos.x)).padStart(4, '0') }}·{{ String(Math.round(pos.y)).padStart(4, '0') }}</span>
    </div>
  </div>
</template>

<style scoped>
.hud-cursor { position: fixed; inset: 0; z-index: 95; pointer-events: none; color: #c6cbcd; mix-blend-mode: difference; }

.reticle { position: absolute; left: 0; top: 0; width: 64px; height: 64px; }
svg { display: block; overflow: visible; }
svg * { fill: none; stroke: currentColor; stroke-width: 1.4; vector-effect: non-scaling-stroke; }
svg .fill { fill: currentColor; stroke: none; }
svg .thin { stroke-width: 1; opacity: 0.6; }
svg .dash { stroke-dasharray: 6 4; transform-origin: 32px 32px; animation: spin 6s linear infinite; }
.g { opacity: 0; transform: scale(0.6) rotate(-45deg); transform-origin: 32px 32px; transition: opacity 0.18s, transform 0.35s var(--ease-out); }
.s-default .g-default, .s-link .g-link, .s-button .g-button, .s-slide .g-slide,
.s-view .g-view, .s-scan .g-scan, .s-text .g-text { opacity: 1; transform: none; }

/* glitch: a split, offset ghost for a fraction of a second on state change */
.glitch .reticle { animation: glitch 0.22s steps(3) 1; }
@keyframes glitch {
  0% { transform-origin: center; filter: drop-shadow(3px 0 0 #6f8a8f) drop-shadow(-3px 0 0 #9c8460); clip-path: inset(0 0 55% 0); }
  50% { filter: drop-shadow(-2px 0 0 #6f8a8f) drop-shadow(2px 0 0 #9c8460); clip-path: inset(40% 0 0 0); }
  100% { filter: none; clip-path: inset(0); }
}
@keyframes spin { to { transform: rotate(360deg); } }

.box { position: absolute; left: 0; top: 0; transition: width 0.3s var(--ease-out), height 0.3s var(--ease-out); }
.locked .box { transition: width 0.35s var(--ease-out), height 0.35s var(--ease-out), transform 0.35s var(--ease-out); }
.c { position: absolute; width: 8px; height: 8px; border: 0 solid currentColor; }
.tl { left: 0; top: 0; border-left-width: 1.5px; border-top-width: 1.5px; }
.tr { right: 0; top: 0; border-right-width: 1.5px; border-top-width: 1.5px; }
.bl { left: 0; bottom: 0; border-left-width: 1.5px; border-bottom-width: 1.5px; }
.br { right: 0; bottom: 0; border-right-width: 1.5px; border-bottom-width: 1.5px; }
.s-default .box, .s-text .box { opacity: 0.55; }
.locked .c { width: 12px; height: 12px; }
.tag { position: absolute; left: 0; top: -16px; font-size: 9px; letter-spacing: 0.16em; white-space: nowrap; }

.readout { position: absolute; left: 0; top: 0; display: flex; flex-direction: column; gap: 2px; font-size: 9px; letter-spacing: 0.12em; opacity: 0.75; white-space: nowrap; }
.lbl { letter-spacing: 0.2em; opacity: 1; }
.trail { position: absolute; font-size: 11px; transform: translate(-50%, -50%); animation: fade 0.9s linear forwards; }
@keyframes fade { from { opacity: 0.5; } to { opacity: 0; transform: translate(-50%, 10px); } }
</style>
