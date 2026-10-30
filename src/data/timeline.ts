import { timeline, type TimelineEntry } from './profile'

export interface Year { year: number; id: string; items: TimelineEntry[] }

const yearOf = (t: TimelineEntry) => t.year ?? Number((t.when.match(/\d{4}/g) ?? ['0']).pop())

/** timeline entries by year, newest year first, entries in their written order */
export const years: Year[] = [...new Set(timeline.map(yearOf))].sort((a, b) => b - a)
  .map((year) => ({ year, id: `year-${year}`, items: timeline.filter((t) => yearOf(t) === year) }))
