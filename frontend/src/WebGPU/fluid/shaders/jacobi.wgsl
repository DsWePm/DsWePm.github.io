// 文件：src/webGPU/fluid/shaders/jacobi.wgsl
@group(0) @binding(0) var pressure : texture_2d<f32>;
@group(0) @binding(1) var divergence : texture_2d<f32>;
@group(0) @binding(2) var output : texture_storage_2d<rgba16float, write>;
@group(0) @binding(3) var<uniform> simParams : SimParams;

struct SimParams {
  texelSize : vec2<f32>;
  alpha : f32;
  rBeta : f32;
};

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) gid : vec3<u32>) {
  let coord = vec2<i32>(gid.xy);
  let resolution = textureDimensions(pressure).xy;

  if (any(coord < vec2<i32>(1)) || any(coord >= vec2<i32>(resolution - 1))) {
    textureStore(output, coord, vec4f(0.0));
    return;
  }

  let l = textureLoad(pressure, coord - vec2<i32>(1, 0), 0).x;
  let r = textureLoad(pressure, coord + vec2<i32>(1, 0), 0).x;
  let b = textureLoad(pressure, coord - vec2<i32>(0, 1), 0).x;
  let t = textureLoad(pressure, coord + vec2<i32>(0, 1), 0).x;
  let div = textureLoad(divergence, coord, 0).x;

  let p = (l + r + b + t + simParams.alpha * div) * simParams.rBeta;
  textureStore(output, coord, vec4f(p, 0.0, 0.0, 1.0));
}
