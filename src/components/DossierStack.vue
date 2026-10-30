<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { dossiers } from '../data/profile'
import { art } from '../data/asciiArt'
import { scramble } from '../composables/scramble'
import { pathOf, postForDossier } from '../data/posts'

// Files stand side by side in a drawer, each showing only its spine, with the
// open one in the middle. Scrolling the wheel (or a trackpad) over the drawer
// rolls the files sideways; at either end the page scrolls on as usual. Up to
// five are in view; the outer two shrink and fade so the open one holds focus.
// Clicking anywhere on a file opens its write-up.
const BASE = import.meta.env.BASE_URL
const SPINE = 72
const VISIBLE = 5
const n = dossiers.length
const router = useRouter()
const drawer = ref<HTMLElement>()
const width = ref(1100)
const target = ref(Math.floor((n - 1) / 2))     // start in the middle so both sides are filled
const pos = ref(target.value)                    // shown position, eased towards target
const active = computed(() => Math.round(pos.value))
const compact = ref(false)
const tilt = ref(0)
const plates = ref(dossiers.map((d) => art[d.art] ?? ''))
const timecode = ref('00:00:00')
let ro: ResizeObserver | undefined
let cancel = () => {}
let tcTimer = 0, raf = 0, snapTimer = 0, last = 0

const openW = computed(() => Math.max(360, width.value - (Math.min(n, VISIBLE) - 1) * SPINE))
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v))

/** per file: x, lift, scale, fade; the open width eases between neighbours as pos moves */
const layout = computed(() => {
  const p = pos.value
  const w = dossiers.map((_, i) => SPINE + clamp(1 - Math.abs(i - p), 0, 1) * (openW.value - SPINE))
  const x: number[] = []
  w.reduce((acc, wi, i) => ((x[i] = acc), acc + wi), 0)
  const k = clamp(Math.floor(p), 0, n - 1), f = p - k
  const mid = (i: number) => x[i] + w[i] / 2
  const c = k + 1 < n ? mid(k) + (mid(k + 1) - mid(k)) * f : mid(k)
  const off = width.value / 2 - c
  return dossiers.map((_, i) => {
    const d = Math.abs(i - p)
    const edge = clamp(d - 1, 0, 1.5)              // 0 next to the open file, 1 at the outer slots
    return {
      x: x[i] + off, w: w[i],
      lift: -10 * clamp(1 - d, 0, 1),
      scale: 1 - 0.07 * edge,
      fade: clamp(1 - 0.45 * edge - 1.2 * clamp(d - 2, 0, 1), 0, 1),
    }
  })
})

function ease(t: number) {
  const dt = Math.min(0.05, (t - last) / 1000 || 0.016)
  last = t
  pos.value += (target.value - pos.value) * (1 - Math.exp(-dt * 11))
  if (Math.abs(target.value - pos.value) < 0.001) { pos.value = target.value; raf = 0; return }
  raf = requestAnimationFrame(ease)
}
function goTo(t: number) {
  target.value = clamp(t, 0, n - 1)
  if (!raf) { last = performance.now(); raf = requestAnimationFrame(ease) }
}

watch(active, (i) => {
  cancel()
  cancel = scramble(art[dossiers[i].art] ?? '', (s) => (plates.value[i] = s), 1000)
})

function onWheel(e: WheelEvent) {
  if (compact.value) return
  const unit = e.deltaMode === 1 ? 40 : e.deltaMode === 2 ? 800 : 1
  const delta = (Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY) * unit
  const next = target.value + delta / 110
  // at either end the wheel goes back to scrolling the page
  if ((next < 0 && target.value <= 0) || (next > n - 1 && target.value >= n - 1)) return
  e.preventDefault(); e.stopPropagation()
  goTo(next)
  clearTimeout(snapTimer)
  snapTimer = window.setTimeout(() => goTo(Math.round(target.value)), 140)
}
function onMove(e: PointerEvent) {
  if (compact.value) return
  const r = drawer.value!.getBoundingClientRect()
  tilt.value = ((e.clientY - r.top) / r.height - 0.5) * -3
}
/** a file with a write-up opens it; one without rolls to the middle */
function open(i: number) {
  const p = postForDossier(dossiers[i].code)
  if (p) router.push(pathOf(p))
  else goTo(i)
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') { goTo(Math.round(target.value) + 1); e.preventDefault() }
  if (e.key === 'ArrowLeft') { goTo(Math.round(target.value) - 1); e.preventDefault() }
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
  ro?.disconnect(); cancel(); clearInterval(tcTimer); clearTimeout(snapTimer); cancelAnimationFrame(raf)
  drawer.value?.removeEventListener('wheel', onWheel)
})

