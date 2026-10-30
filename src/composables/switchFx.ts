import { nextTick } from 'vue'
import { theme } from './prefs'

// The switch for night mode and 中 / EN: the new state spreads out from the
// button behind an uneven front, and the seam is dithered in characters rather
// than cut: ahead of the front the new page's colour bleeds out as sparse
// ░▒▓ blocks, just behind it blocks of the old colour linger, and a ragged
// band of glyphs rides the edge itself.
// The reveal is a view transition whose new layer is clipped to a noisy
// polygon that grows from the click. The dither is a canvas with its own
// view-transition-name, so it is a live layer above both pages and can draw
// on either side of the front. Without view transitions the glyph band still
// runs over an instant switch; with reduced motion the switch is just instant.

const DURATION = 950           // ms
const CELL = 14
const RAMP = ' .·:-=+*≡#%@'
const BLOCKS = '░▒▓█'
const SIDES = 120              // polygon points around the front
const STEPS = 30               // clip-path keyframes
const PAPER = { light: '227,230,231', dark: '16,20,23' }    // the archive's background in each mode
const INK = { light: '42,50,54', dark: '200,208,210' }

type VT = { ready: Promise<void>; finished: Promise<void> }
type DocVT = Document & { startViewTransition?: (cb: () => Promise<void> | void) => VT }
type Rect = { l: number; t: number; r: number; b: number }

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

/** where night mode changes anything: the archive / reading pages on screen, minus the hero stage over them */
function themedRects(): Rect[] {
  const stage = document.querySelector<HTMLElement>('.hero .stage')
  const s = stage && getComputedStyle(stage).visibility !== 'hidden' ? stage.getBoundingClientRect() : null
  return [...document.querySelectorAll<HTMLElement>('.theme-light')].map((el) => {
    const r = el.getBoundingClientRect()
    // the hero stage sits on top of the archive's first screen until the landing
    const top = s && s.bottom > r.top ? Math.max(r.top, s.bottom) : r.top
    return { l: r.left, t: top, r: r.right, b: r.bottom }
  }).filter((r) => r.b > r.t && r.b > 0 && r.t < innerHeight)
}

/** run `apply` (a state change), revealed from the point the user clicked; `recolours` for night mode */
export function switchFrom(e: MouseEvent, apply: () => void, recolours = false) {
  const doc = document as DocVT
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { apply(); return }
  const r = (e.currentTarget as HTMLElement | null)?.getBoundingClientRect()
  const ox = r ? r.left + r.width / 2 : e.clientX, oy = r ? r.top + r.height / 2 : e.clientY
  const maxR = Math.hypot(Math.max(ox, innerWidth - ox), Math.max(oy, innerHeight - oy)) * 1.25

  // the front's raggedness: a few periodic waves around the circle, drifting as it grows
  const waves = Array.from({ length: 4 }, (_, i) => ({ f: [3, 5, 8, 13][i], a: [0.07, 0.05, 0.035, 0.025][i], p: Math.random() * 6.28, w: (Math.random() - 0.5) * 6 }))
  const radius = (a: number, t: number) => {
    let n = 0
    for (const v of waves) n += v.a * Math.sin(v.f * a + v.p + v.w * t)
    return maxR * ease(t) * (1 + n)
  }
  const from = theme.value
  const seam = recolours ? { old: PAPER[from], neu: PAPER[from === 'dark' ? 'light' : 'dark'], rects: themedRects() } : null

  if (!doc.startViewTransition) { startDither(ox, oy, maxR, radius, null).run(); apply(); return }

  // created before the transition, empty, so it gets its own (live) layer above both pages
  const fx = startDither(ox, oy, maxR, radius, seam)
  const vt = doc.startViewTransition(async () => { apply(); await nextTick() })
  vt.ready.then(() => {
    fx.run()
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
  }).catch(() => fx.stop())
}

function startDither(ox: number, oy: number, maxR: number, radius: (a: number, t: number) => number,
                     seam: { old: string; neu: string; rects: Rect[] } | null) {
  // one at a time: a second layer with the same view-transition-name would abort the transition
  document.querySelectorAll('.switch-fx').forEach((el) => el.remove())
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
  const inThemed = (x: number, y: number) => !!seam && seam.rects.some((r) => x >= r.l && x < r.r && y >= r.t && y < r.b)
  let raf = 0, t0 = 0

  const frame = (now: number) => {
    const t = Math.min(1, (now - t0) / DURATION)
    // glyphs in the ink of the page being revealed (read after the switch)
    const ink = INK[theme.value]
    ctx.clearRect(0, 0, w, h)
    const depth = 36 + 90 * Math.sin(Math.PI * t)          // the band is widest mid-way
    const fade = 1 - t * 0.35
    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols; i++) {
        const x = i * CELL + CELL / 2, y = j * CELL + CELL / 2
        const d = Math.hypot(x - ox, y - oy)
        if (d > maxR) continue
        const R = radius(Math.atan2(y - oy, x - ox), t)
        const s = seed[j * cols + i]
        const span = depth * (0.55 + s * 0.9)
        const k = (R - d) / span                            // > 0 behind the front, < 0 ahead of it
        if (seam && k > -1 && k < 0.6 && inThemed(x, y)) {
          // dither the seam: ahead, the new colour bleeds out; just behind, the old colour lingers
          const ahead = k < 0
          const q = ahead ? 1 + k : 1 - k / 0.6               // 1 at the front, 0 at the dither's far edge
          if (s < q * 0.95) {
            const b = BLOCKS[Math.min(BLOCKS.length - 1, Math.floor(q * q * BLOCKS.length * (0.75 + s * 0.4)))]
            ctx.fillStyle = `rgba(${ahead ? seam.neu : seam.old},${(0.35 + 0.65 * q).toFixed(3)})`
            ctx.fillText(b, i * CELL, j * CELL)
          }
        }
        if (k < 0 || k > 1 || s < k * 0.7) continue          // the glyph band: uneven, thinning as it goes in
        const g = RAMP[Math.max(1, Math.round((1 - k) * (RAMP.length - 1) * (0.7 + s * 0.3)))]
        ctx.fillStyle = `rgba(${ink},${((1 - k) * 0.85 * fade).toFixed(3)})`
        ctx.fillText(g, i * CELL + 1, j * CELL)
      }
    }
    if (t < 1) raf = requestAnimationFrame(frame)
    else stop()
  }
  const stop = () => { cancelAnimationFrame(raf); c.remove() }
  const run = () => { t0 = performance.now(); raf = requestAnimationFrame(frame) }
  return { run, stop }
}
