import { ref, watch } from 'vue'

// The visitor's two switches: language (中 / EN) and the archive's night mode.
// Both are remembered per browser; night mode starts from the system setting.
// Night mode only re-colours the pages after the landing (the archive, posts);
// the hero keeps its rain-city look either way.

export type Lang = 'zh' | 'en'
export type Theme = 'light' | 'dark'

/** a string (or anything) given in both languages, or one value for both */
export type L<T = string> = T | { zh: T; en: T }

function load<T extends string>(key: string, ok: readonly T[], fallback: T): T {
  try {
    const v = localStorage.getItem(key) as T | null
    if (v && ok.includes(v)) return v
  } catch { /* storage blocked: use the default */ }
  return fallback
}
function save(key: string, v: string) {
  try { localStorage.setItem(key, v) } catch { /* storage blocked: not remembered */ }
}

const systemDark = typeof matchMedia === 'function' && matchMedia('(prefers-color-scheme: dark)').matches
const systemLang: Lang = typeof navigator !== 'undefined' && !/^zh/i.test(navigator.language) ? 'en' : 'zh'

export const lang = ref<Lang>(load('lang', ['zh', 'en'] as const, systemLang))
export const theme = ref<Theme>(load('theme', ['light', 'dark'] as const, systemDark ? 'dark' : 'light'))

function apply() {
  const html = document.documentElement
  html.lang = lang.value === 'zh' ? 'zh-CN' : 'en'
  html.dataset.theme = theme.value
}
apply()
watch(lang, (v) => { save('lang', v); apply() })
watch(theme, (v) => { save('theme', v); apply() })

const isPair = <T>(v: L<T>): v is { zh: T; en: T } => typeof v === 'object' && v !== null && 'zh' in v && 'en' in v

/** pick the current language's value */
export function tr<T>(v: L<T>): T {
  return isPair(v) ? v[lang.value] : v
}
