// 文件：src/webGPU/fluid/simulation.ts
import { createTexture } from "@/utils/WebGPU/initWebGPUPipline";
import AdvectionShader from "@/webGPU/fluid/shaders/advection.wgsl?raw";
import DivergenceShader from "@/webGPU/fluid/shaders/divergence.wgsl?raw";
import JacobiShader from "@/webGPU/fluid/shaders/jacobi.wgsl?raw";
import GradientShader from "@/webGPU/fluid/shaders/gradient.wgsl?raw";

export class FluidSimulation {
  device: GPUDevice;
  width: number;
  height: number;
  velocity: GPUTexture;
  velocityPrev: GPUTexture;
  dye: GPUTexture;
  dyePrev: GPUTexture;
  pressure: GPUTexture;
  pressurePrev: GPUTexture;
  divergence: GPUTexture;
  sampler: GPUSampler;
  simParamBuffer: GPUBuffer;
  advectionPipeline: GPUComputePipeline;
  divergencePipeline: GPUComputePipeline;
  jacobiPipeline: GPUComputePipeline;
  gradientPipeline: GPUComputePipeline;

  constructor(device: GPUDevice, width: number, height: number) {
    this.device = device;
    this.width = width;
    this.height = height;

    this.velocity = createTexture(device, width, height);
    this.velocityPrev = createTexture(device, width, height);
    this.dye = createTexture(device, width, height);
    this.dyePrev = createTexture(device, width, height);
    this.pressure = createTexture(device, width, height);
    this.pressurePrev = createTexture(device, width, height);
    this.divergence = createTexture(device, width, height);

    this.sampler = device.createSampler({ magFilter: "linear", minFilter: "linear" });
    this.simParamBuffer = device.createBuffer({ size: 32, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });

    this.advectionPipeline = this.loadComputePipeline("advection");
    this.divergencePipeline = this.loadComputePipeline("divergence");
    this.jacobiPipeline = this.loadComputePipeline("jacobi");
    this.gradientPipeline = this.loadComputePipeline("gradient");
  }

  private loadComputePipeline(name: string): GPUComputePipeline {
    const shaderCodeMap: Record<string, string> = {
      advection: AdvectionShader,
      divergence: DivergenceShader,
      jacobi: JacobiShader,
      gradient: GradientShader,
    };

    const code = shaderCodeMap[name];
    return this.device.createComputePipeline({
      layout: "auto",
      compute: {
        module: this.device.createShaderModule({ code }),
        entryPoint: "main",
      },
    });
  }

  private dispatch(pipeline: GPUComputePipeline, bindings: Iterable<GPUBindGroupEntry>) {
    const bindGroup = this.device.createBindGroup({
      layout: pipeline.getBindGroupLayout(0),
      entries: Array.from(bindings),
    });
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginComputePass();
    pass.setPipeline(pipeline);
    pass.setBindGroup(0, bindGroup);
    pass.dispatchWorkgroups(Math.ceil(this.width / 8), Math.ceil(this.height / 8));
    pass.end();
    this.device.queue.submit([encoder.finish()]);
  }

  step() {
    const texelSize = [1 / this.width, 1 / this.height];
    const dt = 0.016;
    const alpha = -1;
    const rBeta = 0.25;

    this.device.queue.writeBuffer(
      this.simParamBuffer,
      0,
      new Float32Array([...texelSize, dt, 0, alpha, rBeta])
    );

    // 1. Advect velocity
    this.dispatch(this.advectionPipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.velocity.createView() },
      { binding: 2, resource: this.velocityPrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
      { binding: 4, resource: this.sampler },
    ]);
    [this.velocity, this.velocityPrev] = [this.velocityPrev, this.velocity];

    // 2. Advect dye
    this.dispatch(this.advectionPipeline, [
      { binding: 0, resource: this.dye.createView() },
      { binding: 1, resource: this.velocity.createView() },
      { binding: 2, resource: this.dyePrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
      { binding: 4, resource: this.sampler },
    ]);
    [this.dye, this.dyePrev] = [this.dyePrev, this.dye];

    // 3. Compute divergence
    this.dispatch(this.divergencePipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.divergence.createView() },
      { binding: 2, resource: { buffer: this.simParamBuffer } },
    ]);

    // 4. Solve pressure (Jacobi iterations)
    for (let i = 0; i < 20; i++) {
      this.dispatch(this.jacobiPipeline, [
        { binding: 0, resource: this.pressure.createView() },
        { binding: 1, resource: this.divergence.createView() },
        { binding: 2, resource: this.pressurePrev.createView() },
        { binding: 3, resource: { buffer: this.simParamBuffer } },
      ]);
      [this.pressure, this.pressurePrev] = [this.pressurePrev, this.pressure];
    }

    // 5. Subtract pressure gradient
    this.dispatch(this.gradientPipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.pressure.createView() },
      { binding: 2, resource: this.velocityPrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
    ]);
    [this.velocity, this.velocityPrev] = [this.velocityPrev, this.velocity];
  }
}
