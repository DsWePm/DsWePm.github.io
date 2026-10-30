<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { lenis } from '../composables/useLenis'

// HUD scrollbar: a dashed rail with section ticks and a bracketed thumb that
// shows the percentage. Drag the thumb or click the rail to move; it replaces
// the native scrollbar on mouse devices.
const enabled = ref(false)
const st = reactive({ p: 0, thumb: 10, top: 0, dragging: false, hover: false })
const marks = ref<{ id: string; label: string; at: number }[]>([])
// ticks come from whatever the current page marks with data-hud-mark="LABEL" (sections, article headings)
let raf = 0, grab = 0, max = 1
let ro: ResizeObserver | undefined

function maxScroll() { return Math.max(1, document.documentElement.scrollHeight - innerHeight) }

function measure() {
  max = maxScroll()
  marks.value = [...document.querySelectorAll<HTMLElement>('[data-hud-mark]')].map((el, i) => ({
    id: el.id || String(i), label: el.dataset.hudMark!,
    at: Math.min(1, (el.getBoundingClientRect().top + scrollY) / max),
  }))
}

function loop() {
  raf = requestAnimationFrame(loop)
  st.p = Math.min(1, Math.max(0, scrollY / max))
  st.thumb = Math.max(4, (innerHeight / (max + innerHeight)) * 100)
  st.top = st.p * (100 - st.thumb)
}

function scrollTo(p: number) {
  const y = Math.min(1, Math.max(0, p)) * maxScroll()
  if (lenis.value) lenis.value.scrollTo(y, { immediate: st.dragging })
  else window.scrollTo(0, y)
}
function onRail(e: PointerEvent) {
  if (st.dragging) return
  scrollTo(e.clientY / innerHeight)
}
function onDown(e: PointerEvent) {
  st.dragging = true
  grab = e.clientY - (st.top / 100) * innerHeight
  ;(e.target as HTMLElement).setPointerCapture(e.pointerId)
}
function onMove(e: PointerEvent) {
  if (!st.dragging) return
  scrollTo((e.clientY - grab) / (innerHeight * (1 - st.thumb / 100)))
}
function onUp() { st.dragging = false }

onMounted(() => {
  enabled.value = matchMedia('(pointer: fine)').matches
  if (!enabled.value) return
  document.documentElement.classList.add('has-scroll-hud')
  measure()
  addEventListener('resize', measure)
  setTimeout(measure, 1500)
  ro = new ResizeObserver(() => measure())       // page height changes, including route changes
  ro.observe(document.body)
  raf = requestAnimationFrame(loop)
})
onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  removeEventListener('resize', measure)
  ro?.disconnect()
  document.documentElement.classList.remove('has-scroll-hud')
})
</script>

<template>
  <div v-if="enabled" class="scroll-hud mono" :class="{ active: st.dragging || st.hover }"
       @pointerenter="st.hover = true; measure()" @pointerleave="st.hover = false" aria-hidden="true">
    <div class="rail" @pointerdown.self="onRail" />
    <button v-for="m in marks" :key="m.id" class="mark" :style="{ top: `${m.at * 100}%` }" tabindex="-1" @click="scrollTo(m.at)">
      <span>{{ m.label }}</span>
    </button>
    <div class="thumb" :style="{ top: `${st.top}%`, height: `${st.thumb}%` }"
         @pointerdown="onDown" @pointermove="onMove" @pointerup="onUp" @pointercancel="onUp">
      <i class="c t" /><i class="c b" />
      <em>{{ String(Math.round(st.p * 100)).padStart(3, '0') }}</em>
    </div>
  </div>
</template>

<style scoped>
.scroll-hud { position: fixed; top: 0; right: 0; bottom: 0; width: 18px; z-index: 80; color: #7b858a; mix-blend-mode: difference; }
.rail { position: absolute; top: 0; bottom: 0; right: 0; width: 18px; }
.rail::after { content: ''; position: absolute; top: 6px; bottom: 6px; right: 8px; width: 1px; background: repeating-linear-gradient(180deg, currentColor 0 3px, transparent 3px 7px); opacity: 0.6; }
.thumb { position: absolute; right: 4px; width: 9px; cursor: grab; touch-action: none; }
.thumb::before { content: ''; position: absolute; inset: 0 3px; background: currentColor; opacity: 0.55; transition: opacity 0.2s; }
.active .thumb::before { opacity: 0.9; }
.c { position: absolute; left: 0; right: 0; height: 4px; border: 0 solid currentColor; }
.c.t { top: -3px; border-top-width: 1px; border-left-width: 1px; border-right-width: 1px; }
.c.b { bottom: -3px; border-bottom-width: 1px; border-left-width: 1px; border-right-width: 1px; }
.thumb em { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); font-style: normal; font-size: 9px; letter-spacing: 0.14em; opacity: 0; transition: opacity 0.2s; white-space: nowrap; }
.active .thumb em { opacity: 1; }
.mark { position: absolute; right: 4px; width: 9px; height: 1px; background: currentColor; padding: 0; opacity: 0.7; }
.mark span { position: absolute; right: 16px; top: -6px; font-size: 9px; letter-spacing: 0.18em; white-space: nowrap; opacity: 0; transform: translateX(6px); transition: opacity 0.2s, transform 0.3s var(--ease-out); }
.active .mark span { opacity: 0.85; transform: none; }
</style>
