<!-- src/components/WebGPUCanvas.vue -->
<template>
  <div>
    <h1>WebGPU Canvas Example</h1>
    <p>This is a simple WebGPU canvas setup.</p>
    <div class="canvas-container">
      <canvas ref="canvasRef" class="fullscreen-canvas"></canvas>
    </div>
  </div>
</template>


<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { initializeWebGPU } from '@/utils/webgpu/webgpu_Initialization';

const canvasRef = ref<HTMLCanvasElement | null>(null);

onMounted(async () => {
  const canvas = canvasRef.value;
  if (!canvas) {
    console.error('Canvas element not found.');
    return;
  }

  const gpuContext = await initializeWebGPU(canvas);
  if (!gpuContext) return;

  const { device, context } = gpuContext;

  // 这里可以继续写你的 WebGPU 渲染逻辑...
});
</script>

<style scoped>
.fullscreen-canvas {
  width: 100vw;
  height: 100vh;
  display: block;
}

</style>
