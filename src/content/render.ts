import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import typescript from 'highlight.js/lib/languages/typescript'
import javascript from 'highlight.js/lib/languages/javascript'
import glsl from 'highlight.js/lib/languages/glsl'
import bash from 'highlight.js/lib/languages/bash'
import cpp from 'highlight.js/lib/languages/cpp'
import json from 'highlight.js/lib/languages/json'
import yaml from 'highlight.js/lib/languages/yaml'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'

// Markdown -> HTML for the article page. Headings get ids for the table of
// contents; code fences become terminal panels; images become captioned
// figures (the alt text is the caption). Relative image paths resolve under public/.
for (const [name, lang] of Object.entries({ python, typescript, javascript, glsl, bash, cpp, json, yaml, xml, css })) hljs.registerLanguage(name, lang)
hljs.registerAliases(['py'], { languageName: 'python' })
hljs.registerAliases(['ts', 'vue'], { languageName: 'typescript' })
hljs.registerAliases(['js'], { languageName: 'javascript' })
hljs.registerAliases(['sh', 'shell', 'powershell'], { languageName: 'bash' })
hljs.registerAliases(['html'], { languageName: 'xml' })

export interface Heading { id: string; text: string; level: number }

const BASE = import.meta.env.BASE_URL
const md = new MarkdownIt({ html: true, linkify: true, typographer: true })

const slugify = (s: string) => s.toLowerCase().trim().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'section'

md.renderer.rules.fence = (tokens, i) => {
  const t = tokens[i]
  const lang = t.info.trim().split(/\s+/)[0] || 'text'
  const code = hljs.getLanguage(lang) ? hljs.highlight(t.content, { language: lang }).value : md.utils.escapeHtml(t.content)
  const lines = t.content.replace(/\n$/, '').split('\n').length
  return `<figure class="code"><figcaption><span>&gt; ${md.utils.escapeHtml(lang)}</span><span>${lines} LN</span>`
    + `<button type="button" class="copy" data-copy>COPY</button></figcaption><pre><code>${code}</code></pre></figure>`
}

// ![caption](url) also takes videos: a .mp4/.webm/.mov file plays inline,
// a YouTube / Bilibili / Vimeo page link becomes an embedded player
const EMBEDS: [RegExp, (m: RegExpMatchArray) => string][] = [
  [/youtu(?:\.be\/|be\.com\/(?:watch\?v=|embed\/|shorts\/))([\w-]{11})/, (m) => `https://www.youtube-nocookie.com/embed/${m[1]}`],
  [/bilibili\.com\/video\/(BV\w+)/, (m) => `https://player.bilibili.com/player.html?bvid=${m[1]}&autoplay=0&high_quality=1`],
  [/vimeo\.com\/(\d+)/, (m) => `https://player.vimeo.com/video/${m[1]}`],
]

md.renderer.rules.image = (tokens, i) => {
  const t = tokens[i]
  let src = String(t.attrGet('src') ?? '')
  const alt = md.utils.escapeHtml(t.content)
  const cap = alt ? `<span class="cap">${alt}</span>` : ''
  for (const [re, url] of EMBEDS) {
    const m = src.match(re)
    if (m) return `<span class="fig embed"><span class="frame"><iframe src="${md.utils.escapeHtml(url(m))}" title="${alt}" loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></span>${cap}</span>`
  }
  if (!/^(https?:|\/|data:)/.test(src)) src = BASE + src
  const s = md.utils.escapeHtml(src)
  if (/\.(mp4|webm|mov|m4v)(\?|#|$)/i.test(src)) {
    return `<span class="fig video"><video src="${s}" controls playsinline muted loop preload="metadata"></video>${cap}</span>`
  }
  return `<span class="fig"><img src="${s}" alt="${alt}" loading="lazy">${cap}</span>`
}

// links out of the site open in a new tab (the stylesheet marks them ↗)
const linkOpen = md.renderer.rules.link_open ?? ((tokens, i, o, _e, self) => self.renderToken(tokens, i, o))
md.renderer.rules.link_open = (tokens, i, o, e, self) => {
  const href = String(tokens[i].attrGet('href') ?? '')
  if (/^https?:/.test(href)) {
    tokens[i].attrSet('target', '_blank')
    tokens[i].attrSet('rel', 'noopener')
  } else if (/^\/(?!\/)/.test(href)) {
    // a page of this site: the real URL carries the base path, the app routes by data-route
    tokens[i].attrSet('href', BASE + href.slice(1))
    tokens[i].attrSet('data-route', href)
  }
  return linkOpen(tokens, i, o, e, self)
}

md.renderer.rules.table_open = () => '<div class="table"><table>'
md.renderer.rules.table_close = () => '</table></div>'

export function render(src: string): { html: string; headings: Heading[] } {
  const tokens = md.parse(src, {})
  const headings: Heading[] = []
  const seen = new Map<string, number>()
  tokens.forEach((t, i) => {
    if (t.type !== 'heading_open') return
    const text = tokens[i + 1].content
    let id = slugify(text)
    const n = seen.get(id) ?? 0
    seen.set(id, n + 1)
    if (n) id += `-${n}`
    t.attrSet('id', id)
    const level = Number(t.tag.slice(1))
    if (level <= 3) headings.push({ id, text, level })
  })
  return { html: md.renderer.render(tokens, md.options, {}), headings }
}
