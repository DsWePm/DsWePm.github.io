<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { lenis } from '../composables/useLenis'

// The picture viewer for the articles: a dark HUD layer over the page, not a new tab.
// × (or Esc, or a click on the dark ground) closes it; the ◀ ▶ buttons, the arrow keys and a
// swipe move through the other figures of the same article. A figure that has to be shrunk to
// fit the screen can be shown at its real size (click it, or the 1:1 button) and panned.
interface Item { src: string; alt: string; label: string; cap: string }

const MAX_UP = 3      // small pictures (the car clips, the SVG diagrams) may be enlarged this much to fit
const PAD = 14        // breathing room around the picture, px

const open = ref(false)
const items = ref<Item[]>([])
const index = ref(0)
const zoomed = ref(false)
const loaded = ref(false)
const closing = ref(false)
const root = ref<HTMLElement>()
const stage = ref<HTMLElement>()
const photo = ref<HTMLImageElement>()
const closeBtn = ref<HTMLButtonElement>()
const nat = reactive({ w: 0, h: 0 })     // the picture's own size
const room = reactive({ w: 0, h: 0 })    // what the stage leaves for it
let opener: HTMLElement | null = null
let ro: ResizeObserver | null = null
let pageOverflow = ''
let closeTimer = 0

const cur = computed(() => items.value[index.value])
const fit = computed(() => (nat.w && room.w > 0 && room.h > 0 ? Math.min(room.w / nat.w, room.h / nat.h) : 1))
const canZoom = computed(() => zoomed.value || (loaded.value && fit.value < 0.98))
const scale = computed(() => (zoomed.value ? 1 : Math.min(fit.value, MAX_UP)))
const frame = computed(() => (nat.w ? { width: `${Math.round(nat.w * scale.value)}px`, height: `${Math.round(nat.h * scale.value)}px` } : {}))
const pad = (n: number) => String(n).padStart(2, '0')

function measure() {
  const el = stage.value
  if (!el) return
  room.w = Math.max(0, el.clientWidth - PAD * 2)
  room.h = Math.max(0, el.clientHeight - PAD * 2)
}
watch(stage, (el) => {
  ro?.disconnect()
  ro = null
  if (!el) return
  ro = new ResizeObserver(measure)
  ro.observe(el)
  measure()
})

function onLoad() {
  const im = photo.value
  if (!im) return
  nat.w = im.naturalWidth || im.width || 800
  nat.h = im.naturalHeight || im.height || 600
  loaded.value = true
}

