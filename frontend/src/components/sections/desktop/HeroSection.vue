<!-- src/components/WebGPUCanvas.vue -->
<template>
  <canvas ref="canvas" width="800" height="600"></canvas>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

const adapter = await navigator.gpu.requestAdapter();
const device = await adapter.requestDevice();
// const canvas = document.querySelector('canvas');
// const context = canvas.getContext('webgpu');

console.log('WebGPU device:', device);




</script>



<style scoped>
</style>
