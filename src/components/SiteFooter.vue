<script setup lang="ts">
import { art } from '../data/asciiArt'
import { profile } from '../data/profile'
const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer mono">
    <pre aria-hidden="true">{{ art.skyline }}</pre>
    <div class="line">
      <span>© {{ year }} {{ profile.name }}</span>
      <span>built with vue 3 · three.js · blender</span>
      <span>end of file ▮</span>
    </div>
  </footer>
</template>

<style scoped>
.footer { position: relative; z-index: 1; padding: 120px var(--gutter) 32px; color: var(--fog-dim); font-size: 11px; letter-spacing: 0.14em; max-width: 1360px; margin: 0 auto; }
pre { margin: 0 0 18px; font-size: 11px; line-height: 1.1; color: var(--line); overflow: hidden; }
.line { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; border-top: 1px solid var(--line); padding-top: 18px; }
</style>
