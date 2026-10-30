<script setup lang="ts">
import HudCursor from './components/HudCursor.vue'
import ScrollHud from './components/ScrollHud.vue'
import AsciiCut from './components/AsciiCut.vue'
import SiteNav from './components/SiteNav.vue'
import { useLenis } from './composables/useLenis'

useLenis()
</script>

<template>
  <HudCursor />
  <ScrollHud />
  <AsciiCut />
  <div class="grain" aria-hidden="true" />
  <SiteNav />
  <!-- home stays alive so the hero and its loaded frames survive a trip to a post -->
  <RouterView v-slot="{ Component, route }">
    <KeepAlive include="HomeView"><component :is="Component" :key="route.name === 'home' ? 'home' : route.fullPath" /></KeepAlive>
  </RouterView>
</template>
