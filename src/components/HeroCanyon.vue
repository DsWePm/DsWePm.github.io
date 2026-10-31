<script setup lang="ts">
import { computed, onActivated, onBeforeUnmount, onDeactivated, onMounted, reactive, ref } from 'vue'
import ScrambleText from './ScrambleText.vue'
import { profile } from '../data/profile'
import { lenis } from '../composables/useLenis'
import { asciiCut } from '../composables/useAsciiCut'
import { startTilt } from '../composables/useTilt'
import type { HeroStill } from '../hero/HeroStill'
import { tr } from '../composables/prefs'

// Hero: an interactive Cycles still on top of a short scroll track. Scrolling
// scrubs the pre-rendered free fall frame by frame (and back up). The track
// overlaps the archive, which waits under the stage: the floor of the shaft is
// a hole in the frames, kept black until impact. Reaching the last frame (top
// speed) plays the landing on its own: the black screen pours away as columns
// of characters with the archive behind them (AsciiCut.vue).
const emit = defineEmits<{ progress: [number]; ready: [] }>()

const BASE = import.meta.env.BASE_URL
const FLOOR_H = 2.8
const WHEEL_BOOST = 1.7          // wheel travels further in the shaft, so a couple of flicks drop you
const SLACK_UP = 0.3             // screens of upward scroll after landing that spring back to the archive

type State = 'idle' | 'landed'
const state = ref<State>('idle')
const section = ref<HTMLElement>()
const canvas = ref<HTMLCanvasElement>()
const fallback = ref(false)
const scroll = ref(0)
const depth = ref(62.1)
const hud = reactive({ x: 0, y: 0, depth: 0, overSlab: true, clock: '' })
let scene: HeroStill | null = null
let raf = 0, hudTimer = 0
let stopTilt = () => {}

const floors = computed(() => Math.round(depth.value / FLOOR_H))
const floor = computed(() => Math.min(floors.value, Math.max(0, Math.ceil((hud.depth - 0.5) / FLOOR_H))))
const gaugeTicks = computed(() => Array.from({ length: floors.value + 1 }, (_, i) => i))
const chrome = computed(() => Math.max(0, 1 - scroll.value * 8))       // title & cue fade as the fall starts
const falling = computed(() => scroll.value > 0.02 && state.value === 'idle')

function supportsWebGL() {
  try { return !!document.createElement('canvas').getContext('webgl2') } catch { return false }
}

function onPointer(e: PointerEvent) {
  hud.x = e.clientX; hud.y = e.clientY
  scene?.setPointer(e.clientX, e.clientY, scroll.value < 0.02)
  if (scene) hud.overSlab = scene.overSlab
}

/** impact: the frame is all black floor by now; the ASCII cut takes it from here */
function impact() {
  if (state.value !== 'idle') return
  state.value = 'landed'
  asciiCut.play()
}

const WHEEL = 0.9                // useLenis default
/** Lenis copies wheelMultiplier into its wheel listener, so set it there */
function setWheel(k: number) {
  const vs = (lenis.value as unknown as { virtualScroll?: unknown } | null)?.virtualScroll as { options: { wheelMultiplier: number } } | undefined
  if (vs) vs.options.wheelMultiplier = WHEEL * k
}

