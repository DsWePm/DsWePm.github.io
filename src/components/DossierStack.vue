<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { dossiers } from '../data/profile'
import { art } from '../data/asciiArt'
import { scramble } from '../composables/scramble'
import { pathOf, postForDossier } from '../data/posts'
import { tr } from '../composables/prefs'

// Files stand side by side in a drawer, each showing only its spine; one is
// open. Up to five are in view at a time (a window over the row).
//  - Hover opens the file under the pointer in place; the window does not move,
//    and the file is resolved from the pointer's x against the *target* layout,
//    not from DOM hover on moving elements, so it never jitters at a boundary.
//  - The wheel (or a trackpad) steps the open file along and slides the window
//    so it sits as near the middle as the row allows; at either end of the row
//    the page scrolls on as usual.
// The window's outer two slots shrink and fade unless they hold the open file.
// Clicking anywhere on a file opens its write-up.
const BASE = import.meta.env.BASE_URL
const SPINE = 72
const VISIBLE = 5
const STEP = 100                 // wheel delta per file
const n = dossiers.length
const slots = Math.min(n, VISIBLE)
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))
const router = useRouter()
const drawer = ref<HTMLElement>()
const width = ref(1100)
const active = ref(Math.floor((n - 1) / 2))
const start = ref(windowFor(active.value))       // first file in view
const compact = ref(false)
const tilt = ref(0)
const plates = ref(dossiers.map((d) => art[d.art] ?? ''))
const timecode = ref('00:00:00')
let ro: ResizeObserver | undefined
let cancel = () => {}
let tcTimer = 0, wheelAcc = 0, lastStep = 0

const openW = computed(() => Math.max(360, width.value - (slots - 1) * SPINE))
function windowFor(i: number) { return clamp(i - Math.floor(slots / 2), 0, n - slots) }

const xOf = (i: number, a = active.value, s = start.value) => (i - s) * SPINE + (i > a ? openW.value - SPINE : 0)

/** per file: x, lift, scale, fade */
const layout = computed(() => dossiers.map((_, i) => {
  const k = i - start.value                      // slot in the window: 0 .. slots-1 when in view
  const edge = i === active.value ? 0 : clamp(Math.max(-k, k - (slots - 1)) + 1, 0, 2)   // 1 at the outer slots
  return {
    x: xOf(i), w: i === active.value ? openW.value : SPINE,
    lift: i === active.value ? -10 : 0,
    scale: 1 - 0.07 * Math.min(edge, 1),
    fade: clamp(1 - 0.45 * Math.min(edge, 1) - 0.55 * clamp(edge - 1, 0, 1), 0, 1),
  }
}))

function indexAt(px: number) {
  const a = active.value
  if (px >= xOf(a) && px < xOf(a) + openW.value) return a
  for (let i = start.value; i < start.value + slots; i++) if (px >= xOf(i) && px < xOf(i) + SPINE) return i
  return a
}
function select(i: number) { if (i !== active.value) active.value = clamp(i, 0, n - 1) }
/** wheel and keys: step the open file and re-centre the window on it */
function step(i: number) {
  select(i)
  start.value = windowFor(active.value)
}

watch(active, (i) => {
  cancel()
  cancel = scramble(art[dossiers[i].art] ?? '', (s) => (plates.value[i] = s), 1000)
})

function onWheel(e: WheelEvent) {
  if (compact.value) return
  const unit = e.deltaMode === 1 ? 40 : e.deltaMode === 2 ? 800 : 1
  const delta = (Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY) * unit
  // at either end the wheel goes back to scrolling the page
  if ((delta < 0 && active.value <= 0) || (delta > 0 && active.value >= n - 1)) { wheelAcc = 0; return }
  e.preventDefault(); e.stopPropagation()
  wheelAcc += delta
  const now = performance.now()
  if (Math.abs(wheelAcc) < STEP || now - lastStep < 110) return
  step(active.value + Math.sign(wheelAcc))
  wheelAcc = 0; lastStep = now
}
function onMove(e: PointerEvent) {
  if (compact.value) return
  const r = drawer.value!.getBoundingClientRect()
  tilt.value = ((e.clientY - r.top) / r.height - 0.5) * -3
  if (e.pointerType === 'mouse') select(indexAt(e.clientX - r.left))
}
/** a file with a write-up opens it; one without becomes the open file */
function open(i: number) {
  const p = postForDossier(dossiers[i].code)
  if (p) router.push(pathOf(p))
  else step(i)
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') { step(active.value + 1); e.preventDefault() }
  if (e.key === 'ArrowLeft') { step(active.value - 1); e.preventDefault() }
  if (e.key === 'Enter') open(active.value)
}

