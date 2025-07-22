// 文件：src/webGPU/fluid/shaders/divergence.wgsl
@group(0) @binding(0) var velocity : texture_2d<f32>;
@group(0) @binding(1) var output : texture_storage_2d<rgba16float, write>;
@group(0) @binding(2) var<uniform> simParams : SimParams;

struct SimParams {
  texelSize: vec2<f32>;
  _pad: vec2<f32>;
};

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) gid : vec3<u32>) {
  let coord = vec2<i32>(gid.xy);
  let resolution = textureDimensions(velocity).xy;

  if (any(coord < vec2<i32>(1)) || any(coord >= vec2<i32>(resolution - 1))) {
    textureStore(output, coord, vec4f(0.0));
    return;
  }

  let l = textureLoad(velocity, coord - vec2<i32>(1, 0), 0).x;
  let r = textureLoad(velocity, coord + vec2<i32>(1, 0), 0).x;
  let b = textureLoad(velocity, coord - vec2<i32>(0, 1), 0).y;
  let t = textureLoad(velocity, coord + vec2<i32>(0, 1), 0).y;

  let div = 0.5 * ((r - l) / simParams.texelSize.x + (t - b) / simParams.texelSize.y);
  textureStore(output, coord, vec4f(div, 0.0, 0.0, 1.0));
}