// a new picture: forget the old size, and catch a cached one whose load event came early;
// the neighbours are fetched ahead so that paging through the figures is quick
watch(index, async () => {
  loaded.value = false
  zoomed.value = false
  nat.w = nat.h = 0
  await nextTick()
  if (photo.value?.complete && photo.value.naturalWidth) onLoad()
})
watch([index, open], () => {
  if (!open.value || items.value.length < 2) return
  if ((navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData) return
  for (const d of [1, -1]) new Image().src = items.value[(index.value + d + items.value.length) % items.value.length].src
})

function show(list: Item[], at: number, from?: HTMLElement | null) {
  if (!list.length) return
  clearTimeout(closeTimer)
  closing.value = false
  items.value = list
  index.value = Math.min(Math.max(at, 0), list.length - 1)
  zoomed.value = false
  loaded.value = false
  nat.w = nat.h = 0
  opener = from ?? (document.activeElement as HTMLElement | null)
  pageOverflow = document.documentElement.style.overflow
  document.documentElement.style.overflow = 'hidden'      // the page behind stays where it is
  lenis.value?.stop()
  document.addEventListener('keydown', onKey)
  open.value = true
  nextTick(() => closeBtn.value?.focus({ preventScroll: true }))
}

function release() {
  document.removeEventListener('keydown', onKey)
  document.documentElement.style.overflow = pageOverflow
  lenis.value?.start()
}

function close() {
  if (!open.value || closing.value) return
  closing.value = true                       // fades out and stops taking clicks at once
  release()
  opener?.focus({ preventScroll: true })
  opener = null
  closeTimer = window.setTimeout(() => { open.value = false; closing.value = false }, 220)
}

function go(step: number) {
  const n = items.value.length
  if (n > 1) index.value = (index.value + step + n) % n
}

function toggleZoom() {
  if (!canZoom.value) return
  zoomed.value = !zoomed.value
  if (!zoomed.value) return
  nextTick(() => {
    const el = stage.value
    if (!el) return
    el.scrollLeft = (el.scrollWidth - el.clientWidth) / 2
    el.scrollTop = (el.scrollHeight - el.clientHeight) / 2
  })
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') { e.preventDefault(); close() }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1) }
  else if (e.key === 'ArrowRight') { e.preventDefault(); go(1) }
  else if (e.key === 'Tab') {
    // keep the focus on the viewer's own buttons
    const els = [...(root.value?.querySelectorAll<HTMLButtonElement>('button') ?? [])]
    if (!els.length) return
    const i = els.indexOf(document.activeElement as HTMLButtonElement)
    const next = e.shiftKey ? (i <= 0 ? els.length - 1 : i - 1) : (i === els.length - 1 ? 0 : i + 1)
    e.preventDefault()
    els[next].focus()
  }
}

function onRootClick(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.lb-frame, button, .lb-cap, .lb-top')) close()
}

let tx = 0
let ty = 0
function touchStart(e: TouchEvent) {
  if (e.touches.length !== 1) return
  tx = e.touches[0].clientX
  ty = e.touches[0].clientY
}
function touchEnd(e: TouchEvent) {
  if (zoomed.value || !e.changedTouches.length) return
  const dx = e.changedTouches[0].clientX - tx
  const dy = e.changedTouches[0].clientY - ty
  if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(dx < 0 ? 1 : -1)
}

onBeforeUnmount(() => {
  clearTimeout(closeTimer)
  ro?.disconnect()
  if (open.value && !closing.value) release()
})

defineExpose({ show })
</script>

<template>
  <Teleport to="body">
      <div v-if="open && cur" ref="root" class="lb" :class="{ out: closing }" role="dialog" aria-modal="true" aria-label="Figure viewer" data-lenis-prevent @click="onRootClick">
        <div class="lb-top mono">
          <span class="cnt">{{ cur.label }}</span>
          <span class="pos">{{ pad(index + 1) }} / {{ pad(items.length) }}</span>
          <span class="rule" aria-hidden="true" />
          <button v-if="canZoom" type="button" class="lb-btn wide" :aria-pressed="zoomed" aria-label="Toggle actual size" @click="toggleZoom">
            <span class="bk" aria-hidden="true">┌</span>
            <span class="tx">{{ zoomed ? 'FIT' : '1:1' }}</span>
            <span class="bk br" aria-hidden="true">┘</span>
          </button>
          <button ref="closeBtn" type="button" class="lb-btn" aria-label="Close" @click="close">
            <span class="bk" aria-hidden="true">┌</span>
            <span class="x" aria-hidden="true">×</span>
            <span class="hint" aria-hidden="true">ESC</span>
            <span class="bk br" aria-hidden="true">┘</span>
          </button>
        </div>

        <div class="lb-mid">
          <button v-if="items.length > 1" type="button" class="lb-btn side prev" aria-label="Previous figure" @click="go(-1)">
            <span class="bk" aria-hidden="true">┌</span><span class="ar" aria-hidden="true">◀</span><span class="bk br" aria-hidden="true">┘</span>
          </button>

          <div ref="stage" class="lb-stage" :class="{ zoomed }" @touchstart.passive="touchStart" @touchend="touchEnd">
            <div class="lb-frame" :class="{ on: loaded }" :style="frame">
              <img :key="cur.src" ref="photo" :src="cur.src" :alt="cur.alt" draggable="false" data-cursor="view" @load="onLoad" @click="toggleZoom">
            </div>
          </div>

          <button v-if="items.length > 1" type="button" class="lb-btn side next" aria-label="Next figure" @click="go(1)">
            <span class="bk" aria-hidden="true">┌</span><span class="ar" aria-hidden="true">▶</span><span class="bk br" aria-hidden="true">┘</span>
          </button>
        </div>

        <p v-if="cur.cap" class="lb-cap mono">{{ cur.cap }}</p>
      </div>
  </Teleport>
</template>

<style scoped>
/* always the dark palette, whatever the page's theme: it lies over the page like the city at night */
.lb {
  position: fixed; inset: 0; z-index: 105;            /* over the nav, the scroll HUD and the grain; the cursor (110) stays on top */
  display: flex; flex-direction: column;
  background: rgba(9, 12, 14, 0.94); color: var(--mist);
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
  overscroll-behavior: contain; touch-action: none; user-select: none;
}
.lb::before { content: ''; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.025) 0 1px, transparent 1px 3px); }
.lb { animation: lb-in 0.25s ease; }
.lb.out { animation: lb-out 0.2s ease forwards; pointer-events: none; }
@keyframes lb-in { from { opacity: 0; } }
@keyframes lb-out { to { opacity: 0; } }

