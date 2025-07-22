// 文件：src/webGPU/fluid/shaders/advection.wgsl
@group(0) @binding(0) var inputTex : texture_2d<f32>;       // 需要传输的源纹理（如 velocity 或 dye）
@group(0) @binding(1) var velocityTex : texture_2d<f32>;    // 流速纹理
@group(0) @binding(2) var outputTex : texture_storage_2d<rgba16float, write>; // 输出纹理
@group(0) @binding(3) var<uniform> simParams : SimParams;

struct SimParams {
  texelSize : vec2<f32>,
  dt : f32
};

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) gid : vec3<u32>) {
  let coord = vec2<i32>(gid.xy);
  let resolution = textureDimensions(inputTex).xy;

  if (any(coord >= vec2<i32>(resolution))) {
    return;
  }

  // 读取当前位置的速度
  let velocity = textureLoad(velocityTex, coord, 0).xy;

  // 使用速度反向追踪位置（Semi-Lagrangian）
  let pos = (vec2<f32>(coord) - velocity * simParams.dt) * simParams.texelSize;

  // 从 input 纹理中采样对应位置的值
  let sampled = textureSampleLevel(inputTex, sampler, pos, 0.0);

  // 写入输出
  textureStore(outputTex, coord, sampled);
}
