// vertex.wgsl

@vertex
fn main(@builtin(vertex_index) vertexIndex: u32) -> @builtin(position) vec4<f32> {
    var positions = array<vec2<f32>, 3>(
        vec2<f32>( 0.0,  0.5),   // 顶点 0
        vec2<f32>(-0.5, -0.5),   // 顶点 1
        vec2<f32>( 0.5, -0.5)    // 顶点 2
    );

    let pos = positions[vertexIndex];
    return vec4<f32>(pos, 0.0, 1.0);
}
