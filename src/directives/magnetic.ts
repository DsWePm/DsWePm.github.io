import type { Directive } from 'vue'

type El = HTMLElement & { __mag?: { move: (e: PointerEvent) => void; leave: () => void } }

/** v-magnetic="0.3": element leans toward the pointer while hovered. */
export const magnetic: Directive<El, number | undefined> = {
  mounted(el, binding) {
    if (matchMedia('(pointer: coarse)').matches) return
    const strength = binding.value ?? 0.3
    el.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)'
    const move = (e: PointerEvent) => {
      const r = el.getBoundingClientRect()
      const dx = e.clientX - (r.left + r.width / 2)
      const dy = e.clientY - (r.top + r.height / 2)
      el.style.transform = `translate(${dx * strength}px, ${dy * strength}px)`
    }
    const leave = () => { el.style.transform = '' }
    el.addEventListener('pointermove', move)
    el.addEventListener('pointerleave', leave)
    el.__mag = { move, leave }
  },
  unmounted(el) {
    if (!el.__mag) return
    el.removeEventListener('pointermove', el.__mag.move)
    el.removeEventListener('pointerleave', el.__mag.leave)
  },
}
