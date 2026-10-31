import * as THREE from 'three'
import { quadVert, heroFrag, rippleFrag } from './shaders'
import { createGlyphAtlas, GLYPHS } from '../three/glyphAtlas'
import { statsBegin, statsFrame } from '../composables/loadStats'

const BASE = import.meta.env.BASE_URL
const ASPECT = 16 / 9
const PARALLAX = 0.016       // image-uv shift of the slab at full mouse deflection
// Phones get a far smaller frame budget: iOS kills a page's process (and reloads it, over and
// over) once it holds a few hundred MB, and every browser on iOS is WebKit.
const PHONE = matchMedia('(pointer: coarse)').matches || /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
const AHEAD = PHONE ? 2 : 10         // decoded fall frames ahead of the one on screen
const MAX_DECODED = PHONE ? 10 : 24  // decoded fall frames held at once (~8 MB each at 1080p, ~3.7 MB at 720p)
const DECODERS = PHONE ? 2 : 4       // decodes in flight
// Every fall frame is also kept small, for when the fall outruns the decoder (~80 full frames/s on
// desktop, far fewer on a phone), as one layer each of a single texture array on the GPU: 640 x 360
// (~230 MB) where there is memory for it, 480 x 270 (~130 MB) on other desktops, 320 x 180 (~58 MB)
// on phones. Not as ImageBitmaps: WebKit backs each with its own buffer, and a few hundred of them,
// however small, get the page killed. Phones decode full frames at 720p.
const LOW = PHONE ? [320, 180] : ((navigator as { deviceMemory?: number }).deviceMemory ?? 4) >= 8 ? [640, 360] : [480, 270]
const FULL = PHONE ? { resizeWidth: 1280, resizeHeight: 720, resizeQuality: 'high' as ResizeQuality } : {}
const BITMAP: ImageBitmapOptions = { imageOrientation: 'flipY', premultiplyAlpha: 'none', colorSpaceConversion: 'none' }
const damp = (a: number, b: number, l: number, dt: number) => b + (a - b) * Math.exp(-l * dt)
const smooth = (a: number, b: number, v: number) => { const t = Math.min(1, Math.max(0, (v - a) / (b - a))); return t * t * (3 - 2 * t) }

/** written by render_hero.py; z is the simulated camera height per frame, lip the frame it passes the slab */
export interface FallMeta { frames: number; fps: number; zStart: number; zLip: number; zFloor: number; slab: number; depth: number; z: number[]; lip: number; pattern: string; first: number }

/**
 * Hero over Cycles pre-renders: an interactive still (depth parallax, slab
 * ripples, rain loop, intro decode) that crossfades into the scroll-scrubbed
 * fall sequence. Frame 0 of the sequence is the same camera as the still.
 */
