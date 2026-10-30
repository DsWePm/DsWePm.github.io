// Phone tilt as a stand-in for the mouse: -1..1 on both axes, relative to how
// the phone was held when the sensor started (the neutral pose slowly follows
// the hand, so a long read in a new posture re-centres on its own).
// Needs a secure context; iOS also wants a permission prompt from a tap.

const RANGE = 18          // degrees of tilt for full deflection
const RECENTRE = 0.15     // per second: how fast the neutral pose drifts to the current one

type Orientation = typeof DeviceOrientationEvent & { requestPermission?: () => Promise<'granted' | 'denied'> }

export function startTilt(onTilt: (x: number, y: number) => void): () => void {
  if (typeof DeviceOrientationEvent === 'undefined' || !matchMedia('(pointer: coarse)').matches) return () => {}
  let base: [number, number] | null = null
  let last = 0

  function onOrient(e: DeviceOrientationEvent) {
    if (e.beta == null || e.gamma == null) return
    // screen-relative axes: swap and flip with the screen rotation
    const a = (screen.orientation?.angle ?? 0) % 360
    let x = e.gamma, y = e.beta
    if (a === 90) [x, y] = [e.beta, -e.gamma]
    else if (a === 270) [x, y] = [-e.beta, e.gamma]
    else if (a === 180) [x, y] = [-e.gamma, -e.beta]
    const now = performance.now()
    if (!base) base = [x, y]
    else {
      const k = Math.min(1, ((now - last) / 1000) * RECENTRE)
      base[0] += (x - base[0]) * k; base[1] += (y - base[1]) * k
    }
    last = now
    const c = (v: number) => Math.max(-1, Math.min(1, v / RANGE))
    onTilt(c(x - base[0]), -c(y - base[1]))     // tilt the top away = look further up the shaft
  }
  const listen = () => addEventListener('deviceorientation', onOrient)

  const D = DeviceOrientationEvent as Orientation
  let ask: (() => void) | null = null
  if (typeof D.requestPermission === 'function') {
    // iOS: only a tap may ask
    ask = () => {
      D.requestPermission!().then((r) => { if (r === 'granted') listen() }).catch(() => {})
      removeEventListener('touchend', ask!)
    }
    addEventListener('touchend', ask, { once: true })
  } else listen()

  return () => {
    removeEventListener('deviceorientation', onOrient)
    if (ask) removeEventListener('touchend', ask)
  }
}
