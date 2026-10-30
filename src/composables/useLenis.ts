import Lenis from 'lenis'
import { onBeforeUnmount, onMounted, shallowRef } from 'vue'

export const lenis = shallowRef<Lenis | null>(null)

export function useLenis() {
  let raf = 0
  onMounted(() => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const l = new Lenis({ lerp: 0.085, wheelMultiplier: 0.9 })
    lenis.value = l
    const loop = (t: number) => { l.raf(t); raf = requestAnimationFrame(loop) }
    raf = requestAnimationFrame(loop)
  })
  onBeforeUnmount(() => { cancelAnimationFrame(raf); lenis.value?.destroy() })
}

export function scrollToId(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  if (lenis.value) lenis.value.scrollTo(el, { offset: -24, duration: 1.6 })
  else el.scrollIntoView({ behavior: 'smooth' })
}
