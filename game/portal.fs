#version 130

uniform sampler2D main_texture;
uniform sampler2D world_texture_0;
uniform sampler2D world_texture_1;
uniform sampler2D world_texture_2;
uniform sampler2D world_texture_3;
uniform sampler2D world_texture_4;
uniform int active_world;
uniform int num_worlds;
uniform bool do_compositing;

in vec2 texcoord;

out vec3 frag_color;

vec3 get_world_texture(int idx, vec2 tc) {
    switch (idx) {
        case 0: return texture(world_texture_0, tc).rgb;
        case 1: return texture(world_texture_1, tc).rgb;
        case 2: return texture(world_texture_2, tc).rgb;
        case 3: return texture(world_texture_3, tc).rgb;
        case 4: return texture(world_texture_4, tc).rgb;
    }
}


void main() {
    int i;
    float fac = 1.0 / 6.0;
  
    if (do_compositing) {
        frag_color = texture(main_texture, texcoord).rgb * fac;

        for (i = 0; i < num_worlds; i++) {
            frag_color += get_world_texture(i, texcoord) * fac;
        }
    }
    else {
        frag_color = get_world_texture(active_world, texcoord).rgb;
    }
}
