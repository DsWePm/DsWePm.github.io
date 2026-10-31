import { reactive } from 'vue'

// What the hero has fetched so far, for the loading screen: written by HeroStill as each
// fall frame arrives, read by LoadingScreen (the shaft survey, the frame map, the telemetry).
export const loadStats = reactive({
  total: 254,          // fall frames (from fall.json once it is in)
  done: 0,             // frames fetched
  reached: 0,          // frames fetched without a gap from the top: how deep the fall can go
  alt: 18,             // camera height over the slab top at `reached` (negative: down the shaft)
  maxDepth: 62.1,
  bytes: 0,
  start: performance.now(),
  map: '',             // one character per frame: '.' waiting, '|' in (ASCII: the web font has no block glyphs)
  log: [] as string[], // the last few requests, newest first
})

let got = new Uint8Array(0)

export function statsBegin(total: number, maxDepth: number) {
  got = new Uint8Array(total)
  Object.assign(loadStats, { total, maxDepth, done: 0, reached: 0, map: '.'.repeat(total) })
}

export function statsFrame(i: number, name: string, bytes: number, altAt: (f: number) => number) {
  got[i] = 1
  loadStats.done++
  loadStats.bytes += bytes
  let r = loadStats.reached
  while (r < got.length && got[r]) r++
  loadStats.reached = r
  loadStats.alt = altAt(Math.max(0, r - 1))
  loadStats.map = loadStats.map.slice(0, i) + '|' + loadStats.map.slice(i + 1)
  const t = ((performance.now() - loadStats.start) / 1000).toFixed(2).padStart(6, '0')
  loadStats.log = [`${t} GET ${name} ${(bytes / 1024).toFixed(0).padStart(4)}K`, ...loadStats.log].slice(0, 5)
}
