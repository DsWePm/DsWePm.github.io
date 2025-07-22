export interface RenderParams {
  device: GPUDevice;
  format: GPUTextureFormat;
  vertexShaderCode: string;
  fragmentShaderCode: string;
  vertexBuffers?: GPUVertexBufferLayout[];
  primitiveTopology?: GPUPrimitiveTopology;
  cullMode?: GPUCullMode;
  depthStencil?: GPUDepthStencilState;
}


export async function FluidSimulation(params:RenderParams) {
    
}