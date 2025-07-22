<!-- src/components/sections/HeroSection.vue -->
<template>
  <div>
    <div class="canvas-container">
      <canvas ref="canvasRef" class="fullscreen-canvas"></canvas>
      <div v-if="!webgpuStore.isSupported" class="fallback">
        WebGPU is not supported in this browser.
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useWebGPUStore } from '@/stores/WebGPU';
import { initializeWebGPU } from '@/utils/WebGPU/initWebGPU';
import { initRenderPipeline } from '@/utils/WebGPU/initWebGPUPipline';


// Import Shaders
import vertexShader from '@/WebGPU/shaders/vertexShaders/testTriangle.wgsl?raw'
import fragmentShader from '@/WebGPU/shaders/fragmentShaders/testRed.wgsl?raw'


const canvasRef = ref<HTMLCanvasElement | null>(null);
const webgpuStore = useWebGPUStore();



onMounted(async () => {
  const canvas = canvasRef.value;
  if (!canvas) {
    console.error('Canvas element not found.');
    return;
  }

  const result = await initializeWebGPU(canvas);
  if (result === false) {
    webgpuStore.setSupport(false);

    // 备用绘制方案
    
    return;
  }

  webgpuStore.setSupport(true);

  // WebGPU 渲染逻辑
  const pipeline = await initRenderPipeline({
    device: result.device,
    format: result.format,
    vertexShaderCode: vertexShader,    
    fragmentShaderCode: fragmentShader 
  });

  
  
  

});
</script>

<style scoped>
.fullscreen-canvas {
  width: 100%;      /* 改为 100%，填满父元素宽度 */
  height: 100vh;    /* 保持高度100vh */
  display: block;
  box-sizing: border-box; /* 避免内边距导致溢出 */
}
</style>
