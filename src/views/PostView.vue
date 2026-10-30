<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { entries, entryBy, pathOf, type Collection } from '../data/posts'
import { filters } from '../composables/filters'
import { dossiers, profile } from '../data/profile'
import { art } from '../data/asciiArt'
import { render } from '../content/render'
import { scramble } from '../composables/scramble'
import { toSection } from '../composables/navigate'
import { lenis } from '../composables/useLenis'
import ScrambleText from '../components/ScrambleText.vue'
import AsciiField from '../components/AsciiField.vue'
import SiteFooter from '../components/SiteFooter.vue'

// A post, opened like a file pulled from the archive: a dark header (the
// city's palette) with the file's ASCII plate and HUD readouts, a dithered
// strip of characters down into the paper-coloured reading page, an index
// that tracks the reading position, and the neighbouring files at the end.
// Logs and projects share it; a project adds its status and links.
const BASE = import.meta.env.BASE_URL
const route = useRoute()
const router = useRouter()
const collection = computed(() => (route.meta.collection as Collection) ?? 'log')
const list = computed(() => entries[collection.value])
const section = computed(() => (collection.value === 'projects' ? 'PROJECTS' : 'LOG'))
const post = computed(() => entryBy(collection.value, String(route.params.slug)))
const doc = computed(() => (post.value ? render(post.value.body) : { html: '', headings: [] }))
const dossier = computed(() => dossiers.find((d) => d.code === post.value?.dossier))
const kind = computed(() => ({ skill: 'SKILL FILE', note: 'FIELD NOTE', project: 'PROJECT' })[post.value?.kind ?? 'note'])
const i = computed(() => list.value.findIndex((p) => p.slug === post.value?.slug))
const newer = computed(() => list.value[i.value - 1])
const older = computed(() => list.value[i.value + 1])
const host = (u: string) => u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')

const article = ref<HTMLElement>()
const plate = ref('')
const activeId = ref('')
const progress = ref(0)
const showTop = ref(false)
let raf = 0, cancelPlate = () => {}

// the strip between the dark header and the page: dense blocks thinning to nothing
const DITHER = '█▓▒░·  '
const dither = Array.from({ length: 7 }, (_, r) =>
  Array.from({ length: 420 }, () => {
    const k = Math.min(DITHER.length - 1, Math.max(0, Math.floor(r + (Math.random() - 0.35) * 2.2)))
    return DITHER[k]
  }).join(''),
).join('\n')

const bar = computed(() => {
  const n = Math.round(progress.value * 14)
  return '█'.repeat(n) + '░'.repeat(14 - n)
})
const pad = (n: number) => String(n).padStart(2, '0')

function track() {
  raf = requestAnimationFrame(track)
  const el = article.value
  if (!el) return
  const r = el.getBoundingClientRect()
  showTop.value = scrollY > innerHeight * 0.9
  progress.value = Math.min(1, Math.max(0, (innerHeight * 0.35 - r.top) / Math.max(1, r.height - innerHeight * 0.3)))
  let id = ''
  for (const h of doc.value.headings) {
    const t = document.getElementById(h.id)
    if (t && t.getBoundingClientRect().top < innerHeight * 0.3) id = h.id
  }
  activeId.value = id
}

function jump(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  if (lenis.value) lenis.value.scrollTo(el, { offset: -90, duration: 1.2 })
  else el.scrollIntoView({ behavior: 'smooth' })
}

function toTop() {
  if (lenis.value) lenis.value.scrollTo(0, { duration: 1.6 })
  else window.scrollTo({ top: 0, behavior: 'smooth' })
}

/** back to this entry's index on the home page, showing its category */
function backToIndex() {
  if (post.value) filters[collection.value] = post.value.category.id
  toSection(collection.value)
}

function onArticleClick(e: MouseEvent) {
  // links to other pages of this site stay in the app (and get the cut)
  const a = (e.target as HTMLElement).closest<HTMLAnchorElement>('a[data-route]')
  if (a && !e.metaKey && !e.ctrlKey) { e.preventDefault(); router.push(a.dataset.route!); return }
  const b = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-copy]')
  if (!b) return
  const code = b.closest('figure')?.querySelector('code')?.textContent ?? ''
  navigator.clipboard?.writeText(code).then(() => {
    b.textContent = 'COPIED'
    setTimeout(() => (b.textContent = 'COPY'), 1400)
  }).catch(() => {})
}

