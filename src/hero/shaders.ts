// Hero compositing over Cycles pre-renders (see tools/blender/render_hero.py).
// slab.jpg is the full frame, canyon.jpg the same view without the slab;
// depth.png R = canyon camera distance (17..85 m -> 0..1), G = slab mask.
// Mouse parallax shifts each layer by 1/distance, like a small camera move.
// Scrolling crossfades into the fall sequence (frame 0 == the still) and
// blends neighbouring frames so scrubbing stays smooth. Fall frames carry
// alpha: the alley floor is a hole the page below shows through.

export const quadVert = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }
`

export const heroFrag = /* glsl */ `
  uniform sampler2D tSlab;
  uniform sampler2D tCanyon;
  uniform sampler2D tDepth;
  uniform sampler2D tRipple;
  uniform sampler2D tGlyph;
  uniform sampler2D tFrameA;
  uniform sampler2D tFrameB;
  uniform highp sampler2DArray tLow;   // every fall frame, small; layer uLowA / uLowB, or -1 for tFrameA / tFrameB
  uniform float uLowA;
  uniform float uLowB;
  uniform sampler2D tRain;
  uniform vec2 uRes;
  uniform float uImgAspect;
  uniform vec2 uShift;          // parallax at slab depth, image-uv units
  uniform vec2 uPointer;        // pointer in image uv
  uniform float uPointerOn;
  uniform vec2 uRippleTexel;
  uniform float uTime;
  uniform float uIntro;         // ASCII decode on load, 1 -> 0
  uniform float uCell;
  uniform float uGlyphs;
  uniform float uSeq;           // 0 = interactive still, 1 = fall sequence
  uniform float uFrameMix;
  uniform float uRainAmt;
  varying vec2 vUv;

  float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
  float distOf(float d) { return 17.0 + d * 68.0; }

  vec2 imageUv(vec2 suv) {
    float sa = uRes.x / uRes.y;
    vec2 s = sa > uImgAspect ? vec2(1.0, uImgAspect / sa) : vec2(sa / uImgAspect, 1.0);
    return (suv - 0.5) * s * 0.975 + 0.5;    // slight overscan so parallax never shows the border
  }

  vec3 still(vec2 iuv) {
    vec2 uvS = iuv - uShift;
    float mask = smoothstep(0.3, 0.7, texture2D(tDepth, uvS).g);
    vec2 uvC = iuv;    // canyon layer: fixed-point search so each pixel moves by its own depth
    for (int i = 0; i < 4; i++) uvC = iuv - uShift * 18.5 / distOf(texture2D(tDepth, uvC).r);
    vec3 canyon = texture2D(tCanyon, uvC).rgb;
    // rain ripples live only on the wet slab
    float hL = texture2D(tRipple, uvS - vec2(uRippleTexel.x, 0.0)).r;
    float hR = texture2D(tRipple, uvS + vec2(uRippleTexel.x, 0.0)).r;
    float hD = texture2D(tRipple, uvS - vec2(0.0, uRippleTexel.y)).r;
    float hU = texture2D(tRipple, uvS + vec2(0.0, uRippleTexel.y)).r;
    vec2 g = vec2(hR - hL, hU - hD);
    vec3 slab = texture2D(tSlab, uvS + g * 0.01).rgb;
    float spec = clamp(dot(normalize(vec3(-g * 14.0, 1.0)), normalize(vec3(-0.4, 0.5, 1.0))), 0.0, 1.0);
    slab += (pow(spec, 24.0) * 0.12 - length(g) * 0.3) * mask;
    return mix(canyon, slab, mask);
  }

  vec4 hero(vec2 iuv) {
    // Cycles rain loop (rendered over black, slab/buildings as holdouts); parts around the pointer
    vec2 dp = (iuv - uPointer) * vec2(uImgAspect, 1.0);
    float amt = uRainAmt * mix(1.0, smoothstep(0.03, 0.12, length(dp)), uPointerOn);
    vec3 rain = texture2D(tRain, iuv).rgb * amt;
    // drops are lenses, not paint: each streak bends what's behind it, then adds a little sheen
    const vec2 RT = vec2(1.5 / 1920.0, 1.5 / 1080.0);
    float r = dot(rain, vec3(0.333));
    float rx = dot(texture2D(tRain, iuv + vec2(RT.x, 0.0)).rgb, vec3(0.333)) * amt;
    float ry = dot(texture2D(tRain, iuv + vec2(0.0, RT.y)).rgb, vec3(0.333)) * amt;
    vec2 bend = vec2(rx - r, ry - r) * 0.012 + vec2(0.0, r * 0.003);
    vec4 col = vec4(uSeq < 1.0 ? still(iuv + bend) : vec3(0.0), 1.0);
    if (uSeq > 0.0) {
      vec4 fa = uLowA >= 0.0 ? texture(tLow, vec3(iuv, uLowA)) : texture2D(tFrameA, iuv);
      vec4 fb = uLowB >= 0.0 ? texture(tLow, vec3(iuv, uLowB)) : texture2D(tFrameB, iuv);
      vec4 f = mix(fa, fb, uFrameMix);
      col = mix(col, f, uSeq);
    }
    float lum = dot(col.rgb, vec3(0.299, 0.587, 0.114));
    col.rgb = col.rgb * (1.0 + r * 0.3) + rain * (1.0 - lum) * 0.6 - rain * lum * 0.15;
    return col;
  }

  void main() {
    vec2 iuv = imageUv(vUv);
    vec4 hc = hero(iuv);
    vec3 col = hc.rgb;
    if (uIntro > 0.0) {
      vec2 fc = gl_FragCoord.xy;
      vec2 cell = floor(fc / uCell);
      vec3 cs = hero(imageUv((cell + 0.5) * uCell / uRes)).rgb;
      float lum = dot(cs, vec3(0.299, 0.587, 0.114));
      vec2 local = fract(fc / uCell);
      float gi = floor(clamp(lum * 1.05 + hash(cell + floor(uTime * 6.0)) * 0.05, 0.0, 0.999) * uGlyphs);
      float gl = texture2D(tGlyph, vec2((gi + local.x) / uGlyphs, local.y)).r;
      col = mix(col, mix(cs * 0.7, cs * 1.1 + 0.03, gl), step(hash(cell) * 0.98 + 0.01, uIntro));
    }
    col += (hash(gl_FragCoord.xy + fract(uTime) * 91.0) - 0.5) * 0.02;   // fine film grain
    gl_FragColor = vec4(col * hc.a, hc.a);     // premultiplied for the transparent canvas
  }
`

export const rippleFrag = /* glsl */ `
  uniform sampler2D uPrev;
  uniform vec2 uTexel;
  uniform vec4 uDrops[16];       // uv, radius (uv units), strength
  uniform float uAspect;
  varying vec2 vUv;
  void main() {
    vec4 s = texture2D(uPrev, vUv);
    float n = texture2D(uPrev, vUv + vec2(uTexel.x, 0.0)).r + texture2D(uPrev, vUv - vec2(uTexel.x, 0.0)).r
            + texture2D(uPrev, vUv + vec2(0.0, uTexel.y)).r + texture2D(uPrev, vUv - vec2(0.0, uTexel.y)).r;
    float h = (n * 0.5 - s.g) * 0.95;     // strong damping: rings die out a short way from the drop
    for (int i = 0; i < 16; i++) {
      if (uDrops[i].z <= 0.0) continue;
      vec2 d = (vUv - uDrops[i].xy) * vec2(uAspect, 1.0);
      h += uDrops[i].w * (1.0 - smoothstep(0.0, uDrops[i].z, length(d)));
    }
    gl_FragColor = vec4(clamp(h, -4.0, 4.0), s.r, 0.0, 1.0);
  }
`
