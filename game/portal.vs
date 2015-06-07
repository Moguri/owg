#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
//uniform vec4 texpad_render_tex;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
    //texcoord = p3d_Vertex.xz; //* texpad_render_tex.xy + texpad_render_tex.xy;
}
