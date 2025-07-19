// src/utils/webgpu_Initialization.ts
export async function initializeWebGPU(canvas: HTMLCanvasElement) {
  if (!navigator.gpu) {
    console.error('WebGPU is not supported in this browser.');
    return null;
  }

  const adapter = await navigator.gpu.requestAdapter();
  if (!adapter) {
    console.error('Failed to get GPU adapter.');
    return null;
  }

  const device = await adapter.requestDevice();

  const context = canvas.getContext('webgpu');
  if (!context) {
    console.error('Failed to get WebGPU context.');
    return null;
  }

  context.configure({
    device,
    format: navigator.gpu.getPreferredCanvasFormat(),
  });

  // 返回设备和上下文，方便后续使用
  return { device, context };
}
