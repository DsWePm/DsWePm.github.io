<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'

// A nav dropdown: hovering the label drops a sheet of groups (categories,
// years) with their counts; picking one jumps to it on the home page.
export interface MenuGroup { key: string; label: string; count: number; go: () => void }

defineProps<{ label: string; groups: MenuGroup[]; go: () => void }>()

const open = ref(false)
let timer = 0
const pad = (n: number) => String(n).padStart(2, '0')

function enter() { clearTimeout(timer); open.value = true }
function leave() { clearTimeout(timer); timer = window.setTimeout(() => { open.value = false }, 160) }
function pick(f?: () => void) { open.value = false; f?.() }
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <li class="menu" :class="{ open }" @pointerenter="enter" @pointerleave="leave" @focusin="enter" @focusout="leave" @keydown.esc="pick()">
    <a href="#" class="trigger" :aria-expanded="open" aria-haspopup="true" v-magnetic="0.2" @click.prevent="pick(go)">
      <span aria-hidden="true">[</span>{{ label }}<i class="caret" aria-hidden="true">▾</i><span aria-hidden="true">]</span>
    </a>
    <div class="sheets" role="menu">
      <div class="sheet">
        <p class="sh mono">┌─ {{ label.toUpperCase() }}</p>
        <button v-for="(g, gi) in groups" :key="g.key" type="button" role="menuitem" class="grp"
                :style="{ transitionDelay: open ? `${40 + gi * 35}ms` : '0ms' }" @click="pick(g.go)">
          <span class="gl">{{ g.label }}</span>
          <span class="dots" aria-hidden="true" />
          <span class="gc">{{ pad(g.count) }}</span>
        </button>
      </div>
    </div>
  </li>
</template>

<style scoped>
.menu { position: relative; }
.trigger > span { opacity: 0; transition: opacity 0.2s; margin: 0 2px; }
.trigger:hover > span, .menu.open .trigger > span { opacity: 0.7; }
.trigger .caret { font-style: normal; display: inline-block; margin-left: 5px; font-size: 9px; opacity: 0.6; transition: transform 0.35s var(--ease-out); }
.menu.open .trigger .caret { transform: rotate(180deg); }

.sheets { position: absolute; top: 100%; left: -16px; padding-top: 14px; pointer-events: none; }
.menu.open .sheets { pointer-events: auto; }
.sheet {
  width: 236px; padding: 10px 0 12px; background: rgba(227, 230, 231, 0.96); backdrop-filter: blur(8px);
  border: 1px solid #bec5c8; color: #505a5f; font-size: 11px; letter-spacing: 0.12em; text-transform: none;
  box-shadow: 0 22px 48px -28px rgba(13, 16, 19, 0.55);
  clip-path: inset(0 0 100% 0); transition: clip-path 0.45s var(--ease-out);
}
.menu.open .sheet { clip-path: inset(0 0 0 0); }
.sh { margin: 0 0 6px; padding: 0 14px; font-size: 10px; letter-spacing: 0.2em; color: #91a4a8; }
button { display: flex; align-items: baseline; gap: 8px; width: 100%; padding: 7px 14px; text-align: left; cursor: pointer; font: inherit; letter-spacing: inherit; color: inherit; transition: color 0.2s, background 0.2s; }
.grp { opacity: 0; transform: translateY(-4px); transition: opacity 0.3s, transform 0.4s var(--ease-out), color 0.2s, background 0.2s; }
.menu.open .grp { opacity: 1; transform: none; }
.grp:hover { color: #2a3236; background: rgba(77, 106, 112, 0.09); }
.gl { text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dots { flex: 1; border-bottom: 1px dotted #bec5c8; transform: translateY(-3px); }
.gc { color: #7b858a; }
.grp:hover .gc { color: #4d6a70; }
</style>