const fileOf = (code: string) => postForDossier(code)
const bar = (v: number) => '█'.repeat(Math.round(v * 12)) + '░'.repeat(12 - Math.round(v * 12))
</script>

<template>
  <div class="dossiers">
    <div
      ref="drawer" class="drawer" :class="{ compact }" tabindex="0" data-cursor="slide"
      aria-label="Skill files. Scroll or use the arrow keys to browse, Enter to open."
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
            <span class="vtitle">{{ d.code }} ── {{ d.title }}</span>
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
              <h3>{{ d.title }}</h3>
              <p class="summary">{{ d.summary }}</p>
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
    <p class="hint mono" aria-hidden="true">◀ ▶ scroll over the drawer to roll the files · click a file to open it · {{ String(active + 1).padStart(2, '0') }} / {{ String(n).padStart(2, '0') }}</p>
  </div>
</template>

<style scoped>
.drawer { position: relative; height: 460px; perspective: 1800px; outline: none; }
.rail { position: absolute; inset: 0; overflow: hidden; transform-style: preserve-3d; transition: transform 0.8s var(--ease-out); padding-top: 10px; }

.file {
  position: absolute; top: 10px; left: 0; height: 440px; display: flex;
  background: linear-gradient(90deg, #f1f3f3, #e9eced 60%, #e4e8e9);
  border: 1px solid var(--line);
  box-shadow: -14px 0 28px rgba(30, 40, 46, 0.10);
  transition: box-shadow 0.4s; cursor: pointer;
  will-change: transform, opacity;
}
.file.open { box-shadow: -20px 6px 40px rgba(30, 40, 46, 0.16); }

.spine {
  flex: 0 0 72px; display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 16px 0;
  border-right: 1px dashed var(--line); background: rgba(205, 211, 213, 0.45);
  font-size: 10px; letter-spacing: 0.2em; color: var(--fog);
  transition: background 0.4s, color 0.4s;
}
.no { font-size: 18px; letter-spacing: 0; color: var(--accent); }
.vtitle { writing-mode: vertical-rl; transform: rotate(180deg); text-transform: uppercase; white-space: nowrap; flex: 1; overflow: hidden; }
.clr { color: var(--fog-dim); }
.barcode { width: 22px; height: 54px; opacity: 0.45; background: repeating-linear-gradient(0deg, var(--fog) 0 1px, transparent 1px 3px, var(--fog) 3px 5px, transparent 5px 6px, var(--fog) 6px 7px, transparent 7px 10px); }

.body { flex: 1; min-width: 0; display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 28px; padding: 28px 30px; opacity: 0; transform: translateX(-12px); transition: opacity 0.4s, transform 0.6s var(--ease-out); }
.file.open .body { opacity: 1; transform: none; transition-delay: 0.12s; }

.media { position: relative; margin: 0; aspect-ratio: 16 / 10; align-self: start; background: #cfd5d7; border: 1px solid var(--line); overflow: hidden; }
.media video { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0.55) contrast(0.95) brightness(1.03); }
.media::after { content: ''; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.06) 0 1px, transparent 1px 3px); }
.plate { margin: 0; height: 100%; display: flex; align-items: center; justify-content: center; font: 10px/1.2 var(--font-mono); color: var(--fog); }
.hud span { position: absolute; font-size: 10px; letter-spacing: 0.14em; color: rgba(42, 50, 54, 0.75); }
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
