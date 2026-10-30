// Logs (articles, skill write-ups) and projects: one Markdown file per entry,
// in src/content/log and src/content/projects. The file name is the URL slug
// (/log/<slug>, /projects/<slug>). Front matter, between --- lines:
//
//   title:    the headline
//   date:     2026-10-30
//   category: cg                     (an id from src/data/categories.ts)
//   tags:     blender, webgl         (comma separated)
//   summary:  one or two lines for the index and the header
//   draft:    true                   (optional: listed in dev only)
// logs only:
//   kind:     skill | note           (skill = the long version of an archive file)
//   dossier:  FILE-03                (optional: the archive file that opens this post)
// projects only:
//   status:   active | shipped | archived
//   repo:     https://github.com/you/name   (its name also pulls stars from repos.json)
//   demo:     https://...
//   cover:    images/cover.jpg       (under public/, shown on the card)
//
// English: put the translation beside it as <slug>.en.md (same front matter,
// translated title / summary / tags / body). Without one, the Chinese file is
// shown in English mode too, and the other way round.

import { reactive, watch } from 'vue'
import repos from './repos.json'
import { categories, categoryOf, type Category } from './categories'
import { lang, type Lang } from '../composables/prefs'

export type Collection = 'log' | 'projects'

export interface Entry {
  collection: Collection
  slug: string
  code: string            // LOG-001 / PRJ-001 ... in date order
  title: string
  date: string
  category: Category
  tags: string[]
  summary: string
  body: string            // Markdown, front matter stripped
  minutes: number         // reading time
  draft: boolean
  kind: 'skill' | 'note' | 'project'
  dossier?: string
  status?: string
  repo?: string
  demo?: string
  cover?: string
  stars?: number
  language?: string
}

const files: Record<Collection, Record<string, string>> = {
  log: import.meta.glob('../content/log/*.md', { query: '?raw', import: 'default', eager: true }),
  projects: import.meta.glob('../content/projects/*.md', { query: '?raw', import: 'default', eager: true }),
}

function parse(collection: Collection, path: string, raw: string): Omit<Entry, 'code'> {
  const slug = path.split('/').pop()!.replace(/(\.en)?\.md$/, '')
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/)
  const meta: Record<string, string> = {}
  for (const line of (m?.[1] ?? '').split(/\r?\n/)) {
    const i = line.indexOf(':')
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^["']|["']$/g, '')
  }
  const body = m ? raw.slice(m[0].length) : raw
  // CJK reads by character, Latin by word
  const cjk = (body.match(/[㐀-鿿]/g) ?? []).length
  const words = body.replace(/[㐀-鿿]/g, ' ').split(/\s+/).filter(Boolean).length
  const repoName = meta.repo?.replace(/\/$/, '').split('/').pop()
  const gh = repos.find((r) => r.name === repoName)
  return {
    collection, slug, body,
    title: meta.title ?? slug,
    date: meta.date ?? '',
    category: categoryOf(meta.category),
    tags: (meta.tags ?? '').split(',').map((t) => t.trim()).filter(Boolean),
    summary: meta.summary ?? '',
    minutes: Math.max(1, Math.round(cjk / 400 + words / 220)),
    draft: meta.draft === 'true',
    kind: collection === 'projects' ? 'project' : meta.kind === 'skill' ? 'skill' : 'note',
    dossier: meta.dossier || undefined,
    status: meta.status || undefined,
    repo: meta.repo || undefined,
    demo: meta.demo || undefined,
    cover: meta.cover || undefined,
    stars: gh?.stars,
    language: gh?.language,
  }
}

/** one Entry per slug, in the given language where a translation exists */
function load(collection: Collection, prefix: string, l: Lang): Entry[] {
  const bySlug = new Map<string, { zh?: Omit<Entry, 'code'>; en?: Omit<Entry, 'code'> }>()
  for (const [p, raw] of Object.entries(files[collection])) {
    const e = parse(collection, p, raw)
    const v = bySlug.get(e.slug) ?? {}
    v[/\.en\.md$/.test(p) ? 'en' : 'zh'] = e
    bySlug.set(e.slug, v)
  }
  return [...bySlug.values()].map((v) => (v[l] ?? v.zh ?? v.en)!)
    .filter((e) => import.meta.env.DEV || !e.draft)
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((e, i) => ({ ...e, code: `${prefix}-${String(i + 1).padStart(3, '0')}` }))
    .reverse()                                     // oldest gets 001; listed newest first
}

// reactive and refilled in place when the language changes, so every list re-renders
export const entries = reactive<Record<Collection, Entry[]>>({ log: [], projects: [] })
function fill(l: Lang) {
  entries.log.splice(0, entries.log.length, ...load('log', 'LOG', l))
  entries.projects.splice(0, entries.projects.length, ...load('projects', 'PRJ', l))
}
fill(lang.value)
watch(lang, fill)
export const posts = entries.log

export const entryBy = (c: Collection, slug: string) => entries[c].find((e) => e.slug === slug)
export const postForDossier = (code: string) => posts.find((p) => p.dossier === code)
export const pathOf = (e: Entry) => `/${e.collection}/${e.slug}`

/** the categories that have entries in a collection, in the configured order, with counts */
export function categoriesIn(c: Collection) {
  const seen = new Map<string, { category: Category; items: Entry[] }>()
  for (const e of entries[c]) {
    const g = seen.get(e.category.id) ?? { category: e.category, items: [] }
    g.items.push(e)
    seen.set(e.category.id, g)
  }
  const rank = (id: string) => { const i = categories.findIndex((x) => x.id === id); return i < 0 ? 1e3 : i }
  return [...seen.values()].sort((a, b) => rank(a.category.id) - rank(b.category.id))
}
