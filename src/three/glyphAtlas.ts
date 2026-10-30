import { CanvasTexture, LinearFilter } from 'three'

/** Glyphs ordered from empty to dense; the ASCII pass picks one by luminance. */
export const GLYPHS = ' .·:-=+*≡#%@'

export function createGlyphAtlas(cell = 32): CanvasTexture {
  const n = [...GLYPHS].length
  const canvas = document.createElement('canvas')
  canvas.width = cell * n
  canvas.height = cell
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.fillStyle = '#fff'
  ctx.font = `500 ${cell * 0.78}px "JetBrains Mono", ui-monospace, monospace`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ;[...GLYPHS].forEach((g, i) => ctx.fillText(g, i * cell + cell / 2, cell * 0.54))
  const tex = new CanvasTexture(canvas)
  tex.minFilter = tex.magFilter = LinearFilter
  tex.generateMipmaps = false
  return tex
}
