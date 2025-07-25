// 文件：src/webGPU/fluid/simulation.ts
import { createTexture } from "@/utils/WebGPU/initWebGPUPipline";
import AdvectionShader from "@/webGPU/fluid/shaders/advection.wgsl?raw";
import DivergenceShader from "@/webGPU/fluid/shaders/divergence.wgsl?raw";
import JacobiShader from "@/webGPU/fluid/shaders/jacobi.wgsl?raw";
import GradientShader from "@/webGPU/fluid/shaders/gradient.wgsl?raw";

const WORKGROUP_SIZE = 8;

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

    // buffer aligned to 32 bytes (2 vec4<f32>)
    this.simParamBuffer = device.createBuffer({
      size: 32,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });

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

  private createBindGroup(pipeline: GPUComputePipeline, bindings: Iterable<GPUBindGroupEntry>): GPUBindGroup {
    return this.device.createBindGroup({
      layout: pipeline.getBindGroupLayout(0),
      entries: Array.from(bindings),
    });
  }

  private dispatch(pipeline: GPUComputePipeline, bindings: Iterable<GPUBindGroupEntry>) {
    const bindGroup = this.createBindGroup(pipeline, bindings);
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginComputePass();
    pass.setPipeline(pipeline);
    pass.setBindGroup(0, bindGroup);
    pass.dispatchWorkgroups(
      Math.ceil(this.width / WORKGROUP_SIZE),
      Math.ceil(this.height / WORKGROUP_SIZE)
    );
    pass.end();
    this.device.queue.submit([encoder.finish()]);
  }

  private updateSimParams(dt: number = 0.016, alpha: number = -1.0, rBeta: number = 0.25) {
    const texelSize = [1 / this.width, 1 / this.height];
    const params = new Float32Array(8); // 2 vec4<f32>
    params.set([...texelSize, dt, 0], 0); // vec4(texelSize, dt, pad)
    params.set([alpha, rBeta, 0, 0], 4);  // vec4(alpha, rBeta, pad, pad)
    this.device.queue.writeBuffer(this.simParamBuffer, 0, params);
  }

  private advectVelocity() {
    this.dispatch(this.advectionPipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.velocity.createView() },
      { binding: 2, resource: this.velocityPrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
      { binding: 4, resource: this.sampler },
    ]);
    [this.velocity, this.velocityPrev] = [this.velocityPrev, this.velocity];
  }

  private advectDye() {
    this.dispatch(this.advectionPipeline, [
      { binding: 0, resource: this.dye.createView() },
      { binding: 1, resource: this.velocity.createView() },
      { binding: 2, resource: this.dyePrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
      { binding: 4, resource: this.sampler },
    ]);
    [this.dye, this.dyePrev] = [this.dyePrev, this.dye];
  }

  private computeDivergence() {
    this.dispatch(this.divergencePipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.divergence.createView() },
      { binding: 2, resource: { buffer: this.simParamBuffer } },
    ]);
  }

  private solvePressure(iterations: number = 20) {
    for (let i = 0; i < iterations; i++) {
      this.dispatch(this.jacobiPipeline, [
        { binding: 0, resource: this.pressure.createView() },
        { binding: 1, resource: this.divergence.createView() },
        { binding: 2, resource: this.pressurePrev.createView() },
        { binding: 3, resource: { buffer: this.simParamBuffer } },
      ]);
      [this.pressure, this.pressurePrev] = [this.pressurePrev, this.pressure];
    }
  }

  private subtractPressureGradient() {
    this.dispatch(this.gradientPipeline, [
      { binding: 0, resource: this.velocity.createView() },
      { binding: 1, resource: this.pressure.createView() },
      { binding: 2, resource: this.velocityPrev.createView() },
      { binding: 3, resource: { buffer: this.simParamBuffer } },
    ]);
    [this.velocity, this.velocityPrev] = [this.velocityPrev, this.velocity];
  }

  step() {
    this.updateSimParams();

    this.advectVelocity();
    this.advectDye();
    this.computeDivergence();
    this.solvePressure();
    this.subtractPressureGradient();
  }
}
