// The big categories logs and projects are sorted into. Add, rename or reorder
// freely; an entry picks one with `category: <id>` in its front matter.
// Categories with no entries are hidden; entries without one land in MISC.

export interface Category { id: string; label: string; name: string }

export const categories: Category[] = [
  { id: 'ai', label: 'AI', name: 'AI / 机器学习' },
  { id: 'cg', label: 'CG', name: 'CG / 图形与渲染' },
  { id: 'dev', label: 'DEV', name: '工程 / 工具' },
]

export const MISC: Category = { id: 'misc', label: 'MISC', name: '其他' }

export const categoryOf = (id?: string) => categories.find((c) => c.id === id) ?? MISC
