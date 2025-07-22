// 文件：src/webGPU/fluid/shaders/render.wgsl
@group(0) @binding(0) var dye : texture_2d<f32>;
@group(0) @binding(1) var sampler0 : sampler;

@fragment
fn main(@builtin(position) pos: vec4<f32>) -> @location(0) vec4<f32> {
  let resolution = vec2<f32>(textureDimensions(dye));
  let uv = pos.xy / resolution;
  return textureSampleLevel(dye, sampler0, uv, 0.0);
}
