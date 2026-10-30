// Download the CC0 Poly Haven sources used by build_city.py into
// tools/blender/textures/ (git-ignored). Only the baked result ships.
//   node tools/blender/fetch_textures.mjs
import { mkdir, writeFile, access } from 'node:fs/promises'

const ROOT = new URL('./textures/', import.meta.url)
const TEXTURES = ['concrete_wall_003', 'painted_plaster_wall', 'floor_tiles_02', 'rusty_metal_02', 'concrete_floor_02',
  // laundry: bed sheets and shirts
  'gingham_check', 'floral_jacquard', 'fabric_pattern_05', 'fabric_pattern_07', 'cotton_jersey']
const MAPS = { Diffuse: 'diff', nor_gl: 'nor', Rough: 'rough' }
const HDRI = 'overcast_soil_puresky'

async function get(url, dest) {
  try { await access(dest); return 'cached' } catch {}
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${url}`)
  await writeFile(dest, Buffer.from(await res.arrayBuffer()))
  return 'ok'
}

await mkdir(ROOT, { recursive: true })
for (const id of TEXTURES) {
  const files = await (await fetch(`https://api.polyhaven.com/files/${id}`)).json()
  for (const [map, short] of Object.entries(MAPS)) {
    // patterned fabrics ship colour variants instead of a single Diffuse map
    const src = files[map] ?? (map === 'Diffuse' ? files.col_01 ?? files.col_1 : undefined)
    const f = src['2k'].jpg
    console.log(id, short, await get(f.url, new URL(`${id}_${short}.jpg`, ROOT)))
  }
}
const h = (await (await fetch(`https://api.polyhaven.com/files/${HDRI}`)).json()).hdri['2k'].hdr
console.log(HDRI, await get(h.url, new URL(`${HDRI}.hdr`, ROOT)))