// only the open file's footage plays
const videoAt = (i: number) => drawer.value?.querySelector<HTMLVideoElement>(`video[data-i="${i}"]`) ?? null
watch([active, compact], async ([a]) => {
  await nextTick()
  drawer.value?.querySelectorAll<HTMLVideoElement>('video[data-i]').forEach((v) => {
    if (Number(v.dataset.i) === a || compact.value) v.play().catch(() => {})
    else v.pause()
  })
})

onMounted(() => {
  ro = new ResizeObserver(([entry]) => {
    // zero while the home page is cached off-document; keep the last real layout
    if (!entry.contentRect.width) return
    width.value = entry.contentRect.width
    compact.value = entry.contentRect.width < 760
  })
  ro.observe(drawer.value!)
  drawer.value!.addEventListener('wheel', onWheel, { passive: false })
  videoAt(active.value)?.play().catch(() => {})
  tcTimer = window.setInterval(() => {
    const v = videoAt(active.value)
    const s = v ? v.currentTime : performance.now() / 1000
    timecode.value = [s / 3600, (s / 60) % 60, s % 60].map((x) => String(Math.floor(x)).padStart(2, '0')).join(':')
  }, 250)
})
onBeforeUnmount(() => {
  ro?.disconnect(); cancel(); clearInterval(tcTimer)
  drawer.value?.removeEventListener('wheel', onWheel)
})

const fileOf = (code: string) => postForDossier(code)
const bar = (v: number) => '█'.repeat(Math.round(v * 12)) + '░'.repeat(12 - Math.round(v * 12))
</script>

<template>
  <div class="dossiers">
    <div
      ref="drawer" class="drawer" :class="{ compact }" tabindex="0" data-cursor="slide"
      aria-label="Skill files. Hover, scroll or use the arrow keys to browse, Enter to open."
      @pointermove="onMove" @keydown="onKey"
    >
      <div class="rail" :style="{ transform: `rotateX(${tilt}deg)` }">
        <article
          v-for="(d, i) in dossiers" :key="d.code"
          class="file" :class="{ open: active === i || compact }"
          :style="compact ? {} : {
            transform: `translate3d(${layout[i].x}px, ${layout[i].lift}px, 0) scale(${layout[i].scale})`,
            transformOrigin: `${layout[i].w / 2}px 60%`, opacity: layout[i].fade, width: `${openW}px`, zIndex: i,
          }"
          :data-cursor="fileOf(d.code) ? 'open' : 'slide'"
          @click="open(i)"
        >
          <header class="spine mono">
            <span class="no">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="vtitle">{{ d.code }} ── {{ tr(d.title) }}</span>
            <span class="clr">L{{ d.clearance.slice(1) }}</span>
            <span class="barcode" aria-hidden="true" />
          </header>

          <div class="body">
            <figure class="media" data-cursor="view">
              <video v-if="d.video" :data-i="i" :src="BASE + d.video" muted loop playsinline preload="metadata" />
              <pre v-else class="plate" aria-hidden="true">{{ plates[i] }}</pre>
              <div class="hud mono" aria-hidden="true">
                <span class="tl">{{ d.video ? '● REC' : '○ NO FOOTAGE' }}</span>
                <span class="tr">{{ d.code }}</span>
                <span class="bl">{{ active === i ? timecode : '--:--:--' }}</span>
                <span class="br">CAM {{ String(i + 1).padStart(2, '0') }}</span>
              </div>
            </figure>
            <div class="info">
              <p class="label">{{ d.code }} · clearance {{ d.clearance }}</p>
              <h3>{{ tr(d.title) }}</h3>
              <p class="summary">{{ tr(d.summary) }}</p>
              <ul class="skills mono">
                <li v-for="s in d.skills" :key="s.name">
                  <span class="name">{{ s.name }}</span>
                  <span class="bar" aria-hidden="true">{{ bar(s.level) }}</span>
                  <span class="pct">{{ Math.round(s.level * 100) }}</span>
                </li>
              </ul>
              <p class="tags mono"><span v-for="t in d.tags" :key="t">#{{ t }}</span></p>
              <p v-if="fileOf(d.code)" class="cue mono">
                <span>[ OPEN FILE ]</span><span class="arrow" aria-hidden="true">──▶</span><span class="code">{{ fileOf(d.code)!.code }}</span>
              </p>
            </div>
          </div>
        </article>
      </div>
    </div>
    <p class="hint mono" aria-hidden="true">◀ ▶ hover or scroll over the drawer to browse the files · click a file to open it · {{ String(active + 1).padStart(2, '0') }} / {{ String(n).padStart(2, '0') }}</p>
  </div>
</template>

