// ./src/utils/webgpu/initWebGPUPipeline.ts

export interface RenderPipelineParams {
  device: GPUDevice;
  format: GPUTextureFormat;
  vertexShaderCode: string;
  fragmentShaderCode: string;
  vertexBuffers?: GPUVertexBufferLayout[];
  primitiveTopology?: GPUPrimitiveTopology;
  cullMode?: GPUCullMode;
  depthStencil?: GPUDepthStencilState;
  layout?: GPUPipelineLayout | 'auto';
}

export interface ComputePipelineParams {
  device: GPUDevice;
  computeShaderCode: string;
  layout?: GPUPipelineLayout | 'auto';
}

export async function initRenderPipeline(params: RenderPipelineParams): Promise<GPURenderPipeline> {
  const { device, format, vertexShaderCode, fragmentShaderCode, layout } = params;

  const vertexModule = device.createShaderModule({ code: vertexShaderCode });
  const fragmentModule = device.createShaderModule({ code: fragmentShaderCode });

  const pipeline = device.createRenderPipeline({
    layout: layout ?? 'auto',
    vertex: {
      module: vertexModule,
      entryPoint: 'main',
      buffers: params.vertexBuffers ?? [],
    },
    fragment: {
      module: fragmentModule,
      entryPoint: 'main',
      targets: [{ format }],
    },
    primitive: {
      topology: params.primitiveTopology ?? 'triangle-list',
      cullMode: params.cullMode ?? 'back',
    },
    depthStencil: params.depthStencil,
  });

  return pipeline;
}

export async function initComputePipeline(params: ComputePipelineParams): Promise<GPUComputePipeline> {
  const { device, computeShaderCode, layout } = params;

  const computeModule = device.createShaderModule({ code: computeShaderCode });

  const pipeline = device.createComputePipeline({
    layout: layout ?? 'auto',
    compute: {
      module: computeModule,
      entryPoint: 'main',
    },
  });

  return pipeline;
}


export function createTexture(
  device: GPUDevice,
  width: number,
  height: number,
  format: GPUTextureFormat = 'rgba16float',
  usage: GPUTextureUsageFlags = GPUTextureUsage.TEXTURE_BINDING |
                             GPUTextureUsage.STORAGE_BINDING |
                             GPUTextureUsage.COPY_SRC |
                             GPUTextureUsage.RENDER_ATTACHMENT
): GPUTexture {
  return device.createTexture({
    size: { width, height },
    format,
    usage,
  });
}