onMounted(async () => {
  if (post.value) document.title = `${post.value.title} — ${post.value.code}`
  const src = art[dossier.value?.art ?? 'tower'] ?? ''
  cancelPlate = scramble(src, (s) => (plate.value = s), 1600)
  await nextTick()
  // article headings feed the HUD scrollbar's ticks
  article.value?.querySelectorAll('h2').forEach((h, n) => { h.dataset.hudMark = `${pad(n + 1)} ${h.textContent ?? ''}`.slice(0, 22).toUpperCase() })
  raf = requestAnimationFrame(track)
})
onBeforeUnmount(() => { cancelAnimationFrame(raf); cancelPlate(); document.title = `${profile.name} — Archive` })
</script>

<template>
  <div v-if="post" class="post" :data-page="collection">
    <header class="head" data-nav-dark>
      <div class="scan" aria-hidden="true" />
      <pre class="plate" aria-hidden="true">{{ plate }}</pre>
      <div class="inner">
        <p class="crumbs mono">
          <a :href="BASE" @click.prevent="toSection(collection)">◀ ARCHIVE</a>
          <span>/</span><span>{{ section }}</span><span>/</span><span>{{ post.category.label }}</span><span>/</span><span class="cur">{{ post.code }}</span>
          <span class="rule" aria-hidden="true" />
          <span class="rec">● OPEN</span>
        </p>
        <p class="label kind">{{ kind }} · {{ post.category.name }} · {{ post.code }}<template v-if="dossier"> · source {{ dossier.code }}</template></p>
        <ScrambleText :text="post.title" as="h1" trigger="mount" :duration="1400" :delay="250" class="title" />
        <p class="summary">{{ post.summary }}</p>
        <dl class="meta mono">
          <div><dt>DATE</dt><dd>{{ post.date }}</dd></div>
          <div v-if="post.status"><dt>STATUS</dt><dd class="status">● {{ post.status.toUpperCase() }}</dd></div>
          <div><dt>READ</dt><dd>{{ pad(post.minutes) }} MIN</dd></div>
          <div><dt>SECTIONS</dt><dd>{{ pad(doc.headings.filter((h) => h.level === 2).length) }}</dd></div>
          <div v-if="dossier"><dt>FILE</dt><dd>{{ dossier.code }} ── {{ dossier.title }}</dd></div>
          <div v-if="post.stars !== undefined"><dt>STARS</dt><dd>★ {{ post.stars }}</dd></div>
          <div class="tags"><dt>TAGS</dt><dd><span v-for="t in post.tags" :key="t">#{{ t }}</span></dd></div>
        </dl>
        <p v-if="post.repo || post.demo" class="links mono">
          <a v-if="post.repo" :href="post.repo" target="_blank" rel="noopener">[ SOURCE ── {{ host(post.repo) }} ↗ ]</a>
          <a v-if="post.demo" :href="post.demo" target="_blank" rel="noopener">[ VIEW ── {{ host(post.demo) }} ↗ ]</a>
        </p>
      </div>
      <pre class="dither" aria-hidden="true">{{ dither }}</pre>
    </header>

    <main class="page theme-light">
      <AsciiField />
      <div class="layout">
        <aside class="toc mono" aria-label="Contents">
          <p class="toc-head">┌─ INDEX</p>
          <ol>
            <li v-for="(h, n) in doc.headings" :key="h.id" :class="[`l${h.level}`, { on: activeId === h.id }]">
              <a :href="`#${h.id}`" @click.prevent="jump(h.id)">
                <span class="n">{{ h.level === 2 ? pad(doc.headings.slice(0, n + 1).filter((x) => x.level === 2).length) : '··' }}</span>{{ h.text }}
              </a>
            </li>
          </ol>
          <p class="toc-foot">└─ [{{ bar }}] {{ String(Math.round(progress * 100)).padStart(3, '0') }}%</p>
        </aside>

        <!-- eslint-disable-next-line vue/no-v-html -->
        <article ref="article" class="prose" @click="onArticleClick" v-html="doc.html" />
      </div>

      <nav class="adjacent" aria-label="More files">
        <RouterLink v-if="older" :to="pathOf(older)" class="adj prev" data-cursor="open">
          <span class="label">◀ PREVIOUS · {{ older.code }}</span><span class="t">{{ older.title }}</span>
        </RouterLink>
        <span v-else class="adj none mono">── START OF {{ section }}</span>
        <RouterLink v-if="newer" :to="pathOf(newer)" class="adj next" data-cursor="open">
          <span class="label">NEXT · {{ newer.code }} ▶</span><span class="t">{{ newer.title }}</span>
        </RouterLink>
        <span v-else class="adj none mono r">END OF {{ section }} ──</span>
      </nav>
      <p class="back mono"><a :href="BASE" @click.prevent="backToIndex">[ ◀ RETURN TO ARCHIVE ]</a></p>
      <SiteFooter />
    </main>

    <button type="button" class="to-top mono" :class="{ on: showTop }" aria-label="Back to top" data-cursor="button" @click="toTop">
      <span class="bk" aria-hidden="true">┌</span>
      <span class="ar" aria-hidden="true">▲</span>
      <span class="lb">TOP</span>
      <span class="pc">{{ String(Math.round(progress * 100)).padStart(3, '0') }}</span>
      <span class="bk br" aria-hidden="true">┘</span>
    </button>
  </div>

  <div v-else class="missing theme-light" :data-page="collection">
    <pre class="mono" aria-hidden="true">┌──────────────────────────┐
