import { nextTick } from 'vue'
import { theme } from './prefs'

// The switch for night mode and 中 / EN: the new state spreads out from the
// button behind an uneven front, and a ragged band of characters rides the
// front, densest at the edge and thinning behind it.
// The reveal is a view transition whose new layer is clipped to a noisy
// polygon that grows from the click; the band is a canvas in the page, so it
// shows inside the new layer. Without view transitions the band still runs
// over an instant switch; with reduced motion the switch is just instant.

const DURATION = 950           // ms
const CELL = 14
const RAMP = ' .·:-=+*≡#%@'
const SIDES = 120              // polygon points around the front
const STEPS = 30               // clip-path keyframes

type VT = { ready: Promise<void>; finished: Promise<void> }
type DocVT = Document & { startViewTransition?: (cb: () => Promise<void> | void) => VT }

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

/** run `apply` (a state change), revealed from the point the user clicked */
export function switchFrom(e: MouseEvent, apply: () => void) {
  const doc = document as DocVT
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { apply(); return }
  const r = (e.currentTarget as HTMLElement | null)?.getBoundingClientRect()
  const ox = r ? r.left + r.width / 2 : e.clientX, oy = r ? r.top + r.height / 2 : e.clientY
  const maxR = Math.hypot(Math.max(ox, innerWidth - ox), Math.max(oy, innerHeight - oy)) * 1.18

  // the front's raggedness: a few periodic waves around the circle, drifting as it grows
  const waves = Array.from({ length: 4 }, (_, i) => ({ f: [3, 5, 8, 13][i], a: [0.07, 0.05, 0.035, 0.025][i], p: Math.random() * 6.28, w: (Math.random() - 0.5) * 6 }))
  const radius = (a: number, t: number) => {
    let n = 0
    for (const v of waves) n += v.a * Math.sin(v.f * a + v.p + v.w * t)
    return maxR * ease(t) * (1 + n)
  }

  if (!doc.startViewTransition) { startBand(ox, oy, maxR, radius); apply(); return }

  const vt = doc.startViewTransition(async () => { apply(); await nextTick() })
  // the band starts after the old page is captured, so no frozen copy of it ends up in the old layer
  vt.ready.then(() => {
    startBand(ox, oy, maxR, radius)
    const frames = Array.from({ length: STEPS + 1 }, (_, k) => {
      const t = k / STEPS
      const pts = Array.from({ length: SIDES }, (_, i) => {
        const a = (i / SIDES) * Math.PI * 2
        const rr = radius(a, t)
        return `${(ox + Math.cos(a) * rr).toFixed(1)}px ${(oy + Math.sin(a) * rr).toFixed(1)}px`
      })
      return { clipPath: `polygon(${pts.join(',')})` }
    })
    document.documentElement.animate(frames, { duration: DURATION, easing: 'linear', pseudoElement: '::view-transition-new(root)' } as KeyframeAnimationOptions)
  }).catch(() => {})
}

/** the ragged band of characters riding the front */
function startBand(ox: number, oy: number, maxR: number, radius: (a: number, t: number) => number) {
  const c = document.createElement('canvas')
  c.className = 'switch-fx'
  c.setAttribute('aria-hidden', 'true')
  const dpr = Math.min(devicePixelRatio, 2)
  const w = innerWidth, h = innerHeight
  c.width = w * dpr; c.height = h * dpr
  document.body.appendChild(c)
  const ctx = c.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.font = `500 ${CELL - 2}px "JetBrains Mono", ui-monospace, monospace`
  ctx.textBaseline = 'top'
  const cols = Math.ceil(w / CELL), rows = Math.ceil(h / CELL)
  const seed = Array.from({ length: cols * rows }, () => Math.random())
  const t0 = performance.now()
  let raf = 0
  const frame = (now: number) => {
    const t = Math.min(1, (now - t0) / DURATION)
    // the band draws in the ink of the page being revealed (read after the switch)
    const ink = theme.value === 'dark' ? '200,208,210' : '42,50,54'
    ctx.clearRect(0, 0, w, h)
    const depth = 36 + 90 * Math.sin(Math.PI * t)          // the band is widest mid-way
    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols; i++) {
        const x = i * CELL + CELL / 2, y = j * CELL + CELL / 2
        const d = Math.hypot(x - ox, y - oy)
        if (d > maxR) continue
        const R = radius(Math.atan2(y - oy, x - ox), t)
        const s = seed[j * cols + i]
        const k = (R - d) / (depth * (0.55 + s * 0.9))     // 0 at the front, 1 at the band's inner edge
        if (k < 0 || k > 1 || s < k * 0.7) continue          // uneven: the band thins out as it goes in
        const g = RAMP[Math.max(1, Math.round((1 - k) * (RAMP.length - 1) * (0.7 + s * 0.3)))]
        ctx.fillStyle = `rgba(${ink},${((1 - k) * 0.85 * (1 - t * 0.35)).toFixed(3)})`
        ctx.fillText(g, i * CELL + 1, j * CELL)
      }
    }
    if (t < 1) raf = requestAnimationFrame(frame)
    else stop()
  }
  const stop = () => { cancelAnimationFrame(raf); c.remove() }
  raf = requestAnimationFrame(frame)
  return { stop }
}