function frame() {
  raf = requestAnimationFrame(frame)
  const el = section.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const track = r.height - innerHeight              // where the stage unsticks, the archive's top is at the top
  scroll.value = track > 0 ? Math.min(1, Math.max(0, -r.top / track)) : 0
  setWheel(state.value === 'idle' && r.top > -track ? WHEEL_BOOST : 1)
  // the floor stops you: momentum that would carry past the shaft eases out at the archive's top
  const l = lenis.value, land = r.top + scrollY + track
  if (l && state.value === 'idle' && scrollY < land - 1 && l.targetScroll > land + 3) l.scrollTo(land + 2, { lerp: 0.085 })
  if (scene) {
    scene.setActive(state.value === 'idle' && r.bottom > 0)
    scene.setProgress(scroll.value / 0.97)          // the floor is reached a few px before the archive's top
    hud.depth = scene.depthAt(scene.progressFrame)
  }
  // after landing, a small pull upwards springs back to the archive; only a deliberate one
  // (past the slack) goes back up the shaft: the black rises over the archive (the landing
  // cut backwards), and once the screen is all black the stage returns and the impact re-arms
  if (state.value === 'landed' && !rising) {
    if (scrollY < land - innerHeight * SLACK_UP) {
      rising = true
      // (if the scroll came back down meanwhile, stay landed: the cover just lifts off the archive)
      asciiCut.play({ dir: 'up', onCovered: () => { rising = false; if (scrollY < land - innerHeight * SLACK_UP * 0.5) state.value = 'idle' } })
    } else if (l && scrollY < land - 1 && !l.isScrolling && performance.now() - lastInput > 220) l.scrollTo(land, { duration: 0.7 })
  }
}
let lastInput = 0, rising = false
const markInput = () => { lastInput = performance.now() }

onMounted(async () => {
  fallback.value = !supportsWebGL()
  addEventListener('pointermove', onPointer, { passive: true })
  for (const ev of ['wheel', 'touchmove', 'keydown']) addEventListener(ev, markInput, { passive: true })
  raf = requestAnimationFrame(frame)
  hudTimer = window.setInterval(() => { hud.clock = new Date().toTimeString().slice(0, 8) }, 500)
  if (fallback.value) { emit('progress', 1); emit('ready'); return }

  const { HeroStill } = await import('../hero/HeroStill')
  scene = new HeroStill(canvas.value!)
  scene.onImpact = impact
  new ResizeObserver(([e]) => { if (e.contentRect.width) scene?.resize() }).observe(canvas.value!)   // 0 while cached off-document
  try {
    await scene.load((p) => emit('progress', p))
    depth.value = scene.meta.depth
  } catch (err) {
    console.error('hero failed to load, using the plain still', err)
    scene.dispose(); scene = null; fallback.value = true
  }
  emit('progress', 1)
  scene?.start()
  stopTilt = startTilt((x, y) => scene?.setTilt(x, y))
  emit('ready')
  setTimeout(() => scene?.beginIntro(), 500)
})

// cached while a post is open: stop driving the stage and the scroll
onDeactivated(() => {
  cancelAnimationFrame(raf); raf = 0
  setWheel(1)
  scene?.setActive(false)
})
onActivated(() => { if (!raf) raf = requestAnimationFrame(frame) })

onBeforeUnmount(() => {
  cancelAnimationFrame(raf); clearInterval(hudTimer)
  setWheel(1)
  removeEventListener('pointermove', onPointer)
  for (const ev of ['wheel', 'touchmove', 'keydown']) removeEventListener(ev, markInput)
  stopTilt()
  scene?.dispose()
})
</script>

<template>
  <section ref="section" class="hero" :class="{ falling, landed: state === 'landed', plain: fallback }" aria-label="Intro">
    <div class="stage" data-cursor="scan">
      <div class="shade" />
      <canvas v-show="!fallback" ref="canvas" class="gl" />
      <img v-if="fallback" class="still" :src="`${BASE}hero/slab.jpg`" alt="" />

      <div class="title" :style="{ opacity: chrome }">
        <p class="label">░ subject file // 0x7A1 · {{ profile.location }}</p>
        <h1><ScrambleText :text="profile.name.toUpperCase()" trigger="mount" :delay="900" :duration="1400" /></h1>
        <p class="role">{{ tr(profile.role) }} — <span>{{ tr(profile.tagline) }}</span></p>
      </div>

      <div class="gauge mono" aria-hidden="true">
        <div class="gauge-head">DEPTH</div>
        <div class="gauge-track">
          <div v-for="i in gaugeTicks" :key="i" class="tick" :class="{ on: i === floor }">
            <span>{{ i % 2 === 0 ? '─┼─' : ' ┼ ' }}</span><em>F{{ String(i).padStart(2, '0') }}</em>
          </div>
          <div class="needle" :style="{ top: `${(hud.depth / depth) * 100}%` }">◀ {{ hud.depth.toFixed(1).padStart(4, '0') }}m</div>
        </div>
      </div>

      <div class="readout mono" :style="{ opacity: chrome }" aria-hidden="true">
        <span>{{ String(Math.round(hud.x)).padStart(4, '0') }}·{{ String(Math.round(hud.y)).padStart(4, '0') }}</span>
        <span :class="{ warn: !hud.overSlab }">{{ hud.overSlab ? '· SLAB' : '▼ VOID' }}</span>
        <span>RAIN 4.2MM/H</span>
        <span>{{ hud.clock }}</span>
      </div>

      <div class="cue mono" :style="{ opacity: chrome }" aria-hidden="true"><span>[ scroll ▼ fall ]</span></div>
    </div>
  </section>
