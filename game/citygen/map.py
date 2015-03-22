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

        self.base_np = p3d.NodePath("CityMap-Placeholder")
        self.base_np.set_hpr(p3d.VBase3(0, 90.0, 0))
        self.base_np.set_scale(0.9)
        self.base_np.set_transparency(1)

        shader = p3d.Shader.make(p3d.Shader.SL_GLSL, VERT_SRC, FRAG_SRC)
        self.pairs = []
        self.active = False

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
            np.set_shader(shader)
            np.set_pos(pos)

            self.pairs.append((building, np))

        # Player Marker
        verts = []
        verts.append(Vertex((-0.015, -0.025, 0)))
        verts.append(Vertex((0.015, -0.025, 0)))
        verts.append(Vertex((0, 0.025, 0)))
        mesh = Mesh(verts, ((0, 1, 2),))
        node = mesh_to_p3d_node(mesh, "player_marker", mat)
        self.player_marker = self.base_np.attach_new_node(node)

    def show(self):
        def map_task(task):
            if not self.active:
                return task.done
            for pair in self.pairs:
                building = pair[0]
                np = pair[1]

                color = RESOURCES[building.resource].color
                color = [c/255.0 for c in color]
                np.set_shader_input("color", p3d.VBase3F(*color))

            pos = base.player_controller.player.get_pos()
            pos[0] /= self.city.width * 0.5
            pos[1] /= self.city.height * 0.5
            pos[2] = 0
            self.player_marker.set_hpr(base.player_controller.player.get_hpr())
            self.player_marker.set_pos(pos)

            return task.cont

        self.base_np.reparent_to(base.aspect2d)
        self.active = True
        base.taskMgr.add(map_task, 'Map Update')

    def hide(self):
        self.base_np.detach_node()
        self.active = False