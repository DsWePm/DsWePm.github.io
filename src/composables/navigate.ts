import { nextTick } from 'vue'
import { router } from '../router'
import { asciiCut } from './useAsciiCut'
import { lenis, scrollToId } from './useLenis'

// Page changes cut through black like the landing: the cut paints black before
// the next paint, the route swaps underneath, then the black pours away in
// characters. Each page remembers where it was left (browser back included).
const saved = new Map<string, number>()
let pendingSection: string | null = null

function scrollNow(to: number | HTMLElement) {
  // absolute position from the DOM: right after a page swap Lenis's own scroll value is stale
  const y = typeof to === 'number' ? to : to.getBoundingClientRect().top + scrollY - 24
  if (lenis.value) lenis.value.scrollTo(y, { immediate: true, force: true })
  else window.scrollTo(0, y)
}

export function installPageCuts() {
  router.beforeEach((_to, from) => { if (from.matched.length) saved.set(from.fullPath, scrollY) })
  router.afterEach(async (to, from, failure) => {
    if (failure || !from.matched.length || to.fullPath === from.fullPath) return
    asciiCut.play()
    const id = pendingSection
    pendingSection = null
    // positions are only right once the old page has left the DOM (a cached home page is
    // re-inserted beside it for a moment, a lazily loaded post page arrives a little later)
    for (let i = 0; i < 40; i++) {
      await nextTick()
      if (document.querySelectorAll('[data-page]').length === 1 && document.querySelector(`[data-page="${String(to.name)}"]`)) break
      await new Promise((r) => setTimeout(r, 16))
    }
    const el = id && document.getElementById(id)
    lenis.value?.resize()
    scrollNow(el || (saved.get(to.fullPath) ?? 0))
  })
}

/** nav links: scroll on the home page, cut back to it from anywhere else */
export function toSection(id: string) {
  if (router.currentRoute.value.name === 'home') return scrollToId(id)
  pendingSection = id
  router.push('/')
}

/** the logo / HOME: the top of the home page (the hero) from anywhere */
export function toHome() {
  if (router.currentRoute.value.name === 'home') {
    if (lenis.value) lenis.value.scrollTo(0, { duration: 2 })
    else window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }
  saved.set('/', 0)
  router.push('/')
}