</template>

<style scoped>
/* the stage plus a short fall track; its last screen overlaps the archive */
.hero { position: relative; z-index: 2; height: calc(100vh + 75vh); margin-bottom: -100vh; pointer-events: none; }
.hero.plain { height: 100vh; margin-bottom: 0; }
.stage { position: sticky; top: 0; height: 100vh; overflow: hidden; color: var(--ink); pointer-events: auto; }
.landed .stage { pointer-events: none; }
.shade { position: absolute; inset: 0; background: #000; }
.gl, .still { position: absolute; inset: 0; width: 100%; height: 100%; display: block; object-fit: cover; }

.title { position: absolute; left: var(--gutter); bottom: clamp(72px, 12vh, 140px); max-width: min(640px, 80vw); pointer-events: none; }
.title .label { color: #5a6266; margin: 0 0 12px; }
h1 { margin: 0; font-weight: 300; font-size: clamp(40px, 7.4vw, 112px); line-height: 0.95; letter-spacing: 0.04em; color: #2a3034; }
.role { margin: 18px 0 0; font: 400 14px/1.6 var(--font-mono); color: #4a5256; letter-spacing: 0.04em; }
.role span { color: #6a7276; }

.gauge { position: absolute; right: calc(var(--gutter) + 8px); top: 50%; transform: translateY(-50%); font-size: 10px; letter-spacing: 0.12em; color: #50585c; transition: color 0.6s; }
.falling .gauge { color: #aab2b6; }
.gauge-head { margin-bottom: 8px; }
.gauge-track { position: relative; }
.tick { display: flex; gap: 8px; line-height: 1.7; opacity: 0.55; }
.tick.on { opacity: 1; color: var(--accent); }
.falling .tick.on { color: #c4d0d3; }
.tick em { font-style: normal; }
.needle { position: absolute; right: 100%; margin-right: 10px; transform: translateY(-50%); white-space: nowrap; color: var(--accent); }
.falling .needle { color: #c4d0d3; }

.readout { position: absolute; right: var(--gutter); bottom: 22px; display: flex; gap: 18px; flex-wrap: wrap; justify-content: flex-end; font-size: 10px; letter-spacing: 0.14em; color: #50585c; }
.readout .warn { color: var(--sodium); }
.cue { position: absolute; left: 50%; bottom: 22px; transform: translateX(-50%); font-size: 10px; letter-spacing: 0.3em; text-transform: uppercase; color: #50585c; }
.cue span { animation: blink 2.4s steps(2) infinite; }
@keyframes blink { 50% { opacity: 0.35; } }

/* landing: the ASCII cut covers the screen from its first frame, so the stage just goes */
.title, .gauge, .readout, .cue { transition: opacity 0.25s; }
.landed .stage { visibility: hidden; }

@media (max-width: 720px) {
  .gauge { display: none; }
  .readout { left: var(--gutter); justify-content: flex-start; gap: 10px; bottom: 48px; font-size: 9px; }
  .title { bottom: 96px; }
  .role { font-size: 12px; }
}
</style>
