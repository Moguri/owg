import panda3d.core as p3d
from data import *
from util import *

VERT_SRC = \
"""
#version 140
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

out vec3 var_barycentric;

uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;

    var_barycentric = p3d_Normal;
}
"""

FRAG_SRC = \
"""
in vec3 var_barycentric;

uniform vec3 color;

float edgeFactor(){
    vec2 d = fwidth(var_barycentric.xz);
    vec2 a2 = smoothstep(vec2(0.0), d*1.5, var_barycentric.xz);
    return min(a2.x, a2.y);
}

void main()
{
    gl_FragColor.rgb = mix(vec3(0.0), color, edgeFactor());
    gl_FragColor.a = 0.75;
}
"""


class CityMap(object):
    def __init__(self, city):
        self.city = city

        # self.alpha = 0.6
        self.base_np = p3d.NodePath("CityMap-Placeholder")
        self.base_np.set_hpr(p3d.VBase3(0, 90.0, 0))
        self.base_np.set_scale(0.9)
        self.base_np.set_transparency(1)

        shader = p3d.Shader.make(p3d.Shader.SL_GLSL, VERT_SRC, FRAG_SRC)
        self.base_np.set_shader(shader)

    def show(self):
        mat = p3d.Material()

        for building in self.city.buildings:
            x1 = 2.0 * -building.collision[0] / self.city.width
            x2 = 2.0 * building.collision[0] / self.city.width
            y1 = 2.0 * -building.collision[1] / self.city.height
            y2 = 2.0 * building.collision[1] / self.city.height

            verts = []
            verts.append(Vertex((x1, y1, 0), (1.0, 0.0, 0.0)))
            verts.append(Vertex((x2, y1, 0), (0.0, 1.0, 0.0)))
            verts.append(Vertex((x2, y2, 0), (0.0, 0.0, 1.0)))
            verts.append(Vertex((x1, y2, 0), (0.0, 1.0, 0.0)))

            mesh = Mesh(verts, ((0, 1, 2), (2, 3, 0)))
            pos = building.position
            pos = (pos[0] / self.city.width * 2.0, pos[1] / self.city.height * 2.0, 0.0)

            node = mesh_to_p3d_node(mesh, "border", mat)
            np = self.base_np.attach_new_node(node)
            c = [c/255.0 for c in RESOURCES[building.resource].color]
            np.set_shader_input("color", p3d.VBase3F(*c))
            np.set_pos(pos)

        self.base_np.reparent_to(base.aspect2d)

    def hide(self):
        for child in self.base_np.get_children():
            child.remove_node()
        self.base_np.detach_node()