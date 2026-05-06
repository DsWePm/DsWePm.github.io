<template>
  <div id="app">
    <Preloader />
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import Preloader from '@/components/layout/Preloader.vue'
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  font-family: 'Montserrat', sans-serif;
  position: relative;
  background-color: #fff;
}
</style>
