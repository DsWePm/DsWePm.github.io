import { onBeforeUnmount, onMounted, type Ref } from 'vue'

/** run `fn(t)` on animation frames, at most `fps` a second, only while `el` is on screen */
export function useVisibleLoop(el: Ref<HTMLElement | undefined>, fn: (t: number) => void, fps = 30) {
  let raf = 0, last = 0
  const gap = 1000 / fps - 2
  const loop = (t: number) => {
    raf = requestAnimationFrame(loop)
    if (t - last < gap) return
    last = t
    fn(t)
  }
  const io = new IntersectionObserver(([e]) => {
    cancelAnimationFrame(raf); raf = 0
    if (e.isIntersecting) raf = requestAnimationFrame(loop)
  })
  onMounted(() => { if (el.value) io.observe(el.value) })
  onBeforeUnmount(() => { cancelAnimationFrame(raf); io.disconnect() })
}
