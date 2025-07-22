export async function initializeWebGPU(canvas: HTMLCanvasElement) {
  if (!canvas) {
    console.error('Canvas element is required for WebGPU initialization.');
    return false;
  }

  if (!canvas.getContext) {
    console.error('Canvas does not support getContext method.');
    return false;
  }

  if (!canvas.getContext('webgpu')) {
    console.error('WebGPU context is not available on this canvas.');
    return false;
  }

  if (!navigator.gpu) {
    console.warn('WebGPU is not supported in this browser.');
    return false;
  }

  const adapter = await navigator.gpu.requestAdapter({
    powerPreference: 'high-performance',
  });

  if (!adapter) {
    console.warn('No WebGPU adapter found.');
    return false;
  }

  const device = await adapter.requestDevice();
  if (!device) {
    console.warn('Failed to request WebGPU device.');
    return false;
  }

  const context = canvas.getContext('webgpu');
  if (!context) {
    console.warn('Failed to get WebGPU context.');
    return false;
  }


  const format = navigator.gpu.getPreferredCanvasFormat();
  if (!format) {
    console.warn('Failed to get preferred canvas format.');
    return false;
  }

  context.configure({
    device: device,
    format: format ,
    size: {
      width: canvas.clientWidth * window.devicePixelRatio,
      height: canvas.clientHeight * window.devicePixelRatio,
    },
    
  });

  return { device, context, adapter, format };
}