│  FILE NOT FOUND  ░▒▓ 404  │
└──────────────────────────┘</pre>
    <p class="mono"><a :href="BASE" @click.prevent="toSection(collection)">[ ◀ RETURN TO ARCHIVE ]</a></p>
  </div>
</template>

<style scoped>
/* ── header: the city's dark palette ─────────────────────────── */
.head { position: relative; overflow: hidden; background: radial-gradient(120% 90% at 70% 10%, #1b2126, var(--graphite) 70%); color: var(--mist); }
.scan { position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(255, 255, 255, 0.025) 0 1px, transparent 1px 3px); }
.plate { position: absolute; right: var(--gutter); top: 50%; transform: translateY(-58%); margin: 0; font: 12px/1.15 var(--font-mono); color: rgba(111, 138, 143, 0.32); pointer-events: none; }
.inner { position: relative; max-width: 1360px; margin: 0 auto; padding: clamp(110px, 18vh, 180px) var(--gutter) 56px; }
.crumbs { display: flex; align-items: center; gap: 10px; font-size: 11px; letter-spacing: 0.16em; color: var(--fog-dim); margin: 0 0 56px; }
.crumbs a { color: var(--fog); transition: color 0.2s; } .crumbs a:hover { color: var(--mist); }
.crumbs .cur { color: var(--accent); }
.crumbs .rule { flex: 1; height: 1px; background: repeating-linear-gradient(90deg, var(--line) 0 6px, transparent 6px 9px); }
.rec { color: var(--sodium); animation: blink 1.6s steps(2) infinite; }
@keyframes blink { 50% { opacity: 0.35; } }
.kind { color: var(--accent); }
.meta .status { color: var(--sodium); }
.links { display: flex; flex-wrap: wrap; gap: 18px; margin: 26px 0 0; font-size: 11px; letter-spacing: 0.14em; }
.links a { color: var(--accent); transition: color 0.2s; } .links a:hover { color: var(--mist); }

/* back to top: a bracketed HUD tab, bottom right, after the first screen */
.to-top {
  position: fixed; right: calc(var(--gutter) + 18px); bottom: 32px; z-index: 40; display: grid; justify-items: center; gap: 2px;
  padding: 12px 12px 10px; min-width: 54px; background: rgba(227, 230, 231, 0.86); backdrop-filter: blur(6px);
  border: 1px solid #bec5c8; color: #4d6a70; font-size: 10px; letter-spacing: 0.18em; cursor: pointer;
  opacity: 0; transform: translateY(14px); pointer-events: none; transition: opacity 0.4s, transform 0.5s var(--ease-out), background 0.3s, color 0.3s;
}
.to-top.on { opacity: 1; transform: none; pointer-events: auto; }
.to-top:hover { background: #4d6a70; color: #e3e6e7; }
.to-top .ar { font-size: 12px; transition: transform 0.4s var(--ease-out); }
.to-top:hover .ar { transform: translateY(-3px); }
.to-top .pc { color: #7b858a; font-size: 9px; letter-spacing: 0.1em; }
.to-top:hover .pc { color: inherit; }
.to-top .bk { position: absolute; font-size: 12px; line-height: 1; color: #4d6a70; }
.to-top .bk { left: -5px; top: -6px; } .to-top .bk.br { left: auto; top: auto; right: -5px; bottom: -6px; }
.title { margin: 14px 0 22px; max-width: 18em; font: 300 clamp(34px, 5.4vw, 72px)/1.08 var(--font-sans); letter-spacing: -0.01em; color: #dfe3e4; }
.summary { max-width: 46em; margin: 0 0 44px; color: var(--fog); font-size: 16px; }
.meta { display: flex; flex-wrap: wrap; margin: 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); max-width: 980px; }
.meta div { padding: 14px 28px 14px 0; margin-right: 28px; border-right: 1px dashed var(--line); }
.meta div:last-child { border-right: 0; }
.meta dt { font-size: 10px; letter-spacing: 0.2em; color: var(--fog-dim); margin-bottom: 4px; }
.meta dd { margin: 0; font-size: 12px; letter-spacing: 0.06em; color: var(--mist); }
.meta .tags dd { display: flex; gap: 10px; flex-wrap: wrap; color: var(--accent); }
.dither { position: relative; margin: 0; font: 12px/0.84 var(--font-mono); color: var(--graphite); background: var(--paper); white-space: pre; overflow: hidden; }

/* ── reading page ─────────────────────────────────────────── */
.page { position: relative; background: var(--paper); }
.layout { position: relative; z-index: 1; display: grid; grid-template-columns: 240px minmax(0, 720px); gap: clamp(32px, 6vw, 96px); max-width: 1360px; margin: 0 auto; padding: 72px var(--gutter) 0; }
.toc { position: sticky; top: 96px; align-self: start; font-size: 11px; color: var(--fog-dim); }
.toc-head, .toc-foot { margin: 0; color: var(--accent-dim); letter-spacing: 0.12em; white-space: nowrap; }
.toc ol { list-style: none; margin: 10px 0 12px; padding: 0 0 0 12px; border-left: 1px solid var(--line); }
.toc li { line-height: 1.5; padding: 5px 0; }
.toc li.l3 { padding-left: 14px; font-size: 10.5px; }
.toc a { display: flex; gap: 10px; color: var(--fog-dim); transition: color 0.25s, transform 0.4s var(--ease-out); }
.toc a:hover { color: var(--mist); }
.toc .n { flex: 0 0 auto; color: var(--accent-dim); }
.toc li.on a { color: var(--mist); transform: translateX(4px); }
.toc li.on .n { color: var(--accent); }

.adjacent { position: relative; z-index: 1; display: grid; grid-template-columns: 1fr 1fr; max-width: 1360px; margin: 120px auto 0; padding: 0 var(--gutter); }
.adj { display: flex; flex-direction: column; gap: 10px; padding: 28px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); color: var(--fog); transition: color 0.3s; }
.adj.next, .adj.r { text-align: right; align-items: flex-end; border-left: 1px dashed var(--line); }
.adj.prev, .adj.none:not(.r) { padding-right: 24px; } .adj.next, .adj.r { padding-left: 24px; }
.adj .t { font: 300 22px/1.3 var(--font-sans); color: var(--mist); }
.adj:hover { color: var(--mist); }
.adj.none { font-size: 11px; letter-spacing: 0.16em; color: var(--fog-dim); justify-content: center; }
.back { position: relative; z-index: 1; text-align: center; margin: 56px 0 0; font-size: 11px; letter-spacing: 0.18em; color: var(--accent); }

.missing { min-height: 100vh; display: grid; place-content: center; text-align: center; background: var(--paper); color: var(--fog); }
.missing pre { color: var(--accent); }

@media (max-width: 960px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  .toc { position: static; }
  .plate { opacity: 0.45; right: -40px; }
}
@media (max-width: 640px) {
  .adjacent { grid-template-columns: 1fr; }
  .adj.next, .adj.r { border-left: 0; padding-left: 0; }
  .meta div { border-right: 0; margin-right: 0; padding-right: 24px; }
}
</style>

<style>
/* ── article typography (v-html content, so unscoped under .prose) ── */
.prose { counter-reset: h2 fig; color: #3a4347; font-size: 16.5px; line-height: 1.85; }
.prose > :first-child { margin-top: 0; }
.prose p { margin: 0 0 1.25em; }
.prose a { color: var(--accent); border-bottom: 1px dashed var(--accent-dim); }
.prose a:hover { color: var(--mist); }
.prose a[target='_blank']::after { content: ' ↗'; font-size: 0.8em; color: var(--accent-dim); }
.prose .fig video { display: block; width: 100%; height: auto; background: #0d1013; }
.prose .fig.embed .frame { position: relative; display: block; aspect-ratio: 16 / 9; background: #0d1013; }
.prose .fig.embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.prose strong { color: var(--mist); font-weight: 500; }
.prose h2, .prose h3 { scroll-margin-top: 96px; color: var(--mist); font-weight: 300; }
.prose h2 { counter-increment: h2; margin: 2.6em 0 0.9em; padding-top: 1.1em; font-size: 30px; line-height: 1.25; border-top: 1px solid var(--line); }
.prose h2::before { content: '── ' counter(h2, decimal-leading-zero) ' ─'; display: block; margin-bottom: 10px; font: 500 11px/1 var(--font-mono); letter-spacing: 0.2em; color: var(--accent); }
.prose h3 { margin: 2em 0 0.6em; font-size: 21px; }
.prose h3::before { content: '▪ '; color: var(--accent-dim); }
.prose ul, .prose ol { margin: 0 0 1.4em; padding-left: 1.4em; }
.prose ul { list-style: none; padding-left: 1.6em; }
.prose ul > li { position: relative; }
.prose ul > li::before { content: '─'; position: absolute; left: -1.5em; color: var(--accent); font-family: var(--font-mono); }
.prose li { margin: 0.35em 0; }
.prose ol > li::marker { font: 500 12px var(--font-mono); color: var(--accent); }
.prose hr { border: 0; margin: 3em 0; height: 1px; background: repeating-linear-gradient(90deg, var(--line) 0 6px, transparent 6px 10px); }

.prose blockquote { position: relative; margin: 2em 0; padding: 18px 24px 18px 26px; background: rgba(77, 106, 112, 0.07); border-left: 2px solid var(--accent); color: var(--mist); font-size: 18px; line-height: 1.7; }
.prose blockquote::before { content: 'NOTE ──'; display: block; margin-bottom: 8px; font: 500 10px/1 var(--font-mono); letter-spacing: 0.22em; color: var(--accent); }
.prose blockquote p:last-child { margin: 0; }

.prose :not(pre) > code { padding: 0.12em 0.4em; font: 0.86em var(--font-mono); background: rgba(46, 54, 61, 0.08); border: 1px solid var(--line); color: var(--mist); }

.prose .code { margin: 2em 0; background: #111619; border: 1px solid #222a30; color: #c3cacd; box-shadow: 0 18px 40px -24px rgba(13, 16, 19, 0.6); }
.prose .code figcaption { display: flex; gap: 16px; align-items: center; padding: 9px 14px; border-bottom: 1px dashed #2e363d; font: 500 10px/1 var(--font-mono); letter-spacing: 0.18em; color: #5d666c; text-transform: uppercase; }
.prose .code figcaption span:first-child { color: #6f8a8f; }
.prose .code .copy { margin-left: auto; font: inherit; letter-spacing: inherit; color: #8a9399; padding: 3px 8px; border: 1px solid #2e363d; transition: color 0.2s, border-color 0.2s; }
.prose .code .copy:hover { color: #dfe3e4; border-color: #6f8a8f; }
.prose .code pre { margin: 0; padding: 18px 20px; overflow-x: auto; font: 13px/1.7 var(--font-mono); }
.prose .code code { font: inherit; }
.hljs-keyword, .hljs-built_in, .hljs-type, .hljs-selector-tag { color: #8fb0b5; }
.hljs-string, .hljs-regexp, .hljs-attr { color: #b39b74; }
.hljs-comment, .hljs-quote, .hljs-meta { color: #5d666c; font-style: italic; }
.hljs-number, .hljs-literal, .hljs-symbol { color: #a7b49c; }
.hljs-title, .hljs-function .hljs-title, .hljs-title.function_ { color: #dfe3e4; }
.hljs-params, .hljs-variable { color: #b9bfc2; }

.prose .fig { counter-increment: fig; position: relative; display: block; margin: 2.4em 0; padding: 10px; border: 1px solid var(--line); background: #dde1e2; }
.prose .fig::before, .prose .fig::after { content: ''; position: absolute; width: 14px; height: 14px; border: 1px solid var(--accent); pointer-events: none; }
.prose .fig::before { top: -4px; left: -4px; border-right: 0; border-bottom: 0; }
.prose .fig::after { bottom: -4px; right: -4px; border-left: 0; border-top: 0; }
.prose .fig img { display: block; width: 100%; height: auto; filter: saturate(0.7); }
.prose .fig .cap { display: block; padding: 10px 2px 0; font: 11px/1.5 var(--font-mono); letter-spacing: 0.08em; color: var(--fog-dim); }
.prose .fig .cap::before { content: 'FIG.' counter(fig, decimal-leading-zero) ' ── '; color: var(--accent); }
.prose .fig.video .cap::before, .prose .fig.embed .cap::before { content: 'REC.' counter(fig, decimal-leading-zero) ' ── '; }

.prose .table { margin: 2em 0; overflow-x: auto; }
.prose table { width: 100%; border-collapse: collapse; font: 12.5px/1.6 var(--font-mono); }
.prose th { text-align: left; font-weight: 500; font-size: 10.5px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--fog-dim); padding: 10px 14px 10px 0; border-bottom: 1px solid var(--mist); }
.prose td { padding: 10px 14px 10px 0; border-bottom: 1px dashed var(--line); color: var(--fog); }
.prose td:first-child { color: var(--mist); }
</style>
