// The big categories logs and projects are sorted into. Add, rename or reorder
// freely; an entry picks one with `category: <id>` in its front matter.
// Categories with no entries are hidden; entries without one land in MISC.
import type { L } from '../composables/prefs'

export interface Category { id: string; label: string; name: L }

export const categories: Category[] = [
  { id: 'ai', label: 'AI', name: { zh: 'AI / 机器学习', en: 'AI / Machine learning' } },
  { id: 'cg', label: 'CG', name: { zh: 'CG / 图形与渲染', en: 'CG / Graphics & rendering' } },
  { id: 'dev', label: 'DEV', name: { zh: '工程 / 工具', en: 'Engineering / Tools' } },
]

export const MISC: Category = { id: 'misc', label: 'MISC', name: { zh: '其他', en: 'Other' } }

export const categoryOf = (id?: string) => categories.find((c) => c.id === id) ?? MISC