export class HeroStill {
  readonly renderer: THREE.WebGLRenderer
  private canvas: HTMLCanvasElement
  private scene = new THREE.Scene()
  private cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)
  private mat: THREE.ShaderMaterial
  private ripple!: { a: THREE.WebGLRenderTarget; b: THREE.WebGLRenderTarget; mat: THREE.ShaderMaterial; scene: THREE.Scene; drops: THREE.Vector4[] }
  private depthData: ImageData | null = null
  private mouse = new THREE.Vector2()
  private mouseDamped = new THREE.Vector2()
  private pointerUv = new THREE.Vector2(-1, -1)
  private lastUv = new THREE.Vector2(-1, -1)
  private pointerIn = false
  private tilted = false
  private splash = 0         // accumulator for random big-drop ripples
  private introStart = -1
  private clock = new THREE.Clock()
  private raf = 0
  private parallax = 1
  // fall sequence
  meta!: FallMeta
  private frames: (Blob | null)[] = []      // encoded files; decoding all 254 would take ~2 GB
  // Uploading an <img> makes the browser decode it on the spot (~30 ms for a 1080p webp), so the
  // frames around the scroll are decoded ahead into ImageBitmaps; from a Blob that runs off the
  // main thread (from an <img> it doesn't). A fast fall can outrun that decoder, so a small copy of
  // every frame stands in until the full one is ready: in motion it reads the same.
  // Frame i lives in slot i % 2: stepping one frame re-uploads one texture, not both.
  private bitmaps = new Map<number, ImageBitmap>()
  private decoding = new Set<number>()
  private release: ImageBitmap[] = []
  private releasing = false
  private lowTex: THREE.DataArrayTexture | null = null
  private lowGl: WebGLTexture | null = null
  private lowHas = new Uint8Array(0)
  private lowsOk = true       // off without array room, or if the browser ignores resizeWidth
  private lastFrame = -1      // the frame last put on screen
  private slots = [new THREE.Texture(), new THREE.Texture()]
  private slotFrame = [-1, -1]
  private target = 0          // frame the scroll asks for
  private shown = 0           // frame on screen (damped)
  private impactArmed = true
  private rainVideo: HTMLVideoElement | null = null
  active = true
  overSlab = true
  /** called once when the fall reaches the impact frame while scrolling down */
  onImpact: () => void = () => {}

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas
    this.renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false, powerPreference: 'high-performance' })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))   // full-screen shader: 2x costs ~1.8x the fill for little gain
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace    // images are already display-referred
    // bitmaps arrive flipped already (createImageBitmap below); WebGL ignores flipY for them
    for (const t of this.slots) { t.colorSpace = THREE.NoColorSpace; t.minFilter = THREE.LinearFilter; t.generateMipmaps = false; t.flipY = false }
    const black = new THREE.DataTexture(new Uint8Array([0, 0, 0, 255]), 1, 1); black.needsUpdate = true
    this.mat = new THREE.ShaderMaterial({
      vertexShader: quadVert, fragmentShader: heroFrag, depthTest: false,
      uniforms: {
        tSlab: { value: null }, tCanyon: { value: null }, tDepth: { value: null }, tRipple: { value: null },
        tFrameA: { value: black }, tFrameB: { value: black }, tRain: { value: black },
        tLow: { value: null }, uLowA: { value: -1 }, uLowB: { value: -1 },
        tGlyph: { value: createGlyphAtlas() }, uGlyphs: { value: [...GLYPHS].length }, uCell: { value: 9 },
        uRes: { value: new THREE.Vector2(1, 1) }, uImgAspect: { value: ASPECT },
        uShift: { value: new THREE.Vector2() }, uPointer: { value: this.pointerUv }, uPointerOn: { value: 0 },
        uRippleTexel: { value: new THREE.Vector2() }, uTime: { value: 0 }, uIntro: { value: 1 },
        uSeq: { value: 0 }, uFrameMix: { value: 0 }, uRainAmt: { value: 1.0 },
      },
    })
    this.scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.mat))
  }

  get frameCount() { return this.frames.length }
  get progressFrame() { return this.shown }

  private frameUrl(i: number) {
    const n = i + this.meta.first
    return BASE + 'hero/' + this.meta.pattern.replace('{n:04}', String(n).padStart(4, '0'))
  }

  private loadFrame(i: number) {
    return fetch(this.frameUrl(i))
      .then((r) => (r.ok ? r.blob() : null))
      .then(async (b) => {
        this.frames[i] = b
        statsFrame(i, this.frameUrl(i).split('/').pop()!, b?.size ?? 0, (f) => this.meta.z[f] ?? 0)
        if (!b || !this.lowsOk || !this.lowGl) return
        const low = await createImageBitmap(b, { ...BITMAP, resizeWidth: LOW[0], resizeHeight: LOW[1], resizeQuality: 'medium' })
        if (low.width !== LOW[0] || low.height !== LOW[1]) { low.close(); this.lowsOk = false; return }
        // straight into its layer, then let the bitmap go
        const gl = this.renderer.getContext() as WebGL2RenderingContext
        this.renderer.state.bindTexture(gl.TEXTURE_2D_ARRAY, this.lowGl)
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false)
        gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false)
        gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE)
        gl.texSubImage3D(gl.TEXTURE_2D_ARRAY, 0, 0, 0, i, LOW[0], LOW[1], 1, gl.RGBA, gl.UNSIGNED_BYTE, low)
        low.close()
        this.lowHas[i] = 1
      })
      .catch(() => {})
  }

  async load(onProgress: (p: number) => void) {
    const tl = new THREE.TextureLoader()
    // the loader stays up until every fall frame is in (a fall reaches frames that aren't yet would
    // stall): the stills are the first 15 % of the bar, the frames the rest
    let still = 0, framesIn = 0
    const report = () => onProgress(0.15 * (still / 4) + 0.85 * (this.frames.length ? framesIn / this.frames.length : 0))
    const tick = () => { still++; report() }
    const tex = (name: string) => tl.loadAsync(BASE + 'hero/' + name).then((t) => {
      t.colorSpace = THREE.NoColorSpace
      t.minFilter = THREE.LinearFilter; t.generateMipmaps = false
      t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping
      tick(); return t
    })
    const meta = fetch(BASE + 'hero/fall.json').then((r) => r.json() as Promise<FallMeta>).then((m) => { this.meta = m; tick(); return m })
    const [slab, canyon, depth, m] = await Promise.all([tex('slab.jpg'), tex('canyon.jpg'), tex('depth.png'), meta])
    const u = this.mat.uniforms
    u.tSlab.value = slab; u.tCanyon.value = canyon; u.tDepth.value = depth
    this.frames = new Array(m.frames).fill(null)
    this.makeLows(m.frames)
    statsBegin(m.frames, m.depth)
    await this.streamFrames(() => { framesIn++; report() })
    this.startRain()
    // CPU copy of the mask for the HUD ("over slab" vs "over the void")
    const img = depth.image as HTMLImageElement
    const c = Object.assign(document.createElement('canvas'), { width: img.width, height: img.height })
    const ctx = c.getContext('2d', { willReadFrequently: true })!
    ctx.drawImage(img, 0, 0)
    this.depthData = ctx.getImageData(0, 0, img.width, img.height)
    this.buildRipple()
    this.resize()
    if (import.meta.env.DEV) (window as unknown as { __hero: HeroStill }).__hero = this
  }

  private async streamFrames(onFrame: () => void) {
    const queue = this.frames.map((_, i) => i)
    const worker = async () => { for (let i = queue.shift(); i !== undefined; i = queue.shift()) { await this.loadFrame(i); onFrame() } }
    await Promise.all(Array.from({ length: 6 }, worker))
  }

  private startRain() {
    const v = document.createElement('video')
    v.muted = true; v.loop = true; v.playsInline = true; v.autoplay = true; v.preload = 'auto'
    v.src = BASE + 'hero/rain.mp4'
    v.addEventListener('canplay', () => {
      const t = new THREE.VideoTexture(v); t.colorSpace = THREE.NoColorSpace
      this.mat.uniforms.tRain.value = t
      v.play().catch(() => {})
    }, { once: true })
    this.rainVideo = v
  }

  private buildRipple() {
    const w = 1280, h = 720       // fine grid: small rings, slow spread (one texel per step)
    const opts = { type: THREE.HalfFloatType, depthBuffer: false, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter }
    const a = new THREE.WebGLRenderTarget(w, h, opts), b = new THREE.WebGLRenderTarget(w, h, opts)
    const drops = Array.from({ length: 16 }, () => new THREE.Vector4())
    const mat = new THREE.ShaderMaterial({
      vertexShader: quadVert, fragmentShader: rippleFrag, depthTest: false,
      uniforms: { uPrev: { value: b.texture }, uTexel: { value: new THREE.Vector2(1 / w, 1 / h) }, uDrops: { value: drops }, uAspect: { value: ASPECT } },
    })
    const scene = new THREE.Scene()
    scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat))
    const r = this.renderer
    r.setClearColor(0x000000, 0)
    for (const t of [a, b]) { r.setRenderTarget(t); r.clear() }
    r.setRenderTarget(null)
    this.ripple = { a, b, mat, scene, drops }
    this.mat.uniforms.uRippleTexel.value.set(1 / w, 1 / h)
  }

  /** screen px -> image uv (same cover mapping as the shader) */
  private toImageUv(x: number, y: number, out: THREE.Vector2) {
    const r = this.canvas.getBoundingClientRect()
    const su = (x - r.left) / r.width, sv = 1 - (y - r.top) / r.height
    const sa = r.width / r.height
    const s = sa > ASPECT ? [1, ASPECT / sa] : [sa / ASPECT, 1]
    return out.set((su - 0.5) * s[0] * 0.975 + 0.5, (sv - 0.5) * s[1] * 0.975 + 0.5)
  }

  setPointer(x: number, y: number, inside: boolean) {
    const r = this.canvas.getBoundingClientRect()
    if (!r.width || !Number.isFinite(x) || !Number.isFinite(y)) return
    if (!this.tilted) this.mouse.set(((x - r.left) / r.width) * 2 - 1, -(((y - r.top) / r.height) * 2 - 1))
    this.toImageUv(x, y, this.pointerUv)
    this.pointerIn = inside
    if (this.depthData) {
      const { width, height, data } = this.depthData
      const px = Math.min(width - 1, Math.max(0, Math.floor(this.pointerUv.x * width)))
      const py = Math.min(height - 1, Math.max(0, Math.floor((1 - this.pointerUv.y) * height)))
      this.overSlab = data[(py * width + px) * 4 + 1] > 127
    }
  }

  /** phone tilt drives the parallax instead of the finger once the sensor reports */
  setTilt(x: number, y: number) {
    this.tilted = true
    this.mouse.set(x, y)
  }

  /** 0..1 over the fall; 0 shows the interactive still */
  setProgress(p: number) {
    if (!this.frames.length) return
    this.target = Math.min(1, Math.max(0, p)) * (this.frames.length - 1)
  }

  /** depth below the slab top for a (fractional) frame, from the same physics as the render */
  depthAt(f: number) {
    const m = this.meta
    if (!m?.z) return 0
    const i = Math.min(m.z.length - 2, Math.max(0, Math.floor(f)))
    const z = m.z[i] + (m.z[i + 1] - m.z[i]) * Math.min(1, Math.max(0, f - i))
    return Math.max(0, Math.min(m.depth, -z))
  }

  /** jump the displayed frame (used after the cut to the archive / when returning) */
  snapTo(p: number) { this.setProgress(p); this.shown = this.target }

  resize() {
    const w = this.canvas.clientWidth, h = this.canvas.clientHeight
    if (!w || !h) return
    this.renderer.setSize(w, h, false)
    const dpr = this.renderer.getPixelRatio()
    this.mat.uniforms.uRes.value.set(w * dpr, h * dpr)
    this.mat.uniforms.uCell.value = Math.round(9 * dpr)
  }

  beginIntro() { this.introStart = this.mat.uniforms.uTime.value }

  start() {
    this.clock.start()
    const loop = () => { this.raf = requestAnimationFrame(loop); if (this.active) this.tick() }
    loop()
  }

  /** the texture array for the small frames: storage only, filled layer by layer as they decode */
  private makeLows(n: number) {
    const gl = this.renderer.getContext() as WebGL2RenderingContext
    this.lowHas = new Uint8Array(n)
    if (gl.getParameter(gl.MAX_ARRAY_TEXTURE_LAYERS) < n) { this.lowsOk = false; return }
    const t = new THREE.DataArrayTexture(null, LOW[0], LOW[1], n)
    t.colorSpace = THREE.NoColorSpace; t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false
    t.source.dataReady = false              // allocate, don't upload
    t.needsUpdate = true                    // (three only creates the GL texture for a version > 0)
    this.renderer.initTexture(t)
    this.lowTex = t
    this.lowGl = (this.renderer.properties.get(t) as { __webglTexture: WebGLTexture }).__webglTexture
    this.mat.uniforms.tLow.value = t
  }

  private ready(i: number) { return this.bitmaps.has(i) || !!this.lowHas[i] }

  /**
   * the frame to show for `a` moving in `dir`: the nearest ready one not past `a`, back to the last
   * frame shown, so a frame decoded further ahead never flashes up before the ones in between
   */
  private pick(a: number, dir: number) {
    const n = this.frames.length
    for (let i = a; i >= 0 && i < n && (this.lastFrame < 0 || (i - this.lastFrame) * dir >= 0); i -= dir) if (this.ready(i)) return i
    return this.nearestReady(a)
  }

  private nearestReady(i: number) {
    for (let d = 0; d < this.frames.length; d++) {
      if (this.ready(i - d)) return i - d
      if (this.ready(i + d)) return i + d
    }
    return -1
  }

  /**
   * decode full-size frames from the one on screen (`a`) towards the scroll target, nearest first;
   * when the target is far ahead they are spread along the way instead of piling up behind it
   */
  private warm(a: number, target: number) {
    const n = this.frames.length
    const dir = target >= a ? 1 : -1
    const stride = Math.max(1, Math.ceil(Math.abs(target - a) / AHEAD))
    // release first, so the budget has room: frames left behind or beyond the stretch being decoded
    for (const [i, b] of this.bitmaps) {
      const ahead = (i - a) * dir
      if ((ahead >= -2 && ahead <= AHEAD * stride + 2) || i === this.lastFrame) continue
      // already uploaded if it sits in a slot; forget the slot so it is never reused without its bitmap
      const k = this.slotFrame.indexOf(i)
      if (k >= 0) this.slotFrame[k] = -1
      this.bitmaps.delete(i); this.release.push(b)
    }
    // a phone can't decode and upload full frames while falling without stuttering: it falls on the
    // small copies and sharpens the frame it comes to rest on
    const settled = !PHONE || !this.lowsOk || Math.abs(target - a) < 1.5
    for (let k = 0; settled && k <= AHEAD && this.decoding.size < DECODERS && this.bitmaps.size + this.decoding.size < MAX_DECODED; k++) {
      const i = a + dir * (k < 2 ? k : 1 + (k - 1) * stride)      // the next frame always, for the crossfade
      if (i < 0 || i >= n) break
      const blob = this.frames[i]
      if (!blob || this.bitmaps.has(i) || this.decoding.has(i)) continue
      this.decoding.add(i)
      createImageBitmap(blob, { ...BITMAP, ...FULL })
        .then((b) => { this.bitmaps.set(i, b) })
        .catch(() => {})
        .finally(() => this.decoding.delete(i))
    }
    // close() is slow-ish (a few ms each), so released frames are closed between frames
    if (this.release.length && !this.releasing) {
      this.releasing = true
      const idle = window.requestIdleCallback ?? ((f: () => void) => setTimeout(f, 50))
      idle(() => { this.releasing = false; this.release.splice(0, PHONE ? 8 : 4).forEach((b) => b.close()) })
    }
  }


  /** frame i into slot `which` (A or B): its full-size texture if decoded (uploading it if needed), else its layer of the small ones */
  private bind(i: number, which: 'A' | 'B') {
    const u = this.mat.uniforms, full = this.bitmaps.get(i)
    if (!full) { u['uLow' + which].value = i; return }
    const k = i & 1, t = this.slots[k]
    if (this.slotFrame[k] !== i) { t.image = full; t.needsUpdate = true; this.slotFrame[k] = i }
    u['tFrame' + which].value = t
    u['uLow' + which].value = -1
  }

  private updateFrames(prev: number) {
    const n = this.frames.length
    this.shown = Math.abs(this.target - this.shown) < 0.002 ? this.target : this.shown
    const a = Math.min(n - 1, Math.floor(this.shown)), b = Math.min(n - 1, a + 1)
    this.warm(a, this.target)
    // not decoded yet: hold the last frame in hand on this side rather than jump about
    const ia = this.pick(a, this.target >= this.shown ? 1 : -1), ib = ia === a && this.ready(b) ? b : ia
    if (ia >= 0) this.lastFrame = ia
    const u = this.mat.uniforms
    if (ia >= 0) { this.bind(ia, 'A'); this.bind(ib, 'B') }
    // short crossfade between neighbours: mostly one sharp frame, never a double image
    u.uFrameMix.value = ib === b && ia === a ? smooth(0.3, 0.7, this.shown - a) : 0
    // the still hands over to frame 0 within the first fraction of a frame
    u.uSeq.value = ia >= 0 ? smooth(0.0, 0.5, this.shown) : 0
    // impact: the floor fills the frame (the last few frames are all black) while falling
    if (this.impactArmed && this.shown >= n - 5 && this.target >= n - 1.01 && this.shown >= prev) {
      this.impactArmed = false
      this.onImpact()
    }
    if (!this.impactArmed && this.target < n - 8) this.impactArmed = true
  }

  private tick() {
    const dt = Math.max(1 / 240, Math.min(this.clock.getDelta(), 1 / 20))
    const u = this.mat.uniforms
    const t = (u.uTime.value += dt)
    if (this.introStart >= 0) u.uIntro.value = 1 - smooth(0, 1.8, t - this.introStart)
    // scrubbing inertia: the shown frame chases the scroll target
    const before = this.shown
    this.shown = damp(this.shown, this.target, 16, dt)
    if (this.frames.length) this.updateFrames(before)
    const still = 1 - smooth(0, 1.5, this.shown)
    this.parallax = damp(this.parallax, still, 12, dt)
    this.mouseDamped.set(damp(this.mouseDamped.x, this.mouse.x, 3.5, dt), damp(this.mouseDamped.y, this.mouse.y, 3.5, dt))
    u.uShift.value.set(this.mouseDamped.x * PARALLAX * this.parallax, this.mouseDamped.y * PARALLAX * this.parallax / ASPECT)
    u.uPointerOn.value = damp(u.uPointerOn.value, this.pointerIn && still > 0.5 ? 1 : 0, 4, dt)
    u.uRainAmt.value = 1.0 * (1 - smooth(0, (this.meta?.lip ?? 50) * 0.6, this.shown))

    if (still > 0.01) {
      // ripples: steady rain plus a wake behind the pointer (shader masks them to the slab)
      const R = this.ripple
      for (const d of R.drops) d.set(0, 0, 0, 0)
      for (let i = 0; i < 4; i++) R.drops[i].set(Math.random(), Math.random(), 0.0008 + Math.random() * 0.0008, 0.3)
      // now and then a fat drop lands: a wider ring, sometimes with a smaller one beside it
      this.splash += dt * (4 + Math.random() * 6)
      for (let i = 5; this.splash >= 1 && i < 15; i += 2) {
        this.splash -= 1
        const x = Math.random(), y = Math.random(), k = Math.random()
        R.drops[i].set(x, y, 0.0005 + k * 0.0006, 0.25 + k * 0.25)
        if (Math.random() < 0.3) R.drops[i + 1].set(x + (Math.random() - 0.5) * 0.0008, y + (Math.random() - 0.5) * 0.001, 0.0005, 0.2)
      }
      if (this.pointerIn && this.lastUv.x >= 0) {
        const speed = this.pointerUv.distanceTo(this.lastUv) / dt
        if (speed > 0.02) R.drops[4].set(this.pointerUv.x, this.pointerUv.y, 0.006, Math.min(0.6, speed * 0.6))
      }
      this.lastUv.copy(this.pointerUv)
      R.mat.uniforms.uPrev.value = R.b.texture
      this.renderer.setRenderTarget(R.a); this.renderer.render(R.scene, this.cam)
      this.renderer.setRenderTarget(null)
      ;[R.a, R.b] = [R.b, R.a]
      u.tRipple.value = R.b.texture
    }
    this.renderer.render(this.scene, this.cam)
  }

  /** the rain loop only plays while the stage is on screen */
  setActive(on: boolean) {
    if (on === this.active) return
    this.active = on
    const v = this.rainVideo
    if (v) { if (on) v.play().catch(() => {}); else v.pause() }
  }

  dispose() {
    cancelAnimationFrame(this.raf)
    for (const b of [...this.bitmaps.values(), ...this.release]) b.close()
    this.lowTex?.dispose()
    this.rainVideo?.pause()
    this.renderer.dispose()
  }
}