<style scoped>
.drawer { position: relative; height: 460px; perspective: 1800px; outline: none; }
.rail { position: absolute; inset: 0; overflow: hidden; transform-style: preserve-3d; transition: transform 0.8s var(--ease-out); padding-top: 10px; }

.file {
  position: absolute; top: 10px; left: 0; height: 440px; display: flex;
  background: var(--sheet);
  border: 1px solid var(--line);
  box-shadow: -14px 0 28px var(--shade);
  transition: transform 0.75s var(--ease-out), opacity 0.5s, box-shadow 0.4s; cursor: pointer;
  will-change: transform, opacity;
}
.file.open { box-shadow: -20px 6px 40px var(--shade-open); }

.spine {
  flex: 0 0 72px; display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 16px 0;
  border-right: 1px dashed var(--line); background: var(--spine);
  font-size: 10px; letter-spacing: 0.2em; color: var(--fog);
  transition: background 0.4s, color 0.4s;
}
.no { font-size: 18px; letter-spacing: 0; color: var(--accent); }
.vtitle { writing-mode: vertical-rl; transform: rotate(180deg); text-transform: uppercase; white-space: nowrap; flex: 1; overflow: hidden; }
.clr { color: var(--fog-dim); }
.barcode { width: 22px; height: 54px; opacity: 0.45; background: repeating-linear-gradient(0deg, var(--fog) 0 1px, transparent 1px 3px, var(--fog) 3px 5px, transparent 5px 6px, var(--fog) 6px 7px, transparent 7px 10px); }

.body { flex: 1; min-width: 0; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 28px; padding: 28px 30px; opacity: 0; transform: translateX(-12px); transition: opacity 0.4s, transform 0.6s var(--ease-out); }
.file.open .body { opacity: 1; transform: none; transition-delay: 0.12s; }

.media { position: relative; margin: 0; aspect-ratio: 16 / 10; align-self: start; background: var(--media); border: 1px solid var(--line); overflow: hidden; }
.media video { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0.55) contrast(0.95) brightness(1.03); }
.media::after { content: ''; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.06) 0 1px, transparent 1px 3px); }
.plate { margin: 0; height: 100%; display: flex; align-items: center; justify-content: center; font: 10px/1.2 var(--font-mono); color: var(--fog); }
.hud span { position: absolute; font-size: 10px; letter-spacing: 0.14em; color: var(--hud-ink); }
.hud .tl { left: 10px; top: 8px; } .hud .tr { right: 10px; top: 8px; }
.hud .bl { left: 10px; bottom: 8px; } .hud .br { right: 10px; bottom: 8px; }
.media video ~ .hud span { color: rgba(236, 239, 240, 0.85); }

.info h3 { margin: 4px 0 12px; font: 300 30px/1.15 var(--font-sans); color: var(--mist); }
.summary { margin: 0 0 18px; color: var(--fog); }
.skills { list-style: none; margin: 0; padding: 0; font-size: 11px; color: var(--fog); }
.skills li { display: grid; grid-template-columns: minmax(0, 1fr) auto 28px; gap: 10px; line-height: 2.1; }
.skills .bar { color: var(--accent); letter-spacing: -0.5px; }
.skills .pct { color: var(--fog-dim); text-align: right; }
.tags { margin: 16px 0 0; font-size: 11px; color: var(--fog-dim); display: flex; gap: 12px; flex-wrap: wrap; }
.cue { display: inline-flex; gap: 10px; align-items: center; margin-top: 22px; padding: 9px 14px; border: 1px solid var(--accent-dim); font-size: 11px; letter-spacing: 0.16em; color: var(--accent); transition: color 0.25s, background 0.25s, border-color 0.25s; }
.file:hover .cue { color: var(--paper); background: var(--accent); border-color: var(--accent); }
.cue .arrow { transition: transform 0.4s var(--ease-out); }
.file:hover .cue .arrow { transform: translateX(4px); }
.cue .code { color: var(--fog-dim); }
.file:hover .cue .code { color: inherit; }
.hint { margin: 18px 0 0; font-size: 10px; letter-spacing: 0.16em; color: var(--fog-dim); }

/* narrow screens: a plain vertical list, every file open */
.drawer.compact { height: auto; perspective: none; }
.compact .rail { position: static; overflow: visible; transform: none !important; display: flex; flex-direction: column; gap: 16px; padding: 0; }
.compact .file { position: relative; top: 0; height: auto; flex-direction: column; width: auto; }
.compact .spine { flex-direction: row; flex-basis: auto; padding: 10px 16px; border-right: 0; border-bottom: 1px dashed var(--line); }
.compact .vtitle { writing-mode: horizontal-tb; transform: none; }
.compact .barcode { display: none; }
.compact .body { grid-template-columns: 1fr; padding: 18px; }
</style>
