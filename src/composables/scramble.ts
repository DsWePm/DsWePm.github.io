const NOISE = '▓▒░#%&@*+=-:./\\|<>'

/**
 * Decode `target` from noise, calling `onUpdate` every frame.
 * Returns a cancel function.
 */
export function scramble(target: string, onUpdate: (s: string) => void, duration = 900): () => void {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { onUpdate(target); return () => {} }
  const chars = [...target]
  const reveal = chars.map(() => Math.random() * duration * 0.85)
  const start = performance.now()
  let raf = 0
  const step = (now: number) => {
    const t = now - start
    let out = ''
    for (let i = 0; i < chars.length; i++) {
      const ch = chars[i]
      out += t >= reveal[i] || ch === ' ' || ch === '\n' ? ch : NOISE[(Math.random() * NOISE.length) | 0]
    }
    onUpdate(out)
    if (t < duration) raf = requestAnimationFrame(step)
    else onUpdate(target)
  }
  raf = requestAnimationFrame(step)
  return () => cancelAnimationFrame(raf)
}