/* top line: which figure, and the controls */
.lb-top { position: relative; flex: 0 0 auto; display: flex; align-items: center; gap: 16px; padding: 16px var(--gutter) 10px; font-size: 11px; letter-spacing: 0.16em; }
.lb-top .cnt { color: var(--accent); }
.lb-top .pos { color: var(--fog); }
.lb-top .rule { flex: 1; height: 1px; background: repeating-linear-gradient(90deg, var(--line) 0 6px, transparent 6px 9px); }

/* the buttons: the bracketed HUD tabs of the back-to-top button */
.lb-btn {
  position: relative; flex: 0 0 auto; display: grid; justify-items: center; align-content: center; gap: 3px;
  min-width: 46px; min-height: 46px; padding: 8px 12px;
  background: rgba(16, 20, 23, 0.8); border: 1px solid #2b343a; color: #86a6ac;
  font: 500 10px/1 var(--font-mono); letter-spacing: 0.18em; cursor: pointer;
  transition: background 0.3s, color 0.3s, border-color 0.3s;
}
.lb-btn:hover, .lb-btn:focus-visible { background: #86a6ac; border-color: #86a6ac; color: #101417; outline: none; }
.lb-btn .bk { position: absolute; left: -5px; top: -6px; font-size: 12px; line-height: 1; color: #86a6ac; }
.lb-btn .bk.br { left: auto; top: auto; right: -5px; bottom: -6px; }
.lb-btn .x { font-size: 22px; line-height: 0.8; letter-spacing: 0; }
.lb-btn .hint { font-size: 8px; color: #6c767c; transition: color 0.3s; }
.lb-btn:hover .hint, .lb-btn:focus-visible .hint { color: #2b343a; }
.lb-btn .ar { font-size: 15px; line-height: 1; letter-spacing: 0; }
.lb-btn .tx { font-size: 11px; }
.lb-btn.wide { padding-inline: 16px; }

/* the picture, and the ◀ ▶ buttons at the two edges */
.lb-mid { position: relative; flex: 1; min-height: 0; display: flex; align-items: center; }
.lb-btn.side { z-index: 2; margin: 0 clamp(10px, 2.2vw, 28px); }
.lb-stage { flex: 1; min-width: 0; align-self: stretch; display: flex; padding: 14px; overflow: hidden; }
.lb-stage.zoomed { overflow: auto; touch-action: pan-x pan-y; overscroll-behavior: contain; scrollbar-width: thin; scrollbar-color: rgba(134, 166, 172, 0.45) transparent; }
.lb-frame {
  position: relative; flex: 0 0 auto; margin: auto; background: #fff; box-shadow: 0 30px 80px -30px rgba(0, 0, 0, 0.85);
  opacity: 0; transform: translateY(10px) scale(0.985); transition: opacity 0.28s, transform 0.5s var(--ease-out);
}
.lb-frame.on { opacity: 1; transform: none; }
.lb-frame::before, .lb-frame::after { content: ''; position: absolute; width: 14px; height: 14px; border: 1px solid var(--accent); pointer-events: none; }
.lb-frame::before { top: -5px; left: -5px; border-right: 0; border-bottom: 0; }
.lb-frame::after { bottom: -5px; right: -5px; border-left: 0; border-top: 0; }
.lb-frame img { display: block; width: 100%; height: 100%; -webkit-user-drag: none; }

/* the caption of the figure */
.lb-cap {
  position: relative; flex: 0 0 auto; width: min(1000px, 100%); max-height: 26vh; margin: 0 auto; overflow: auto; touch-action: pan-y;
  padding: 10px var(--gutter) 22px; font-size: 11px; line-height: 1.7; letter-spacing: 0.06em; color: var(--fog); user-select: text;
}

@media (max-width: 640px) {
  .lb-top { gap: 12px; padding: 12px 16px 8px; }
  .lb-btn { min-width: 42px; min-height: 42px; }
  /* on a narrow screen the ◀ ▶ sit in the empty band under the picture instead of over its edges */
  .lb-btn.side { position: absolute; bottom: 10px; margin: 0; min-width: 40px; min-height: 40px; padding: 6px 8px; background: rgba(16, 20, 23, 0.8); }
  .lb-btn.side.prev { left: 8px; }
  .lb-btn.side.next { right: 8px; }
  .lb-stage { padding: 10px 6px; }
  .lb-cap { max-height: 22vh; padding-bottom: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  .lb-frame { transform: none; transition: opacity 0.2s; }
}
</style>
